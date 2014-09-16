#!/bin/sh

echo "Removing data from stardog"
stardog data remove --all guidelines

echo "Loading TMR and TMR4I into stardog"
stardog data add --named-graph http://guidelines.data2semantics.org/vocab guidelines data/TMR.owl
stardog data add --named-graph http://guidelines.data2semantics.org/vocab guidelines data/TMR4I.owl

echo "Setting http://guidelines.data2semantics.org/vocab as TBox graph"
stardog-admin db offline guidelines
stardog-admin metadata set -o reasoning.schema.graphs=http://guidelines.data2semantics.org/vocab reasoning.punning.enabled=true guidelines
stardog-admin db online guidelines