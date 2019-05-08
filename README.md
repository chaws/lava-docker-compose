# Using LAVA & SQUAD with Docker Compose

This repository attempts to provide a reference implementation of deploying
LAVA using its [officially distributed docker
containers](https://master.lavasoftware.org/static/docs/v2/docker-admin.html#official-lava-software-docker-images)
and SQUAD using its containers.

## Requirements

Install the following.
- [Docker](https://docs.docker.com/install/)
- [docker-compose](https://docs.docker.com/compose/install/)


Make sure some ports are available before firing up the containers: 69, 80, 3128, 8000, and 8080

    $ docker-compose up

This will bring up all live logs from all services in this docker-compose structure.

## What you'll see

Access [localhost:8080](http://localhost:8080) for LAVA and [localhost:8000](http://localhost:8000) for SQUAD, a project dashboard for keep track of what's being run and what's been built.

## Configuration

No configuration should be necessary when running a simple qemu worker.

Note: current master branch contains configuration specific to author's
personal LAB. This is limited to:
 - ser2net configuration file
 - devices connected to ser2net container

## Usage

`make`: Deploy following containers:
 - pgsql
 - rabbitmq
 - ser2net
 - lava server
 - lava dispatcher
 - lava dispatcher http server
 - lava dispatcher tftp server
 - squad frontend
 - squad worker
 - squad listener

A user (username admin, password admin) for lava server
will automatically be deployed, as well as a qemu device-type and a qemu-01
device. Its health check should run automatically.

SQUAD user 'admin' will be created but it's assigned no password. This is
due to missing feature in SQUAD. There will be group 'example' and project
'example' created. LAVA CI backend configured to work with lava server container
will also be created. All tokens are exchanged automatically during setup.

`make clean`: Permanently delete the containers and volumes.

Once up, go to your http://localhost:8080 and log in with admin:admin. You
should see qemu-01's health-check running and it should finish successfully.
SQUAD frontend operate on port 8000 (http://localhost:8000). Port changes are
required as lava dispatched http server occupies port 80.

## Upgrades

1. Stop containers.
2. Back up pgsql from its docker volume

    sudo tar cvzf lava-server-pgdata-$(date +%Y%m%d).tgz /var/lib/docker/volumes/lava-server-pgdata

3. Back up SQUAD home

    sudo tar cvzf squad-home-$(date +%Y%m%d).tgz /var/lib/docker/volumes/squad-home

4. Change e.g. `lavasoftware/amd64-lava-server:2018.11` to
`lavasoftware/amd64-lava-server:2019.01` and
`lavasoftware/amd64-lava-dispatcher:2018.11` to
`lavasoftware/amd64-lava-dispatcher:2019.01` in docker-compose.yml.
5. Change the FROM line if any containers are being rebuilt, such as
[./server-docker/Dockerfile](./server-docker/Dockerfile)
6. Start containers.

## Design

The design goal of this repository is to demonstrate how to use the official
LAVA and SQUAD docker containers in a native way. Ideally, this means without having to
rebuild or modify the containers in any way. In the events that the containers
or their entrypoints do need modifications, patches should be [pushed
upstream](https://git.lavasoftware.org/lava/pkg/docker) to provide interfaces
for the given functionality. As the official containers mature, this repository
should become more simple.

### Containers

There are 13 containers defined in [docker-compose.yml](docker-compose.yml):

#### database

This is an official postgres container, and runs using a docker volume. Using
an official postgres container is a lot easier than using the postgres that
comes with the lava-server container. This set-up makes data persistant by
default, and makes backups easy (if desired).

Note that
[./server-overlay/etc/lava-server/instance.conf](./server-overlay/etc/lava-server/instance.conf)
provides connection details to this database for lava-server.

#### squid

This is a squid container that serves as an http proxy to the LAVA dispatcher.
Its purpose is to cache downloads to a docker volume, to improve performance
and prevent duplicate downloads. This is enabled in
[./server-overlay/etc/lava-server/env.yaml](./server-overlay/etc/lava-server/env.yaml)

#### server

This is lava-server (lava master). In order to provision a qemu device
automatically, a script at
[./server-overlay/root/provision.sh](./server-overlay/root/provision.sh) is run
at boot time to add a superuser (admin/admin) and a qemu device and qemu
worker. The lava-server container's
[entrypoint.sh](server-docker/entrypoint.sh) needed to be modified to support
this functionality - a feature that could be added upstream (see discussion at
[pkg/docker
MR#10](https://git.lavasoftware.org/lava/pkg/docker/merge_requests/10) for
details).

Several other files are mounted into the container.
[settings.conf](server-overlay/etc/lava-server/settings.conf) is provided, as
well as device and health-check directories.

#### dispatcher

The lava dispatcher is run using the official container directly. However, to
use an actual board container modifications would have to be made in a similar
way as they were made to lava-server. Example modifications were done in master
branch

#### worker-webserver

This is official [httpd container](https://hub.docker.com/_/httpd) with modified
webserver confing. It's used to provide LAVA features like transfer_overlaiy. Container
can be shared between multiple dispatchers.

#### worker-tftpd

This container launches tftpd-hpa server to provide dispatcher with ability to run
TFTP boot type jobs. Container can be shared between multiple dispatchers.

#### ser2net

This container runs ser2net providing serial connectivity for dispatcher. Container
can be shared between multiple dispatchers

#### squad-rabbitmg

Official rabbitmq container providing messaging queue for SQUAD

#### squad-dbmigrate

This container uses SQUAD image to do initial setup:
 - create/migrate database structure for SQUAD
 - create SQUAD users
 - create example group and project
 - configure LAVA CI backend that connects to previously configured LAVA master

This container doesn't restart once it's job is complete

#### squad-web

SQUAD frontend. Provides web UI for SQUAD

#### squad-worker

This container runs SQUAD Celery worker. All SQUAD background tasks are executed here

#### squad-listener

This container runs SQUAD's "listen" command. It connects to all CI backends that
provide notification service. In this case it connects to LAVA master ZMQ publisher.

#### squad-scheduler

Scheduler triggers periodic background tasks defined in SQUAD's settings.

### Boards added to this set up

This repository is a fork from Milosz, which is a fork from Dan. In this fork I
wrote a simple arduino program that controls a 8-channel relay via [power_control.py](./dispatcher-docker/power_control.py)
which is configured in the device [rpi-chaws](./server-overlay/etc/lava-server/dispatcher-config/devices/rpi-chaws.jinja2).

Make sure that the [dispatcher_ip](./server-overlay/etc/lava-server/dispatcher.d/dispatcher.yaml) is set to whatever IP address your machine has.
