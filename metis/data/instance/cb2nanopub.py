
# In[10]:

from rdflib import ConjunctiveGraph, Graph, Namespace, RDF, URIRef, BNode
from rdflib.plugins.memory import IOMemory

g = Graph()
g.parse('TMR-CausationBeliefs.ttl',format='turtle')

TMR = Namespace('http://guidelines.data2semantics.org/vocab/tmr/')
NP = Namespace('http://www.nanopub.org/nschema#')
PROV = Namespace('http://www.w3.org/ns/prov#')
OA = Namespace('http://www.w3.org/ns/oa#')
g.bind('tmr',TMR)



store = IOMemory()

np_g = ConjunctiveGraph(store = store)
np_g.bind('tmr',TMR)
np_g.bind('nanopub',NP)
np_g.bind('prov',PROV)
np_g.bind('oa',OA)

fakepub = URIRef('http://hdl.handle.net/10222/43703') #Jafarpour



for s, p, o in g.triples((None, RDF.type, TMR['CausationBelief'])): 
    value = g.value(s, TMR['hasValue'])
    cause = g.value(s, TMR['hasCause'])
    effect = g.value(s, TMR['hasEffect'])
    
    prov_uri = URIRef(str(s)+'_provenance')
    ass_uri = URIRef(str(s)+'_assertion')
    pi_uri = URIRef(str(s)+'_publicationinfo')
    
    prov_g = Graph(store=store, identifier=prov_uri)
    prov_g.bind('tmr',TMR)
    ass_g = Graph(store=store, identifier=ass_uri)
    ass_g.bind('tmr',TMR)
    pi_g = Graph(store=store, identifier=pi_uri)
    pi_g.bind('tmr',TMR)
    
    nanopub = URIRef(str(s)+'_nanopub')
    
    np_g.add((nanopub, RDF.type, NP['Nanopublication']))
    np_g.add((nanopub, NP['hasAssertion'], ass_uri))
    np_g.add((nanopub, NP['hasProvenance'], prov_uri))
    
    ass_g.add((cause, TMR['causes'], effect))
    ass_g.add((ass_uri, TMR['strength'], value))
    
    prov_g.add((prov_uri, RDF.type, OA['Annotation']))
    prov_g.add((prov_uri, OA['hasBody'], ass_uri))
    
    target_bnode = BNode()
    prov_g.add((prov_uri, OA['hasTarget'], target_bnode))
    prov_g.add((target_bnode, OA['hasSource'], fakepub))
    
    prov_g.add((ass_uri, RDF.type, TMR['CausationBelief']))
    
    prov_g.add((ass_uri, PROV['wasDerivedFrom'], fakepub))
    
    
    pi_g.add((nanopub, PROV['wasDerivedFrom'], fakepub))
    

with open('output.trig','w') as f:
    np_g.serialize(f, format='trig')
    
    
    
    
    
    
    


# In[ ]:



