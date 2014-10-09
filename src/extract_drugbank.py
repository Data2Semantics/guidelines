from bs4 import BeautifulSoup
from rdflib import Graph, Namespace, RDF, OWL, RDFS, Literal

BASE_URI = 'http://wifo5-04.informatik.uni-mannheim.de/drugbank/resource/'



FILE = 'drugbank.xml'

db = BeautifulSoup(open(FILE,'r'))

drugs = db.find_all('drug')


DB = Namespace(BASE_URI+'drugbank/')
DRUG = Namespace(BASE_URI+'drugs/')
CATEGORY = Namespace(BASE_URI+'drug_categories/')

g = Graph()
g.bind('drugbank',DB)
g.bind('drug',DRUG)
g.bind('category',CATEGORY)
for drug in drugs:
    db_ids = drug.find_all('drugbank-id')
    ids = []
    for db_id in db_ids:
        ids.append(db_id.text)
    
    n = drug.find('name')
    if n :
        name = n.text
    else :
        name = None
        
    d = drug.find('description')
    if d:
        description = d.text
    else :
        description = None
    
    db_categories = drug.find('categories')
    categories = []
    
    if db_categories :    
        for db_category in db_categories.find_all('category') :
            db_c = db_category.find('category')
        
            if db_c :
                categories.append(db_c.text)
        
    db_interactions = drug.find('drug-interactions')
    interactions = []
    
    if db_interactions:
        for db_interaction in db_interactions.find_all('drug-interaction') :
            interactions.append(db_interaction.find('drugbank-id').text)
        
    print ids, name, description, categories, interactions
    
    g.add((DRUG[ids[0]],RDF.type,DB['drugs']))
    for id in ids[1:]:
        g.add((DRUG[ids[0]],OWL.sameAs,DRUG[id]))
        
    if name:
        g.add((DRUG[id],RDFS.label,Literal(name)))
        
    if description :
        g.add((DRUG[id],DB['description'],Literal(description)))
        
    for c in categories :
        c_stripped = c.replace(' ','')
        g.add((CATEGORY[c_stripped],RDFS.label,Literal(c)))
        g.add((DRUG[id],DB['drugCategory'],CATEGORY[c_stripped]))
        
    for i in interactions :
        g.add((DRUG[id],DB['interactsWith'],DRUG[i]))
        g.add((DRUG[i],DB['interactsWith'],DRUG[id]))
        

outfile = open('drugbank_small.nt','w')


g.serialize(destination=outfile,format='nt')
outfile.close()
        
