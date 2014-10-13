from flask import render_template, g, request, jsonify, make_response
from SPARQLWrapper import SPARQLWrapper
import requests
import json
from app import app
import uuid

ENDPOINT_URL = 'http://localhost:5820/guidelines/query'
UPDATE_URL = 'http://localhost:5820/guidelines/update'

REASONING_TYPE = 'SL'


### This is old style, but leaving for backwards compatibility with earlier versions of Stardog
QUERY_HEADERS = {
                    'Accept': 'application/sparql-results+json',
                    'SD-Connection-String': 'reasoning={}'.format(REASONING_TYPE)
                }
                
UPDATE_HEADERS = {
    'Content-Type': 'application/sparql-update',
    'SD-Connection-String': 'reasoning={}'.format(REASONING_TYPE)
}
                
PREFIXES = """
            PREFIX tmr4i: <http://guidelines.data2semantics.org/vocab/>
            PREFIX drugbank: <http://wifo5-04.informatik.uni-mannheim.de/drugbank/resource/drugbank/>
            PREFIX drug: <http://wifo5-04.informatik.uni-mannheim.de/drugbank/resource/drugs/>
            """

@app.route("/")
def index():
    return render_template('base.html')
    
    
@app.route('/getinference')
def inference():
    query = PREFIXES + """
    SELECT DISTINCT ?r1 ?r2 
    WHERE
    { 
         ?r1  a  tmr4i:Recommendation .
         ?r1  a  owl:NamedIndividual .
         ?r2  a  tmr4i:Recommendation .
         ?r2  a  owl:NamedIndividual .
         ?r1  tmr4i:partOf  ?g .
         ?r2  tmr4i:partOf  ?g .
         ?g  a  owl:NamedIndividual .
         ?r1  tmr4i:recommends ?t1 .
         ?r2  tmr4i:recommends ?t2 .
         ?t1 a owl:NamedIndividual .
         ?t2 a owl:NamedIndividual .
     
         { 
             ?t1    tmr4i:similarToTransition ?t2 .
         }
         UNION
         {
             ?t1    tmr4i:inverseToTransition ?t2 .
         }
         UNION
         {
             ?t1    tmr4i:promotedBy ?ca .
             ?t2    tmr4i:promotedBy ?ca .
         }
         FILTER (?r1 != ?r2 && ?t1 != ?t2)
         
         # Need to make sure that we are not adding duplicate interactions
         FILTER NOT EXISTS {
             ?iir   a tmr4i:InternalRecommendationInteraction .
             ?iir   tmr4i:relates ?r1 .
             ?iir   tmr4i:relates ?r2 .
         }
    } """
    results = sparql(query)
    
    deduped_results = set()
    for r in results :
        one = r['r1']['value']
        two = r['r2']['value']
        
        if not (two,one) in deduped_results:
            print "adding", (one,two)
            deduped_results.add((one,two))
        else :
            print "result already found", (two,one)        
 
    print len(deduped_results), "interactions found."
 
    update_template = PREFIXES + """
    INSERT DATA
    {{ 
        tmr4i:{0}   a  tmr4i:InternalRecommendationInteraction, owl:NamedIndividual .
        tmr4i:{0}   tmr4i:relates <{1}> .
        tmr4i:{0}   tmr4i:relates <{2}> .
        <{1}> tmr4i:interactsInternallyWith <{2}> .
        <{2}> tmr4i:interactsInternallyWith <{1}> .
    }}
    """
     
    for (one,two) in deduped_results :
        interaction = "internal_recommendation_interaction_{}".format(str(uuid.uuid4()))
        
        update = update_template.format(interaction, one, two)
        
        print interaction, one, two
        result = sparql_update(update)
    
        results = sparql(query)

    # Including Incompatible Drugs External Interactions
    query = PREFIXES + """
    
        SELECT distinct ?r1 ?r2 ?d1 ?d2
        WHERE {
        ?r1 tmr4i:recommendsToPursue ?t1 .
        ?t1 tmr4i:promotedBy ?ca1 .
        ?r2 tmr4i:recommendsToPursue ?t2 .
        ?t2 tmr4i:promotedBy ?ca2 .
        ?r1 tmr4i:partOf ?g .
        ?r2 tmr4i:partOf ?g .
    
        { ?ca1 tmr4i:involves ?d1 . } UNION { ?ca1 tmr4i:involves ?c1 . ?d1 drugbank:drugCategory ?c1 .}
        { ?ca2 tmr4i:involves ?d2 . } UNION { ?ca2 tmr4i:involves ?c2 . ?d2 drugbank:drugCategory ?c2 .}
        ?d1 drugbank:interactsWith ?d2 .
    
        FILTER(?r1 != ?r2 && ?d1 != ?d2 && ?ca1 != ?ca2 )
        
        # Need to make sure that we are not adding duplicate interactions
        FILTER NOT EXISTS {
        ?iir   a tmr4i:IncompatibleDrugExternalInteraction .
        ?iir   tmr4i:relates ?r1 .
        ?iir   tmr4i:relates ?r2 .
        }
        
        }
        """
    results = sparql(query)

    deduped_results = set()
    for r in results :
        ROne = r['r1']['value']
        RTwo = r['r2']['value']
        DOne = r['d1']['value']
        DTwo = r['d2']['value']
            
        if not (RTwo,ROne,DTwo,DOne) in deduped_results:
            print "adding", (ROne,RTwo,DOne,DTwo)
            deduped_results.add((ROne,RTwo,DOne,DTwo))
        else :
            print "result already found", (RTwo,ROne,DTwo,DOne)

    print len(deduped_results), "external interactions found."
    
    update_template = PREFIXES + """
            INSERT DATA
            {{
            tmr4i:{0}   a  tmr4i:IncompatibleDrugExternalInteraction, owl:NamedIndividual .
            tmr4i:{0}   tmr4i:relates <{1}> .
            tmr4i:{0}   tmr4i:relates <{2}> .
            tmr4i:{0}   tmr4i:relates <{3}> .
            tmr4i:{0}   tmr4i:relates <{4}> .
            <{1}> tmr4i:interactsExternallyWith <{2}> .
            <{2}> tmr4i:interactsExternallyWith <{1}> .
            }}
            """
    
    for (ROne,RTwo,DOne,DTwo) in deduped_results :
        interaction = "external_recommendation_interaction_{}".format(str(uuid.uuid4()))
        
        update = update_template.format(interaction, ROne,RTwo,DOne,DTwo)
        
        print interaction, ROne,RTwo,DOne,DTwo
        result = sparql_update(update)

    # Including Alternative Drug External Interactions
    # The rules for classifying the internal interaction should be already performed
    
    # RH: TODO: THIS NEEDS TO BE CHANGED... the 'regards' relation is not necessary, since the drugs are already related to a drug category. 
    query = PREFIXES + """
        INSERT
        {
        _:iir   a  tmr4i:AlternativeDrugExternalInteraction .
        _:iir   tmr4i:relates ?rec .
        _:iir   tmr4i:relates ?ca .
        _:iir   tmr4i:relates ?d .
        _:iir   tmr4i:relates ?dALT .
        }
        WHERE
        {
        { {?i a tmr4i:ContradictionDueToSameAction .} UNION {?i a tmr4i:ContradictionDueToInverseTransition .}
        UNION {?i a tmr4i:ContradictionDueToSimiliarTransition} .} #Given a contradictory interaction (RH: Why not just check for an instance of RecommendationInteraction?)
        ?i tmr4i:relates ?rec .
        ?rec tmr4i:recommendsToPursue ?t .
        ?rec tmr4i:partOf ?g .
        ?t tmr4i:regards ?dc .						  	#For a transition related with the effect meant by DrugCategory
        
        ?t tmr4i:promotedBy ?ca .
        ?ca tmr4i:involves ?d .
        
        ?dALT drugbank:drugCategory ?dc .				#Find alternative drugs with the same effect / Category
        
        FILTER (?d != ?dALT) .
        
        FILTER NOT EXISTS
        { ?dALT drugbank:interactsWith ?d2 .
        { ?ca2 tmr4i:involves ?d2 . }
        UNION { ?ca2 tmr4i:involves ?c2 . ?d2 drugbank:drugCategory ?c2 .} .
        ?t2 tmr4i:promotedBy ?ca2 .
        ?rec2 tmr4i:recommendsToPursue ?t2 .
        ?rec2 tmr4i:partOf ?g .
        FILTER(?dALT != ?d2)
        }
        
        # Need to make sure that we are not adding duplicate interactions
        FILTER NOT EXISTS {
        ?iir   a tmr4i:AlternativeDrugExternalInteraction .
        ?iir   tmr4i:relates ?rec .
        ?iir   tmr4i:relates ?ca .
        ?iir   tmr4i:relates ?d .
        ?iir   tmr4i:relates ?dALT .
        }
    
        }
        """
    results = sparql(query)
    print results

    return jsonify({'status': 'Done'})


