#!/bin/sh

echo "Loading drugbank data into stardog"
# stardog data add --named-graph http://www4.wiwiss.fu-berlin.de/drugbank guidelines data/drugbank_dump.nt
stardog data add guidelines data/drugbank_small.nt