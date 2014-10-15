#!/bin/sh

echo "Dropping database 'guidelins'"
stardog data remove --all guidelines

./create-stardog.sh