@app.route('/getguidelines')
def guidelines():
    print "Retrieving guidelines"
    query = PREFIXES + "SELECT DISTINCT ?gl ?gl_label WHERE {?rec tmr4i:partOf ?gl . ?gl rdfs:label ?gl_label .}";
    
    guidelines = sparql(query, strip=True)

    return render_template('guidelines_list.html',guidelines = guidelines)
    

@app.route('/getrecommendations', methods=['GET'])
def recommendations():
    print "Retrieving recommendations"
    guideline_uri = request.args.get('uri', '')
    guideline_label = request.args.get('label','')
    
    query = PREFIXES + """
    SELECT DISTINCT ?rec ?rec_label ?crec ?irec ?erec WHERE 
    { 
        ?rec tmr4i:partOf <""" + guideline_uri + """>  . 
        ?rec rdfs:label ?rec_label .
        ?rec a owl:NamedIndividual .
        OPTIONAL {
            ?rec tmr4i:interactsInternallyWith ?crec .
            ?crec a owl:NamedIndividual .
        }
        OPTIONAL {
            ?rec a tmr4i:InternallyInteractingRecommendation .
            BIND(tmr4i:InternallyInteractingRecommendation AS ?irec)
        }
        OPTIONAL {
            ?rec a tmr4i:ExternallyInteractingRecommendation .
            BIND(tmr4i:ExternallyInteractingRecommendation AS ?erec)
        }
    }"""
    
    
    recommendations = sparql(query, strip=True)
    
    print recommendations
    
    return render_template('recommendations_list.html', recommendations = recommendations, guideline_label = guideline_label)

