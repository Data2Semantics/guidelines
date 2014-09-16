#!/bin/sh

stardog query "guidelines;reasoning=SL" "SELECT * {<http://guidelines.data2semantics.org/vocab/RecOA-HT-DM-Painkiller> ?p ?o . ?p a owl:ObjectProperty . ?o a owl:NamedIndividual . <http://guidelines.data2semantics.org/vocab/RecOA-HT-DM-Painkiller> a owl:NamedIndividual .}"