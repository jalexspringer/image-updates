#!/usr/bin/env bash

# pip install .
image-updates -y 2 -o os-updates2.png -j os2.json ubuntu oraclelinux fedora debian centos busybox alpine
image-updates -y 2 -o non-os-updates2.png -j non-os2.json redis postgres php node nginx mysql mongo jenkins
# deactivate