@app.route('/gettransitions', methods=['GET'])
def transitions():
    print "Retrieving transitions"
    uri = request.args.get('uri', '')
    pos_query = PREFIXES + """
    SELECT DISTINCT * WHERE {
        <""" + uri + """> tmr4i:recommendsToPursue ?transition .
        ?transition tmr4i:hasTransformableSituation ?transformable_situation .
        ?transformable_situation rdfs:label ?transformable_situation_label .
      	?transition tmr4i:hasExpectedPostSituation ?post_situation .
        ?post_situation rdfs:label ?post_situation_label .
        ?transition a owl:NamedIndividual .
        ?transformable_situation a owl:NamedIndividual .
        ?post_situation a owl:NamedIndividual .
        OPTIONAL {
            ?transition tmr4i:hasFilterCondition ?f_condition .
            ?f_condition a owl:NamedIndividual .
        }
        OPTIONAL {
            ?transition tmr4i:inverseToTransition ?inverse_transition .
            ?inverse_transition a owl:NamedIndividual .
            ?irec tmr4i:recommends ?inverse_transition .
        }
        OPTIONAL {
            ?transition tmr4i:similarToTransition ?similar_transition .
            ?similar_transition a owl:NamedIndividual .
            ?srec tmr4i:recommends ?similar_transition .
        }
        
        
        BIND(IF (bound(?f_condition), ?f_condition, "none") as ?filter_condition)
    }
    """

    neg_query = PREFIXES + """
    SELECT DISTINCT * WHERE {
        <""" + uri + """> tmr4i:recommendsToAvoid ?transition .
        ?transition tmr4i:hasTransformableSituation ?transformable_situation .
        ?transformable_situation rdfs:label ?transformable_situation_label .
      	?transition tmr4i:hasExpectedPostSituation ?post_situation .
        ?post_situation rdfs:label ?post_situation_label .
        ?transition a owl:NamedIndividual .
        ?transformable_situation a owl:NamedIndividual .
        ?post_situation a owl:NamedIndividual .
        OPTIONAL {
            ?transition tmr4i:hasFilterCondition ?f_condition .
            ?f_condition a owl:NamedIndividual .
        }
        OPTIONAL {
            ?transition tmr4i:inverseToTransition ?inverse_transition .
            ?inverse_transition a owl:NamedIndividual .
        }
        OPTIONAL {
            ?transition tmr4i:similarToTransition ?similar_transition .
            ?similar_transition a owl:NamedIndividual .
        }
        BIND(IF (bound(?f_condition), ?f_condition, "none") as ?filter_condition)

    }
    """

    pos_transitions = sparql(pos_query, strip=True)
    neg_transitions = sparql(neg_query, strip=True)
    
    return render_template('transitions_list.html', pos_transitions = pos_transitions, neg_transitions = neg_transitions)

@app.route('/getcare_actions', methods=['GET'])
def care_actions():
    uri = request.args.get('uri','')
    query = PREFIXES + """
        SELECT DISTINCT * WHERE {
            <"""+uri+"""> tmr4i:promotedBy ?ca .
            ?ca a owl:NamedIndividual .
        }
    """
    care_actions = sparql(query, strip=True)
    
    return render_template('care_actions.html', care_actions = care_actions)
    

def sparql_update(query, endpoint_url = UPDATE_URL):
    
    print query 
    
    result = requests.post(endpoint_url,params={'reasoning': REASONING_TYPE}, data=query, headers=UPDATE_HEADERS)
    
    return result.content

def sparql(query, strip=False, endpoint_url = ENDPOINT_URL, strip_prefix = 'http://guidelines.data2semantics.org/vocab/'):
    """This method replaces the SPARQLWrapper sparql interface, since SPARQLWrapper cannot handle the Stardog-style query headers needed for inferencing"""
    
    result = requests.get(endpoint_url,params={'query': query, 'reasoning': REASONING_TYPE}, headers=QUERY_HEADERS)
    try :
        result_dict = json.loads(result.content)
    except Exception as e:
        return result.content
    
    if strip:
        new_results = []
        for r in result_dict['results']['bindings']:
            new_result = {}
            for k, v in r.items():
                print k, v
                if v['type'] == 'uri' and not k+'_label' in r.keys():
                    new_result[k+'_label'] = {}
                    new_result[k+'_label']['type'] = 'literal'
                    new_result[k+'_label']['value'] = v['value'].replace(strip_prefix,'')
                elif not k+'_label' in r.keys():
                    new_result[k+'_label'] = {}
                    new_result[k+'_label']['type'] = 'literal'
                    new_result[k+'_label']['value'] = v['value']
                    
                new_result[k] = v
                    
            new_results.append(new_result)
                   
        print new_results
        return new_results
    else :
        return result_dict['results']['bindings']
    
    