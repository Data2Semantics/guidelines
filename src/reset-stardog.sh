#!/bin/sh

echo "Removing data from stardog"
stardog data remove --all guidelines

echo "Loading TMR and TMR4I into stardog"
# stardog data add --named-graph http://guidelines.data2semantics.org/vocab guidelines data/TMR.owl
stardog data add guidelines data/TMR4I.ttl data/TMR4I-rules.ttl

