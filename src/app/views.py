from flask import render_template, g, request, jsonify, make_response
from SPARQLWrapper import SPARQLWrapper
import requests
import json
from app import app

ENDPOINT_URL = 'http://localhost:5820/guidelines/query'

QUERY_HEADERS = {
                    'Accept': 'application/sparql-results+json',
                    'SD-Connection-String': 'reasoning=SL'
                }
                
                
PREFIXES = "PREFIX gl: <http://guidelines.data2semantics.org/vocab/>\n"

@app.route("/")
def index():
    return render_template('base.html')
    
    
@app.route('/guidelines')
def guidelines():
    
    
    query = PREFIXES + "SELECT DISTINCT ?gl WHERE {?gl gl:composedBy ?rec }";
    
    guidelines = sparql(query, strip=True)

    return render_template('guidelines_list.html',guidelines = guidelines)
    

@app.route('/recommendations', methods=['GET'])
def recommendations():
    uri = request.args.get('uri', '')
    query = PREFIXES + 'SELECT DISTINCT ?rec ?crec WHERE {<' + uri + '> gl:composedBy ?rec . OPTIONAL {?rec gl:contradictsRecommendation ?crec}}'
    
    recommendations = sparql(query, strip=True)
    return render_template('recommendations_list.html', recommendations = recommendations)

@app.route('/transitions', methods=['GET'])
def transitions():
    uri = request.args.get('uri', '')
    query = PREFIXES + """
    SELECT DISTINCT * WHERE {
      {
        <""" + uri + """> gl:recommends ?pos_transition .
        ?pos_transition gl:hasTransformableSituation ?transformable_situation .
      	?pos_transition gl:hasExpectedPostSituation ?post_situation .
      } UNION {
        <""" + uri + """> gl:nonRecommends ?neg_transition .
        ?neg_transition gl:hasTransformableSituation ?transformable_situation .
      	?neg_transition gl:hasExpectedPostSituation ?post_situation .
      }
    }
    """
    
    transitions = sparql(query, strip=True)
    
    print transitions
    return render_template('transitions_list.html', transitions = transitions)

def sparql(query, strip=False, strip_prefix = 'http://guidelines.data2semantics.org/vocab/'):
    result = requests.get(ENDPOINT_URL,params={'query': query}, headers=QUERY_HEADERS)
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

                new_result[k] = v
                    
            new_results.append(new_result)
                   
        print new_results
        return new_results
    else :
        return result_dict['results']['bindings']
    
    