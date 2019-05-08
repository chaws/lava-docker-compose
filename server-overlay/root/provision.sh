#!/bin/sh

# Idempotentally provision users and devices in lava

set -ex

lava-server manage users list | grep -q ${LAVA_ADMIN_USER} || \
    lava-server manage users add --staff --superuser --email admin@example.com --passwd ${LAVA_ADMIN_PASSWORD} ${LAVA_ADMIN_USER}

lava-server manage users list | grep -q ${LAVA_SQUAD_USER} || \
    lava-server manage users add --email admin@example.com --passwd ${LAVA_SQUAD_PASSWORD} ${LAVA_SQUAD_USER}
lava-server manage users list | grep -q ${LAVA_SQUAD_USER} || \
    lava-server manage tokens add --user ${LAVA_SQUAD_USER} --description "SQUAD token" --secret ${LAVA_SQUAD_TOKEN}

lava-server manage device-types list | grep -q qemu || \
    lava-server manage device-types add qemu

lava-server manage devices list | grep -q qemu-01 || \
    lava-server manage devices add --device-type qemu --worker dispatcher qemu-01

lava-server manage device-types list | grep -q x15 || \
    lava-server manage device-types add x15

lava-server manage devices list | grep -q x15-01 || \
    lava-server manage devices add --device-type x15 --worker dispatcher x15-01

lava-server manage device-types list | grep -q bcm2837-rpi-3-b-32 || \
    lava-server manage device-types add bcm2837-rpi-3-b-32

lava-server manage devices list | grep -q rpi-chaws || \
    lava-server manage devices add --device-type bcm2837-rpi-3-b-32 --worker dispatcher rpi-chaws
