#!/usr/bin/env bash

mkdir test-outputs

# Download updates test
image-updates -o test-outputs/centos -j test-outputs/centos.json centos

# Download updates test - verbose
image-updates -v -o test-outputs/centos-verbose.png -j test-outputs/centos.json centos

# Download updates test - 2 year 
image-updates -y 2 -o test-outputs/centos-2year.jpg -j test-outputs/centos2year.json centos

# Download updates test - tag input formats
image-updates -o test-outputs/multi -j test-outputs/multi.json centos ubuntu:precise anchore/anchore-engine library/redis:latest

# Load from file test
# cp command only when no connection and above don't run
#cp ../example-outputs/non-os2.json test-outputs/multi.json
image-updates -l test-outputs/multi.json -o test-outputs/loaded 

# Load from file test - quiet
image-updates -l test-outputs/multi.json -o test-outputs/loaded-q -q

cd test-outputs
for file in centos.png centos-verbose.png centos-2year.jpg multi.png loaded.png loaded-q.png multi.json
do
if [ -f "$file" ]
then
	echo "$file found. Passed"
else
	echo "$file not found. Failed."
fi
done

cd ..
rm -r test-outputs
