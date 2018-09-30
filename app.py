import logging
import os
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
    containers = set(client.containers.list(all=True))
    running_containers = {container for container in containers if container.attrs["State"]["Running"]}
    context = {
        "containers": containers,
        "running_containers": running_containers,
        "stopped_containers": containers - running_containers
    }
    return render_template("index.html", **context)


@app.route('/container/<container_id>/')
def container_details(container_id):
    try:
        container = client.containers.get(container_id)
        return render_template("container.html", container=container)
    except docker.errors.NotFound:
        return render_template("404.html")


@app.route('/container/<container_id>/download-logs/', methods=['POST'])
def download_logs(container_id):
    try:
        container = client.containers.get(container_id)
        log_path = f"work/logs/{container.name}.log"
        # TODO Validate datetime range
        with_timestamps: bool = request.form.get("timestamps", False)
        custom_timerange: bool = request.form.get("timerange", False)

        date_start_str: str = request.form.get("date-start")
        time_start_str: str = request.form.get("time-start", "12:00 AM")
        date_end_str: str = request.form.get("date-end")
        time_end_str: str = request.form.get("time-end", "12:00 AM")

        if custom_timerange and date_start_str is not None and date_start_str != "":
            if time_start_str == "":
                time_start_str = "12:00 AM"
            datetime_start = datetime.strptime(f"{date_start_str} {time_start_str}", "%b %d, %Y %I:%M %p")
        else:
            datetime_start = None

        if custom_timerange and date_end_str is not None and date_end_str != "":
            if time_end_str == "":
                time_end_str = "12:00 AM"
            datetime_end = datetime.strptime(f"{date_end_str} {time_end_str}", "%b %d, %Y %I:%M %p")
        else:
            datetime_end = None

        log_lines = container.logs(
            timestamps=with_timestamps,
            since=datetime_start,
            until=datetime_end
        ).decode("utf-8")

        open(log_path, "w+").write(log_lines)

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
    app.run(debug=True)
