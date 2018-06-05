# Docker Image Update Frequency
Command line tool to create visualizations and record update histories for docker hub images. Uses anchore navigator for update data. 

Example output.
![chart of updates example](https://github.com/jalexspringer/image-updates/raw/master/results.png)

```
$ image-update -y 1 -o plot.png ubuntu     

Found library/ubuntu:latest - loading update history.
library/ubuntu:latest history loaded
library/ubuntu:latest update times:
2018-06-05 16:51:39
2018-04-27 19:45:04
2018-04-13 20:15:26
2018-03-08 01:32:04
2018-01-26 13:01:43
2018-01-16 10:37:22
2018-01-07 03:32:16
2017-11-17 19:38:12
```

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

