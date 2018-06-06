#!/usr/bin/env bash

python3 -m venv env
source env/bin/activate
pip install .
image-update -y 2 -o os-updates2.png -j os2.json ubuntu oraclelinux fedora debian centos busybox alpine
image-update -y 2 -o non-os-updates2.png -j non-os2.json redis postgres php node nginx mysql mongo jenkins
deactivate
