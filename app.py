from datetime import datetime

import docker
from flask import Flask, render_template, send_file, request

# TODO Gunicorn
# TODO Logs

client = docker.from_env()  # TODO If fails, exit 1
app = Flask(__name__)


@app.route('/')
def index():
    containers = client.containers.list()
    return render_template("index.html", containers=containers)


@app.route('/logs/<container_id>/')
def container_details(container_id):
    try:
        container = client.containers.get(container_id)
        return render_template("container.html", container=container)
    except docker.errors.NotFound:
        return render_template("404.html")


@app.route('/logs/<container_id>/download/', methods=['POST'])
def download_logs(container_id):
    try:
        container = client.containers.get(container_id)
        log_path = f"work/logs/{container.name}.log"
        # TODO Validate datetime range
        date_start_str: str = request.form.get("date-start")
        time_start_str: str = request.form.get("time-start", "00:00 AM")
        date_end_str: str = request.form.get("date-end")
        time_end_str: str = request.form.get("time-end", "00:00 AM")

        if date_start_str is not None and date_start_str != "":
            datetime_start = datetime.strptime(f"{date_start_str} {time_start_str}", "%b %d, %Y %I:%M %p")
        else:
            datetime_start = None

        if date_end_str is not None and date_end_str != "":
            datetime_end = datetime.strptime(f"{date_end_str} {time_end_str}", "%b %d, %Y %I:%M %p")
        else:
            datetime_end = None

        with_timestamps: bool = request.form.get("timestamps", False)
        log_lines = container.logs(
            timestamps=with_timestamps,
            since=datetime_start,
            until=datetime_end
        ).decode("utf-8")

        with open(log_path, "w+") as f:
            f.write(log_lines)

        return send_file(
            log_path,
            mimetype="text/plain",
            attachment_filename=log_path.split("/")[-1],
            as_attachment=True
        )
    except docker.errors.NotFound:
        return render_template("404.html")


if __name__ == '__main__':
    app.run(debug=True)
