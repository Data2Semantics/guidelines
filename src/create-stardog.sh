#!/bin/sh

stardog-admin db create -n guidelines data/TMR4I.ttl data/TMR4I-rules.ttl data/TMR4I-drugs.ttl

echo "Setting tag:stardog:api:context:all as TBox graph"
# Other option: http://guidelines.data2semantics.org/vocab
stardog-admin db offline guidelines
stardog-admin metadata set -o reasoning.schema.graphs=tag:stardog:api:context:all guidelines
stardog-admin db online guidelines