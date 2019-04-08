# Flying Whales

## Yet another Docker GUI

A simple Docker Web GUI to download service logs, kill and restart Docker Swarm services.
Made with Python 3.6, [Flask](http://flask.pocoo.org/), [Docker-Py](https://docker-py.readthedocs.io) and
 [Materialize](http://materializecss.com). Requires Docker and Docker Compose.

## Features

- List all running Docker Services.
- Download the service logs starting from a certain date.
- Displays a short snippet (50 lines) of the logs in the browser, without the need of downloading the full log file.
- Kill and restart containers (only allowed users).
- LDAP for authentication by default (see FAQs)

## Install

1. Clone this repo where your Docker host is.
2. Copy/Rename `config.example.ini` to `config.ini` and add the values to all variables.
3. Copy/Rename `auth_users.example.py` to `auth_users.py` and add the list of usernames with permissions to restart and kill services.
4. Run `docker-compose up`

### Optional

Check `docker-compose.yml` for some optional extra configuration:

- Replace `8080` for the port where you want to publish the webapp.
- Replace `./logs` (on the left) with the folder where the logfiles will be written and pre processed before serving them. This could be replaced with `/tmp` or any temporal folder.
- If your `docker.sock` isn't on the default location, replace `/var/run/docker.sock` with the actual location.

## Screenshots

![list](https://i.imgur.com/G1Kzgnb.png)
![details](https://i.imgur.com/zdtDUf0.png)

## FAQs

### Why the name?

Based on a [song](https://open.spotify.com/track/5OjCsHeByDYEGxMrb1z8KQ) by Gojira with the same name. Docker's logo is a whale, services are on the cloud... flying... It made sense when I came up with it.

### Why LDAP?

I wrote this while working on a company that used LDAP for authentication, but it could be easily swapped out with something else.

### Can I use it with regular Containers?

Sure, but it requires some minor Docker-Py call changes. Open an issue if needed.
