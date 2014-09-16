#!/bin/sh

echo "Removing data from stardog"
stardog data remove --all guidelines

echo "Loading TMR and TMR4I into stardog"
stardog data add --named-graph http://www.semanticweb.org/veruskacz/ontologies/2014/8/TMR.owl guidelines data/TMR.owl
stardog data add --named-graph http://www.semanticweb.org/veruskacz/ontologies/2014/8/TMR4I.owl guidelines data/TMR4I.owl

