#!/bin/sh

echo "Dropping database 'guidelines'"
stardog-admin db drop guidelines

./create-stardog.sh


