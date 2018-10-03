import logging
import os
import time
from datetime import datetime

import docker
from flask import Flask, render_template, request, send_file
from requests.exceptions import ConnectionError

app = Flask(__name__)

if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


client = docker.from_env()
try:
    docker_info = client.info()
    app.logger.info(f"Containers: {docker_info['Containers']}")
    app.logger.info(f"Containers Running: {docker_info['ContainersRunning']}")
    app.logger.info(f"Containers Stopped: {docker_info['ContainersStopped']}")
except ConnectionError:
    app.logger.critical("Docker service not found or not running")
    exit(1)  # TODO Exit gunicorn

try:
    os.makedirs("work/logs")
except FileExistsError:
    pass


@app.route('/')
def index():
    services = client.services.list()
    return render_template("index.html", services=services)


@app.route('/service/<service_id>/')
def service_details(service_id):
    try:
        service = client.services.get(service_id)
        return render_template("service.html", service=service)
    except docker.errors.NotFound:
        return render_template("404.html")


@app.route('/service/<service_id>/download-logs/', methods=['POST'])
def download_logs(service_id):
    try:
        service = client.services.get(service_id)
        log_path = f"work/logs/{service.name}.log"
        with_timestamps: bool = request.form.get("timestamps", False)
        custom_timerange: bool = request.form.get("timerange", False)

        since_date_str: str = request.form.get("date-start")
        since_time_str: str = request.form.get("time-start", "12:00 AM")

        if custom_timerange and since_date_str is not None and since_date_str != "":
            if since_time_str == "":
                since_time_str = "12:00 AM"
            since_unix_time = time.mktime(
                datetime.strptime(f"{since_date_str} {since_time_str}", "%b %d, %Y %I:%M %p").timetuple()
            )
        else:
            since_unix_time = None

        log_lines = service.logs(
            timestamps=with_timestamps,
            since=since_unix_time,
            stdout=True,
            stderr=True
        )

        with open(log_path, "w+") as f:
            for line in log_lines:
                f.write(line.decode("utf-8"))

        filename = log_path.split("/")[-1]

        # TODO Add dates to filename

        return send_file(
            log_path,
            mimetype="text/plain",
            attachment_filename=filename,
            as_attachment=True
        )
    except docker.errors.NotFound:
        return render_template("404.html")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
