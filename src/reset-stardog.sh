#!/bin/sh

echo "Dropping database 'guidelines'"
stardog data remove --all guidelines

./create-stardog.sh


