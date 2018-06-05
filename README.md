# Docker Image Update Frequency
Command line tool to create visualizations and record update histories for docker hub images. Uses anchore navigator for update data. 

See results.png for example output.
![chart of updates example](https://github.com/jalexspringer/image-updates/raw/master/results.png)

## Installation
git clone https://github.com/jalexspringer/image-updates.git
cd image-updates
pip install --user .

## Usage
image-update --help
image-update -y 1 -o plot.png ubuntu centos:7 anchore/anchore-engine library/python:alpine

## TODOS
- Adjust figure height of output, make output prettier.
- Make 'human readable' more... readable. Or get rid of it.
- Store output somewhere (JSON?) for later use and further analytics?

