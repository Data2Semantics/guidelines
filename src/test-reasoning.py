#!/bin/python

queries = {
    'rules_loaded': """SELECT (COUNT(DISTINCT ?r) as ?c) { ?r	a rule:SPARQLRule . }""",
    'same_individuals': """SELECT (COUNT(DISTINCT ?i1) as ?c) { ?i1 owl:sameAs ?i2 . ?i1 a owl:NamedIndividual. ?i2 a owl:NamedIndividual }""",
    'different_individuals': """SELECT (COUNT(DISTINCT ?i1) as ?c) { ?i1 owl:differentFrom ?i2 . ?i1 a owl:NamedIndividual. ?i2 a owl:NamedIndividual }""",  
    'internal_interaction_count': """SELECT (COUNT(DISTINCT ?iir) as ?c) { ?iir	a tmr4i:InternalRecommendationInteraction . }""",
    'internal_interaction_c': """
        ASK { 
                ?iir   a  tmr4i:InternalRecommendationInteraction .
                ?iir   tmr4i:relates ?r1 .
                ?iir   tmr4i:relates ?r2 .
                ?r1 tmr4i:interactsInternallyWith ?r2 .
                ?r2 tmr4i:interactsInternallyWith ?r1 .
                tmr4i:interactsInternallyWith a owl:ObjectProperty . 
            }""",
    'internal_interaction_a': """
        ASK {              
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
                         ?ca    a tmr4i:CareAcionType .
                         ?ca    a owl:NamedIndividual .
                         ?t1    tmr4i:promotedBy ?ca .
                         ?t2    tmr4i:promotedBy ?ca .
                     }
                     FILTER (?r1 != ?r2 && ?t1 != ?t2)
             }""",
    'rule_01_similarTo_c': """ASK { ?t1	tmr4i:similarToTransition ?t2 . ?t1 a owl:NamedIndividual . ?t2 a owl:NamedIndividual .}""",
    'rule_01_similarTo_a': """
        ASK { ?ca1	a	tmr4i:CareActionType, owl:NamedIndividual .
        ?ca2	a	tmr4i:CareActionType, owl:NamedIndividual .
        ?sa    a    tmr4i:SituationType, owl:NamedIndividual .
        ?sb    a    tmr4i:SituationType, owl:NamedIndividual .
        ?t1    a    tmr4i:Transition, owl:NamedIndividual .
        ?t2    a    tmr4i:Transition, owl:NamedIndividual .
        ?t1    tmr4i:promotedBy    ?ca1 .
        ?t2    tmr4i:promotedBy    ?ca2 .
        ?t1    tmr4i:hasExpectedPostSituation     ?sb .
        ?t2    tmr4i:hasExpectedPostSituation     ?sb .
        ?t1    tmr4i:hasTransformableSituation     ?sa .
        ?t2    tmr4i:hasTransformableSituation     ?sa .
        # ?ca1    owl:differentFrom    ?ca2 .
        FILTER (?ca1 != ?ca2 && ?t1 != ?t2)
        }""",
    'rule_02_inverseTo_c': """ASK { ?t1	tmr4i:inverseToTransition ?t2 . ?t1 a owl:NamedIndividual . ?t2 a owl:NamedIndividual .}""",
    'rule_02_inverseTo_a': """
        ASK { ?sa	a	tmr4i:SituationType, owl:NamedIndividual .
                    ?sb	a	tmr4i:SituationType, owl:NamedIndividual .
                    ?t1	a	tmr4i:Transition, owl:NamedIndividual .
                    ?t2	a	tmr4i:Transition, owl:NamedIndividual .
                    ?t1	tmr4i:hasExpectedPostSituation	 ?sb .
                    ?t2	tmr4i:hasExpectedPostSituation	 ?sa .
                    ?t1	tmr4i:hasTransformableSituation	 ?sa .
                    ?t2	tmr4i:hasTransformableSituation	 ?sb .
                    FILTER (?sa != ?sb)
        }""",

    	'rule_03_contradiction_same_action_c': """ SELECT (COUNT(DISTINCT ?i) as ?c) WHERE { ?i	a	tmr4i:ContradictionDueToSameAction, owl:NamedIndividual . } """,
    	'rule_03_contradiction_same_action_a': """ ASK { ?ca	a	tmr4i:CareActionType, owl:NamedIndividual .
                ?i	a	tmr4i:InternalRecommendationInteraction, owl:NamedIndividual .
                ?r1	a	tmr4i:Recommendation, owl:NamedIndividual .
                ?r2	a	tmr4i:Recommendation, owl:NamedIndividual .
                ?t1	tmr4i:promotedBy	 ?ca .
                ?t2	tmr4i:promotedBy	 ?ca .
                ?r2	tmr4i:recommendsToAvoid	 ?t2 .
                ?r1	tmr4i:recommendsToPursue	 ?t1 .
                ?i	tmr4i:relates	 ?r1 .
                ?i	tmr4i:relates	 ?r2 .
    } """,
    	'rule_04_contradiction_inverse_transition_c': """ SELECT (COUNT(DISTINCT ?i) as ?c) WHERE { ?i	a	tmr4i:ContradictionDueToInverseTransition, owl:NamedIndividual .} """,
    	'rule_04_contradiction_inverse_transition_a': """ ASK { ?i	a	tmr4i:InternalRecommendationInteraction, owl:NamedIndividual .
                ?r1	a	tmr4i:Recommendation, owl:NamedIndividual .
                ?r2	a	tmr4i:Recommendation, owl:NamedIndividual .
                ?t1	tmr4i:inverseToTransition	 ?t2 .
                ?r1	tmr4i:recommendsToPursue	 ?t1 .
                ?r2	tmr4i:recommendsToPursue	 ?t2 .
                ?i	tmr4i:relates	 ?r1 .
                ?i	tmr4i:relates	 ?r2 .
    } """,
    	'rule_05_contradiction_similar_transition_c': """ SELECT (COUNT(DISTINCT ?i) as ?c) WHERE { ?i	a	tmr4i:ContradictionDueToSimiliarTransition, owl:NamedIndividual .} """,
    	'rule_05_contradiction_similar_transition_a': """ ASK { ?i	a	tmr4i:InternalRecommendationInteraction, owl:NamedIndividual .
                ?r1	a	tmr4i:Recommendation, owl:NamedIndividual .
                ?r2	a	tmr4i:Recommendation, owl:NamedIndividual .
                ?r2	tmr4i:recommendsToAvoid	 ?t2 .
                ?r1	tmr4i:recommendsToPursue	 ?t1 .
                ?i	tmr4i:relates	 ?r1 .
                ?i	tmr4i:relates	 ?r2 .
                ?t1	tmr4i:similarToTransition	 ?t2 .
    } """,
    	'rule_06_repetition_same_action_c': """ SELECT (COUNT(DISTINCT ?i) as ?c) WHERE { ?i	a	tmr4i:RepetitionDueToSameAction, owl:NamedIndividual .} """,
    	'rule_06_repetition_same_action_a': """ ASK { ?ca	a	tmr4i:CareActionType, owl:NamedIndividual .
                ?i	a	tmr4i:InternalRecommendationInteraction, owl:NamedIndividual .
                ?r1	a	tmr4i:Recommendation, owl:NamedIndividual .
                ?r2	a	tmr4i:Recommendation, owl:NamedIndividual .
                ?t1	tmr4i:promotedBy	 ?ca .
                ?t2	tmr4i:promotedBy	 ?ca .
                ?r1	tmr4i:recommendsToPursue	 ?t1 .
                ?r2	tmr4i:recommendsToPursue	 ?t2 .
                ?i	tmr4i:relates	 ?r1 .
                ?i	tmr4i:relates	 ?r2 .
                FILTER (?t1 != ?t2)
    } """,
    	'rule_07_same_as_repetition_c': """ SELECT (COUNT(DISTINCT ?i1) as ?c) WHERE { ?i1	owl:sameAs	?i2 ; a tmr4i:RepetitionDueToSameAction, owl:NamedIndividual .} """,
    	'rule_07_same_as_repetition_a': """ ASK { ?g	a	tmr4i:Guideline, owl:NamedIndividual .
                ?r1	a	tmr4i:Recommendation, owl:NamedIndividual .
                ?r2	a	tmr4i:Recommendation, owl:NamedIndividual .
                ?r3	a	tmr4i:Recommendation, owl:NamedIndividual .
                ?i1	a	tmr4i:RepetitionDueToSameAction, owl:NamedIndividual .
                ?i2	a	tmr4i:RepetitionDueToSameAction, owl:NamedIndividual .
                ?r1	tmr4i:partOf	 ?g .
                ?r2	tmr4i:partOf	 ?g .
                ?r3	tmr4i:partOf	 ?g .
                ?i1	tmr4i:relates	 ?r1 .
                ?i1	tmr4i:relates	 ?r2 .
                ?i2	tmr4i:relates	 ?r2 .
                ?i2	tmr4i:relates	 ?r3 .
                ?r1	owl:differentFrom	?r3 .
    } """,
    	'rule_08_alternative_inverse_transition_c': """ SELECT (COUNT(DISTINCT ?i) as ?c) WHERE { ?i	a	tmr4i:AlternativeDueToInverseTransition, owl:NamedIndividual .} """,
    	'rule_08_alternative_inverse_transition_a': """ ASK { ?i	a	tmr4i:InternalRecommendationInteraction, owl:NamedIndividual .
                ?r1	a	tmr4i:Recommendation, owl:NamedIndividual .
                ?r2	a	tmr4i:Recommendation, owl:NamedIndividual .
                ?t1	tmr4i:inverseToTransition	 ?t2 .
                ?r2	tmr4i:recommendsToAvoid	 ?t2 .
                ?r1	tmr4i:recommendsToPursue	 ?t1 .
                ?i	tmr4i:relates	 ?r1 .
                ?i	tmr4i:relates	 ?r2 .
    } """,
        'rule_08_TEST': """ ASK { ?i tmr4i:relates tmr4i:RecDUTIA-AvoidBleeding, tmr4i:RecDUTIA-RedMediumRiskVE . }""",
    	'rule_09_same_as_alternative_similar_transition_c': """ SELECT (COUNT(DISTINCT ?i1) as ?c) WHERE { ?i1	tmr4i:sameAs	?i2; a tmr4i:AlternativeDueToSimilarTransition, owl:NamedIndividual .} """,
    	'rule_09_same_as_alternative_similar_transition_a': """ 
        
            ASK { 
                ?i1	a	tmr4i:AlternativeDueToSimilarTransition, owl:NamedIndividual .
                ?i2	a	tmr4i:AlternativeDueToSimilarTransition, owl:NamedIndividual .
                ?g	a	tmr4i:Guideline, owl:NamedIndividual .
                ?r1	a	tmr4i:Recommendation, owl:NamedIndividual .
                ?r2	a	tmr4i:Recommendation, owl:NamedIndividual .
                ?r3	a	tmr4i:Recommendation, owl:NamedIndividual .
                ?r1	tmr4i:partOf	 ?g .
                ?r2	tmr4i:partOf	 ?g .
                ?r3	tmr4i:partOf	 ?g .
                ?i1	tmr4i:relates	 ?r1 .
                ?i1	tmr4i:relates	 ?r2 .
                ?i2	tmr4i:relates	 ?r2 .
                ?i2	tmr4i:relates	 ?r3 .
                FILTER (?r1	!=	?r3) .
    } """,
    	'rule_10_alternative_similar_transition_c': """ SELECT (COUNT(DISTINCT ?i) as ?c) WHERE { ?i	a	tmr4i:AlternativeDueToSimilarTransition .} """,
    	'rule_10_alternative_similar_transition_a': """ ASK { ?i	a	tmr4i:InternalRecommendationInteraction, owl:NamedIndividual .
                ?r1	a	tmr4i:Recommendation, owl:NamedIndividual .
                ?r2	a	tmr4i:Recommendation, owl:NamedIndividual .
                ?r1	tmr4i:recommendsToPursue	 ?t1 .
                ?r2	tmr4i:recommendsToPursue	 ?t2 .
                ?i	tmr4i:relates	 ?r1 .
                ?i	tmr4i:relates	 ?r2 .
                ?t1	tmr4i:similarToTransition	 ?t2 .
                FILTER(?r1 != ?r2)
    }  """
}

