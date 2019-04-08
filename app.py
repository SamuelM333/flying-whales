import logging.handlers
import re
import time
from datetime import datetime
from urllib.parse import urlparse, urljoin

import docker
from flask import (
    Flask, render_template, request,
    send_file, redirect, flash,
    url_for, jsonify, abort
)
from flask_login import LoginManager, logout_user, login_user, login_required, current_user
from requests.exceptions import ConnectionError

from config import FLASK_SECRET_KEY, HOST_NAME, LOG_DIR, LDAP_HOST, LDAP_DN, LDAP_PASSWORD, AUTH_USERS
from ldap import LDAPBind
from models import User, users

__version__ = "0.1.1"

NODE_RE = re.compile("com\.docker\.swarm\.node\.id=(\w+)")

app = Flask(__name__)
app.config['SECRET_KEY'] = FLASK_SECRET_KEY

LOGFILE = "{}/{}-FlyingWhales.log".format(LOG_DIR, HOST_NAME)
formatter = logging.Formatter('%(process)d: %(asctime)s - %(levelname)s - %(message)s')

rotating_file_handler = logging.handlers.TimedRotatingFileHandler(LOGFILE, when="W6")
rotating_file_handler.setFormatter(formatter)
rotating_file_handler.setLevel(logging.INFO)

if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    app.logger.addHandler(rotating_file_handler)

app.logger.info("WELCOME: Iniciando Flying Whales")

login_manager = LoginManager(app)
login_manager.login_view = 'login'

app.logger.info("Conectado a server LDAP {} con DN {}".format(LDAP_HOST, LDAP_DN))

docker_client = docker.from_env()
nodes = dict()

try:
    app.logger.info("Containers Running: {}".format(len(docker_client.services.list())))
except ConnectionError:
    app.logger.critical("Docker service not found or not running")
    exit(1)  # TODO Exit gunicorn or show error message.


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def add_node_hostname_to_logs(log_lines, append_html_break=False):
    lines = ""
    for line in log_lines:
        line = line.decode('utf-8')
        node_id = NODE_RE.findall(line)
        try:
            node_id = node_id[0]
            try:
                node_name = nodes[node_id]
            except KeyError:
                node_name = docker_client.nodes.get(node_id).attrs["Description"]["Hostname"]
                nodes[node_id] = node_name
        except IndexError:
            node_name = ""

        line = re.sub(r"com\.docker\.swarm\.node\.id=\w+\,", node_name, line)
        line = re.sub(r"com\.docker\.swarm\.service\.id=\w+\,", "", line)
        line = re.sub(r"com\.docker\.swarm\.task\.id=\w+", "", line)
        if append_html_break:
            lines += "{}<br>".format(line)
        else:
            lines += line
    return lines


@login_manager.user_loader
def load_user(username):
    return users.get(username)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        with LDAPBind(host=LDAP_HOST, dn=LDAP_DN, password=LDAP_PASSWORD) as (server, conn):
            user = User(server=server, conn=conn, username=username)

            if user.try_login(password):
                app.logger.info("Login successful. {}".format(user))
                login_user(user)  # TODO Add remember me
                next_url = request.args.get('next')

                if next_url is None or not is_safe_url(next_url):
                    return redirect("/")
                return redirect(next_url)
            else:
                flash('Invalid username or password. Please try again.', 'danger')
                return redirect("/")
    return render_template("login.html")


@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect("/login/")


@app.route('/')
@login_required
def index():
    services = []
    for service in docker_client.services.list():
        nodes = []
        for task in service.tasks():
            if task["DesiredState"] == "running":
                # TODO NodeID not found. Validate
                try:
                    nodes.append(docker_client.nodes.get(task["NodeID"]).attrs["Description"]["Hostname"])
                except KeyError:
                    pass
        services.append(
            {
                "service": service,
                "nodes": tuple(nodes)
            }
        )

    return render_template("index.html", services=services, current_user=current_user)


