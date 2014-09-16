from flask import render_template, g, request, jsonify, make_response
from SPARQLWrapper import SPARQLWrapper
import requests
import json
from app import app

ENDPOINT_URL = 'http://localhost:5820/guidelines/query'
UPDATE_URL = 'http://localhost:5820/guidelines/update'

REASONING_TYPE = 'SL'


### This is old style, but leaving for backwards compatibility with earlier versions of Stardog
QUERY_HEADERS = {
                    'Accept': 'application/sparql-results+json',
                    'SD-Connection-String': 'reasoning={}'.format(REASONING_TYPE)
                }
                
UPDATE_HEADERS = {
    'Accept': 'application/sparql-update',
    'SD-Connection-String': 'reasoning={}'.format(REASONING_TYPE)
}
                
PREFIXES = "PREFIX gl: <http://guidelines.data2semantics.org/vocab/>\n"

@app.route("/")
def index():
    return render_template('base.html')
    
    
@app.route('/inference')
def inference():
    query = PREFIXES + """
    INSERT DATA
    { 
        _:iir   a  gl:InternalRecommendationInteraction .
        _:iir   gl:relates ?r1 .
        _:iir   gl:relates ?r2 
    } 
WHERE
 { 
     ?r1  a  gl:Recommendation .
     ?r1  a  owl:NamedIndividual .
     ?r2  a  gl:Recommendation .
     ?r2  a  owl:NamedIndividual .
     ?r1  gl:partOf  ?g .
     ?r2  gl:partOf  ?g .
     ?g  a  owl:NamedIndividual .
     ?r1  gl:recommends ?t1 .
     ?r2  gl:recommends ?t2 .
     ?t1 a owl:NamedIndividual .
     ?t2 a owl:NamedIndividual .
     
     { 
         ?t1    gl:similarTo ?t2 .
     }
     UNION
     {
         ?t1    gl:inverseTo ?t2 .
     }
     UNION
     {
         ?ca    a gl:CareAcionType .
         ?ca    gl:promotes ?t1 .
         ?ca    gl:promotes ?t2 .
     }
     FILTER (?r1 != ?r2 && ?t1 != ?t2)
   } """
    
    result = sparql_update(query)
    
    return jsonify(result)

    
@app.route('/guidelines')
def guidelines():
    query = PREFIXES + "SELECT DISTINCT ?gl WHERE {?rec gl:partOf ?gl . }";
    
    guidelines = sparql(query, strip=True)

    return render_template('guidelines_list.html',guidelines = guidelines)
    

@app.route('/recommendations', methods=['GET'])
def recommendations():
    uri = request.args.get('uri', '')
    query = PREFIXES + """
    SELECT DISTINCT ?rec ?crec ?irec WHERE 
    { 
        ?rec gl:partOf <""" + uri + """>  . 
        ?rec a owl:NamedIndividual .
        OPTIONAL {
            ?rec gl:contradictsRecommendation ?crec .
            ?crec a owl:NamedIndividual .
        }
        OPTIONAL {
            ?rec a ?irec .
            ?irec a owl:Class .
            FILTER(?irec = gl:InternallyInteractingRecommendation)
        }
    }"""
    
    recommendations = sparql(query, strip=True)
    
    print recommendations
    
    return render_template('recommendations_list.html', recommendations = recommendations)

@app.route('/transitions', methods=['GET'])
def transitions():
    uri = request.args.get('uri', '')
    pos_query = PREFIXES + """
    SELECT DISTINCT * WHERE {
        <""" + uri + """> gl:recommendsToPursue ?pos_transition .
        ?pos_transition gl:hasTransformableSituation ?transformable_situation .
      	?pos_transition gl:hasExpectedPostSituation ?post_situation .
        OPTIONAL {
            ?pos_transition gl:hasFilterCondition ?f_condition
        }
        BIND(IF (bound(?f_condition), ?f_condition, "none") as ?filter_condition)
    }
    """

    neg_query = PREFIXES + """
    SELECT DISTINCT * WHERE {
        <""" + uri + """> gl:recommendsToAvoid ?neg_transition .
        ?neg_transition gl:hasTransformableSituation ?transformable_situation .
      	?neg_transition gl:hasExpectedPostSituation ?post_situation .
        OPTIONAL {
            ?neg_transition gl:hasFilterCondition ?f_condition .
        }
        BIND(IF (bound(?f_condition), ?f_condition, "none") as ?filter_condition)
    }
    """

    pos_transitions = sparql(pos_query, strip=True)
    neg_transitions = sparql(neg_query, strip=True)
    
    return render_template('transitions_list.html', pos_transitions = pos_transitions, neg_transitions = neg_transitions)

@app.route('/care_actions', methods=['GET'])
def care_actions():
    uri = request.args.get('uri','')
    query = PREFIXES + """
        SELECT DISTINCT * WHERE {
            <"""+uri+"""> gl:promotedBy ?ca .
            ?ca a owl:NamedIndividual .
        }
    """
    care_actions = sparql(query, strip=True)
    
    return render_template('care_actions.html', care_actions = care_actions)
    

def sparql_update(query, endpoint_url = UPDATE_URL):
    result = requests.get(endpoint_url,params={'query': query, 'reasoning': REASONING_TYPE}, headers=QUERY_HEADERS)
    
    print result.headers
    print result.status_code
    print result.content
    
    # result_dict = json.loads(result.content)
    

    return result.content

def sparql(query, strip=False, endpoint_url = ENDPOINT_URL, strip_prefix = 'http://guidelines.data2semantics.org/vocab/'):
    """This method replaces the SPARQLWrapper sparql interface, since SPARQLWrapper cannot handle the Stardog-style query headers needed for inferencing"""
    print query
    
    result = requests.get(endpoint_url,params={'query': query, 'reasoning': REASONING_TYPE}, headers=QUERY_HEADERS)
    result_dict = json.loads(result.content)
    print result_dict
    
    if strip:
        new_results = []
        for r in result_dict['results']['bindings']:
            new_result = {}
            for k, v in r.items():
                print k, v
                if v['type'] == 'uri' :
                    new_result[k+'_label'] = {}
                    new_result[k+'_label']['type'] = 'literal'
                    new_result[k+'_label']['value'] = v['value'].replace(strip_prefix,'')
                else :
                    new_result[k+'_label'] = {}
                    new_result[k+'_label']['type'] = 'literal'
                    new_result[k+'_label']['value'] = v['value']
                    
                new_result[k] = v
                    
            new_results.append(new_result)
                   
        print new_results
        return new_results
    else :
        return result_dict['results']['bindings']
    
    