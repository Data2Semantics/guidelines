from flask import render_template, request, jsonify
import logging
import requests
import json
from app import app
import uuid
import pprint
import os

ENDPOINT_URL = os.getenv('ENDPOINT_URL') or 'http://localhost:5820/guidelines/query'
UPDATE_URL = os.getenv('UPDATE_URL') or 'http://localhost:5820/guidelines/update'

REASONING_TYPE = 'SL'

log = app.logger
log.setLevel(logging.DEBUG)

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
    internal_recommendation_interaction()

    incompatible_drugs_external_interaction()

    # Including Alternative Drug External Interactions
    # The rules for classifying the internal interaction should be already performed



    alternative_drugs_external_interaction()


    same_as()


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
    SELECT DISTINCT ?rec ?rec_label WHERE
    {
        ?rec tmr4i:partOf <""" + guideline_uri + """>  .
        ?rec rdfs:label ?rec_label .
        ?rec a owl:NamedIndividual .
    }"""

    recommendations_menu = sparql(query, strip=True)


    ## initialize the rest of the results with the stuff for the recommendations menu
    all_results = []
    all_results.extend(recommendations_menu)

    query = PREFIXES + """
    SELECT DISTINCT * WHERE
    {
        ?rec tmr4i:partOf <""" + guideline_uri + """>  .
        ?rec rdfs:label ?rec_label .
        ?rec a owl:NamedIndividual .
        ?rec tmr4i:interactsInternallyWith ?internal_rec .
        ?internal_rec rdfs:label ?internal_rec_label .
        ?i tmr4i:relates ?rec .
        ?i tmr4i:relates ?internal_rec .
        FILTER NOT EXISTS {
           ?rec owl:sameAs ?internal_rec .
        }
        {
            ?i a tmr4i:ContradictionDueToSameAction .
            ?i tmr4i:action ?ca .
            ?ca rdfs:label ?ca_label .
            BIND(tmr4i:ContradictionDueToSameAction AS ?itype)
        } UNION {
            ?i a tmr4i:RepetitionDueToSameAction .
            ?i tmr4i:action ?ca .
            ?ca rdfs:label ?ca_label .
            BIND(tmr4i:RepetitionDueToSameAction AS ?itype)
        } UNION {
            ?i a tmr4i:ContradictionDueToInverseTransition .
            BIND(tmr4i:ContradictionDueToInverseTransition AS ?itype)
        } UNION {
            ?i a tmr4i:AlternativeDueToSimilarTransition .
            BIND(tmr4i:AlternativeDueToSimilarTransition AS ?itype)
        } UNION {
            ?i a tmr4i:AlternativeDueToInverseTransition .
            BIND(tmr4i:AlternativeDueToInverseTransition AS ?itype)
        } UNION {
            ?i a tmr4i:ContradictionDueToSimilarTransition .
            BIND(tmr4i:ContradictionDueToSimilarTransition AS ?itype)
        }
        BIND(tmr4i:InternallyInteractingRecommendation AS ?irec)
    }"""

    internal_interactions = sparql(query, strip=True)

    deduped_internal_interactions = []
    double_interactions = set()
    print len(internal_interactions)

    # Go through all detected internal interactions, and remove the duplicates (but retain directedness).
    for r in internal_interactions :
        if 'rec' and 'internal_rec' in r:
            r1 = r['rec']['value']
            r2 = r['internal_rec']['value']

            if (r1,r2) in double_interactions :
                log.debug("Interaction couple already found")
            elif (r2, r1) in double_interactions :
                log.debug("Interaction couple found in other direction, still adding")
                double_interactions.add((r1,r2))
                deduped_internal_interactions.append(r)
            else :
                log.debug("Interaction couple is fresh! Yum.")
                double_interactions.add((r1,r2))
                deduped_internal_interactions.append(r)
        else :
            deduped_internal_interactions.append(r)

    print len(deduped_internal_interactions)

    all_results.extend(deduped_internal_interactions)

    query = PREFIXES + """
        SELECT DISTINCT * WHERE
        {
            ?rec tmr4i:partOf <""" + guideline_uri + """>  .
            ?rec rdfs:label ?rec_label .
            ?rec a owl:NamedIndividual .
            ?rec tmr4i:interactsExternallyWith ?external_rec .
            ?external_rec rdfs:label ?external_rec_label .
            ?external_rec a tmr4i:Recommendation .
            ?external_rec a owl:NamedIndividual .
            ?i tmr4i:relates ?rec .
            ?i tmr4i:relates ?external_rec .
            ?i tmr4i:drug ?drug1 .
            ?drug1 rdfs:label ?drug1_label .
            ?i tmr4i:drug ?drug2 .
            ?drug2 rdfs:label ?drug2_label .
            FILTER(?drug1 != ?drug2)
            BIND(tmr4i:ExternallyInteractingRecommendation AS ?erec)
        }
    """

    all_results.extend(sparql(query, strip=True))

    query = PREFIXES + """
        SELECT DISTINCT * WHERE
        {
            ?rec tmr4i:partOf <""" + guideline_uri + """>  .
            ?rec rdfs:label ?rec_label .
            ?rec a owl:NamedIndividual .
            ?i tmr4i:relates ?rec .
            ?i tmr4i:action ?care_action .
            ?care_action rdfs:label ?care_action_label .
            ?i tmr4i:drug ?drug1 .
            ?drug1 rdfs:label ?drug1_label .
            ?i tmr4i:alternative_drug ?drug2 .
            ?drug2 rdfs:label ?drug2_label .
            BIND(tmr4i:ExternallyInteractingRecommendation AS ?erec)
        }
    """
    all_results.extend(sparql(query, strip=True))

    log.debug(all_results)

    recommendations = []
    double_drugs = set()
    print len(all_results)
    for r in all_results :
        if 'drug1_label' and 'drug2_label' in r:
            d1 = r['drug1_label']['value']
            d2 = r['drug2_label']['value']

            if (d2,d1) in double_drugs:
                log.debug("Drug couple already found")
            else :
                double_drugs.add((d1,d2))
                recommendations.append(r)
        else :
            recommendations.append(r)

    print len(recommendations)

    pprint.pprint(recommendations)

    return render_template('recommendations_list.html', recommendations_menu = recommendations_menu, recommendations = recommendations, guideline_label = guideline_label)

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
        ?transition tmr4i:promotedBy ?care_action .
        ?care_action rdfs:label ?care_action_label .
        ?care_action a owl:NamedIndividual .
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
            ?irec rdfs:label ?irec_label .
        }
        OPTIONAL {
            ?transition tmr4i:similarToTransition ?similar_transition .
            ?similar_transition a owl:NamedIndividual .
            ?srec tmr4i:recommends ?similar_transition .
            ?srec rdfs:label ?srec_label .
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
        ?transition tmr4i:promotedBy ?care_action .
        ?care_action rdfs:label ?care_action_label .
        ?care_action a owl:NamedIndividual .
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
            ?irec rdfs:label ?irec_label .
        }
        OPTIONAL {
            ?transition tmr4i:similarToTransition ?similar_transition .
            ?similar_transition a owl:NamedIndividual .
            ?srec tmr4i:recommends ?similar_transition .
            ?srec rdfs:label ?srec_label .
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

    log.debug(query)

    result = requests.post(endpoint_url,params={'reasoning': REASONING_TYPE}, data=query, headers=UPDATE_HEADERS)

    return result.content

def sparql(query, strip=False, endpoint_url = ENDPOINT_URL):
    """This method replaces the SPARQLWrapper SPARQL interface, since SPARQLWrapper cannot handle the Stardog-style query headers needed for inferencing"""

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
                    new_result[k+'_label']['value'] = v['value'][v['value'].rfind('/')+1:]

                elif not k+'_label' in r.keys():
                    new_result[k+'_label'] = {}
                    new_result[k+'_label']['type'] = 'literal'
                    new_result[k+'_label']['value'] = v['value']

                new_result[k+'_stripped'] = {}
                new_result[k+'_stripped']['type'] = 'literal'
                new_result[k+'_stripped']['value'] = v['value'][v['value'].rfind('/')+1:]


                new_result[k] = v

            new_results.append(new_result)

        log.debug(new_results)
        return new_results
    else :
        return result_dict['results']['bindings']







def internal_recommendation_interaction():
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

    log.debug("{} interactions found.".format(len(deduped_results)))

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







def incompatible_drugs_external_interaction():
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

    log.debug("{} external interactions found.".format(len(deduped_results)))

    update_template = PREFIXES + """
            INSERT DATA
            {{
            tmr4i:{0}   a  tmr4i:IncompatibleDrugExternalInteraction, owl:NamedIndividual .
            tmr4i:{0}   tmr4i:relates <{1}> .
            tmr4i:{0}   tmr4i:relates <{2}> .
            tmr4i:{0}   tmr4i:drug <{3}> .
            tmr4i:{0}   tmr4i:drug <{4}> .
            <{1}> tmr4i:interactsExternallyWith <{2}> .
            <{2}> tmr4i:interactsExternallyWith <{1}> .
            }}
            """

    for (ROne,RTwo,DOne,DTwo) in deduped_results :
        interaction = "external_recommendation_interaction_{}".format(str(uuid.uuid4()))

        update = update_template.format(interaction, ROne,RTwo,DOne,DTwo)

        print interaction, ROne,RTwo,DOne,DTwo
        result = sparql_update(update)









def alternative_drugs_external_interaction():
    query = PREFIXES + """
        SELECT DISTINCT ?rec ?ca ?d ?dALT WHERE
        {
        { {?i a tmr4i:ContradictionDueToSameAction .} UNION {?i a tmr4i:ContradictionDueToInverseTransition .}
        UNION {?i a tmr4i:ContradictionDueToSimiliarTransition .} UNION {?i a tmr4i:IncompatibleDrugExternalInteraction .} }
                                                        #Given a contradictory or incompatibleDrug interaction (search for alternatives when it's needed)
        ?i tmr4i:relates ?rec .
        ?rec tmr4i:recommendsToPursue ?t .
        ?rec tmr4i:partOf ?g .
        ?t tmr4i:regards ?dc .						  	#For a transition related with the effect meant by DrugCategory

        ?t tmr4i:promotedBy ?ca .
        ?ca tmr4i:involves ?d .

        ?dALT drugbank:drugCategory ?dc .				#Find alternative drugs with the same effect / Category

        FILTER (?d != ?dALT) .

        FILTER NOT EXISTS                               #Don't consider alternative drugs that are incompatible with recommended ones
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
        ?iir   tmr4i:drug ?d .
        ?iir   tmr4i:alternative_drug ?dALT .
        }

        }
        """

    results = sparql(query)
    log.debug(results)

    deduped_results = set()
    for r in results :
        rec = r['rec']['value']
        ca = r['ca']['value']
        DOne = r['d']['value']
        DTwo = r['dALT']['value']

        if not (rec,ca,DTwo,DOne) in deduped_results:
            print "adding", (rec,ca,DOne,DTwo)
            deduped_results.add((rec,ca,DOne,DTwo))
        else :
            print "result already found", (rec,ca,DTwo,DOne)

    log.debug("{} external alternative interactions found.".format(len(deduped_results)))

    update_template = PREFIXES + """
            INSERT DATA
            {{
            tmr4i:{0}   a  tmr4i:AlternativeDrugExternalInteraction, owl:NamedIndividual .
            tmr4i:{0}   tmr4i:relates <{1}> .
            tmr4i:{0}   tmr4i:action <{2}> .
            tmr4i:{0}   tmr4i:drug <{3}> .
            tmr4i:{0}   tmr4i:alternative_drug <{4}> .
            }}
            """

    for (rec,ca,DOne,DTwo) in deduped_results :
        interaction = "external_recommendation_interaction_{}".format(str(uuid.uuid4()))

        update = update_template.format(interaction, rec,ca,DOne,DTwo)

        print interaction, rec,ca,DOne,DTwo
        result = sparql_update(update)





def same_as():
    # Including insert query to derive owl:sameAs for cumulative interactions
    # The rules for classifying the internal interaction should be already performed

    query = PREFIXES + """
        INSERT
        {   ?i1 owl:sameAs ?i2 .
            ?i1 tmr4i:relates ?r3 .
            ?i2 tmr4i:relates ?r1 .}
        WHERE
        {   ?i1    a    owl:NamedIndividual .
            ?i2    a    owl:NamedIndividual .
            {  { ?i1 a tmr4i:RepetitionDueToSameAction . ?i2 a tmr4i:RepetitionDueToSameAction .}
              UNION
              { ?i1 a tmr4i:AlternativeDueToSimilarTransition . ?i2 a tmr4i:AlternativeDueToSimilarTransition .}
            }
            ?g    a    tmr4i:Guideline, owl:NamedIndividual .
            ?r1    a    tmr4i:Recommendation, owl:NamedIndividual .
            ?r2    a    tmr4i:Recommendation, owl:NamedIndividual .
            ?r3    a    tmr4i:Recommendation, owl:NamedIndividual .
            ?r1    tmr4i:partOf     ?g .
            ?r2    tmr4i:partOf     ?g .
            ?r3    tmr4i:partOf     ?g .
            ?i1    tmr4i:relates     ?r1 .
            ?i1    tmr4i:relates     ?r2 .
            ?i2    tmr4i:relates     ?r2 .
            ?i2    tmr4i:relates     ?r3 .
            FILTER (?r1	!= ?r2 && ?r1 != ?r3 && ?r2 != ?r3 && ?i1 != ?i2)
        }
        """

    results = sparql_update(query)
    log.debug(results)