expected = """
AlternativeDueToInverseTransition
*	DUTIAInteraction3 relates RecDUTIA-ProtectingDuodenum and RecDUTIA-AvoidBleeding

AlternativeDueToSimilarTransition
	DUTIAInteraction2 relates RecDUTIA-RedMediumRiskVE and RecDUTIASol-RedMediumRiskVE
	OA-HT-DM-Interaction4 relates RecOA-HT-DM-Painkiller and RecOA-HT-DM-Sol-Painkiller
	OA-HT-DM-Interaction5 relates RecOA-HT-DM-AntiThrombotic and RecOA-HT-DM-Sol-AntiThrombotic
	OA-HT-DM-InteractionExtra relates RecOA-HT-DM-AntiThrombotic and RecOA-HT-DM-Extra-AntiThrombotic

ContradictionDueToSameAction
*	DUTIAInteraction1 relates RecDUTIA-AvoidBleeding and RecDUTIA-RedMediumRiskVE 
	OA-HT-DM-Interaction1 relates RecOA-HT-DM-AvoidGIB and RecOA-HT-DM-AntiThrombotic
	OA-HT-DM-Interaction2 relates RecOA-HT-DM-AvoidHighBP and RecOA-HT-DM-Painkiller
	OA-HT-DM-Interaction3 relates RecOA-HT-DM-AvoidHighLBS and RecOA-HT-DM-Diuretic

RepetitionDueToSameAction
	DUTIAInteraction4 relates RecDUTIASol-ProtectingDuodenum and RecDUTIA-HealingDU2
*	OA-HT-DM-Interaction6 relates RecOA-HT-DM-Sol-AntiThrombotic and RecOA-HT-DM-Sol-Painkiller

OA-HT-DM-Interaction5 sameAs OA-HT-DM-InteractionExtra

"""


from app.views import *
import xml.etree.ElementTree as ET
import collections

if __name__ == '__main__':
    # sparql = SPARQLWrapper('http://localhost:5820/guidelines/query')
    # sparql.setReturnFormat(XML)
    # sparql.addParameter('reasoning','SL')
    print expected
    ordered_queries = collections.OrderedDict(sorted(queries.items()))
    
    for name,query in ordered_queries.iteritems():
        results = sparql(query)
        if isinstance(results,str):
            root = ET.fromstring(results)
            value = root[1].text
        else :
            value = results[0]['c']['value']
        
        print "{}:\t{}".format(name.ljust(50),value)
        