@app.route('/service/<service_id>/')
@login_required
def service_details(service_id):
    try:
        service = docker_client.services.get(service_id)
        nodes = []
        for task in service.tasks():
            if task["DesiredState"] == "running":
                nodes.append(docker_client.nodes.get(task["NodeID"]).attrs["Description"]["Hostname"])

        return render_template(
            "service.html",
            service=service,
            nodes=nodes,
            superuser=current_user.username in AUTH_USERS
        )
    except docker.errors.NotFound:
        abort(404)


@app.route('/service/<service_id>/download-logs/short/<log_lines_num>', methods=['GET'])
@login_required
def download_logs_snippet(service_id, log_lines_num):
    try:
        log_lines_num = int(log_lines_num)
    except ValueError:
        return jsonify({"error": "'log_lines_num' must be a number"}), 400

    try:
        service = docker_client.services.get(service_id)
        log_lines = service.logs(
            details=True,
            timestamps=True,
            stdout=True,
            stderr=True,
            tail=log_lines_num
        )

        lines = add_node_hostname_to_logs(sorted(log_lines), True)

        return jsonify({
            "service": service_id,
            "log_lines": lines
        })

    except docker.errors.NotFound:
        return jsonify({"error": "{} not found".format(service_id)}), 404


@app.route('/service/<service_id>/download-logs/', methods=['POST'])
@login_required
def download_logs(service_id):
    # TODO Make async
    try:
        service = docker_client.services.get(service_id)
        log_path = "/tmp/{}.log".format(service.name)
        with_timestamps = request.form.get("timestamps", False)
        custom_timerange = request.form.get("timerange", False)

        since_date_str = request.form.get("date-start")
        since_time_str = request.form.get("time-start", "12:00 AM")

        if custom_timerange and since_date_str is not None and since_date_str != "":
            if since_time_str == "":
                since_time_str = "12:00 AM"
            since_unix_time = time.mktime(
                datetime.strptime("{} {}".format(since_date_str, since_time_str), "%b %d, %Y %I:%M %p").timetuple()
            )
        else:
            since_unix_time = None

        log_lines = service.logs(
            details=True,
            timestamps=with_timestamps,
            since=since_unix_time,
            stdout=True,
            stderr=True
        )
        if with_timestamps:
            log_lines = sorted(log_lines)  # TODO For long logs, this will take a while
        lines = add_node_hostname_to_logs(log_lines)

        open(log_path, 'w').writelines(lines)

        # TODO Add dates to filename
        filename = log_path.split("/")[-1]
        app.logger.info("Logs from service {} downloaded by {}".format(service_id, current_user))

        return send_file(
            log_path,
            mimetype="text/plain",
            attachment_filename=filename,
            as_attachment=True
        )
    except docker.errors.NotFound:
        abort(404)


@app.route('/service/<service_id>/remove/')
@login_required
def remove_service(service_id):
    if current_user.username in AUTH_USERS:
        try:
            service = docker_client.services.get(service_id)
            image = service.attrs["Spec"]["TaskTemplate"]["ContainerSpec"]["Image"].split("@")[0]
            service.remove()
            app.logger.info("SERVICE STOPPED: Service {} with Image {} stopped by {}."
                            .format(service_id, image, current_user))
            return redirect("/")
        except docker.errors.NotFound:
            pass

    abort(404)


@app.route('/service/<service_id>/restart/')
@login_required
def restart_service(service_id):
    if current_user.username in AUTH_USERS:
        try:
            service = docker_client.services.get(service_id)
            image = service.attrs["Spec"]["TaskTemplate"]["ContainerSpec"]["Image"].split("@")[0]
            service.force_update()
            app.logger.info("SERVICE RESTARTED: Service {} with Image {} restarted by {}"
                            .format(service_id, image, current_user))
            return redirect("/")
        except docker.errors.NotFound:
            pass

    abort(404)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
