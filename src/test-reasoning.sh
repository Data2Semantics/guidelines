#!/bin/sh

# echo "Testing for inferred properties of painkiller"
#
# stardog query "guidelines;reasoning=SL" "SELECT * {<http://guidelines.data2semantics.org/vocab/RecOA-HT-DM-Painkiller> ?p ?o . ?p a owl:ObjectProperty . ?o a owl:NamedIndividual . <http://guidelines.data2semantics.org/vocab/RecOA-HT-DM-Painkiller> a owl:NamedIndividual .}"
#
# echo "Testing for the existence of interactions"
#
# stardog query "guidelines;reasoning=SL" "SELECT * {?s a <http://guidelines.data2semantics.org/vocab/InternalRecommendationInteraction> . ?s a owl:NamedIndividual .}"

echo "Check if rules were loaded (should be 12)"
stardog query "guidelines;reasoning=SL" "SELECT (COUNT(DISTINCT ?r) as ?c) { ?r	a rule:SPARQLRule . }"

echo "Rule - Interaction Assertion"
stardog query "guidelines;reasoning=SL" "ASK { ?iir   a  tmr4i:InternalRecommendationInteraction .
            ?iir   tmr4i:relates ?r1 .
            ?iir   tmr4i:relates ?r2 .
            ?r1 tmr4i:interactsInternallyWith ?r2 .
            ?r2 tmr4i:interactsInternallyWith ?r1 .
            tmr4i:interactsInternallyWith a owl:ObjectProperty . }"

echo "Rule - Interaction Assertion (antecedent check)"
stardog query "guidelines;reasoning=SL" "ASK {              ?r1  a  tmr4i:Recommendation .
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
             
             BIND(UUID() AS ?iir)}"

echo "Rule 1"
stardog query "guidelines;reasoning=SL" "ASK { ?t1	tmr4i:similarToTransition ?t2 . ?t1 a owl:NamedIndividual . ?t2 a owl:NamedIndividual .}"

echo "Rule 1 antecedent check"
stardog query "guidelines;reasoning=SL" "ASK { ?ca1	a	tmr4i:CareActionType, owl:NamedIndividual .
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
?ca1    owl:differentFrom    ?ca2 .
}"

echo "Rule 2"

stardog query "guidelines;reasoning=SL" "ASK { ?t1	tmr4i:inverseToTransition ?t2 . ?t1 a owl:NamedIndividual . ?t2 a owl:NamedIndividual .}"

echo "Rule 2 antecedent check"
stardog query "guidelines;reasoning=SL" "ASK { ?sa	a	tmr4i:SituationType, owl:NamedIndividual .
            ?sb	a	tmr4i:SituationType, owl:NamedIndividual .
            ?t1	a	tmr4i:Transition, owl:NamedIndividual .
            ?t2	a	tmr4i:Transition, owl:NamedIndividual .
            ?t1	tmr4i:hasExpectedPostSituation	 ?sb .
            ?t2	tmr4i:hasExpectedPostSituation	 ?sa .
            ?t1	tmr4i:hasTransformableSituation	 ?sa .
            ?t2	tmr4i:hasTransformableSituation	 ?sb .
}"

echo "Rule 3"

stardog query "guidelines;reasoning=SL" "ASK { ?i	a	tmr4i:ContradictionDueToSameAction, owl:NamedIndividual . }"

echo "Rule 3 antecedent check"
stardog query "guidelines;reasoning=SL" "ASK { ?ca	a	tmr4i:CareActionType, owl:NamedIndividual .
            ?i	a	tmr4i:InternalRecommendationInteraction, owl:NamedIndividual .
            ?r1	a	tmr4i:Recommendation, owl:NamedIndividual .
            ?r2	a	tmr4i:Recommendation, owl:NamedIndividual .
            ?t1	tmr4i:promotedBy	 ?ca .
            ?t2	tmr4i:promotedBy	 ?ca .
            ?r2	tmr4i:recommendsToAvoid	 ?t2 .
            ?r1	tmr4i:recommendsToPursue	 ?t1 .
            ?i	tmr4i:relates	 ?r1 .
            ?i	tmr4i:relates	 ?r2 .
}"

echo "Rule 4"

stardog query "guidelines;reasoning=SL" "ASK { ?i	a	tmr4i:ContradictionDueToInverseTransition, owl:NamedIndividual .}"

echo "Rule 4 antecedent check"
stardog query "guidelines;reasoning=SL" "ASK { ?i	a	tmr4i:InternalRecommendationInteraction, owl:NamedIndividual .
            ?r1	a	tmr4i:Recommendation, owl:NamedIndividual .
            ?r2	a	tmr4i:Recommendation, owl:NamedIndividual .
            ?t1	tmr4i:inverseToTransition	 ?t2 .
            ?r1	tmr4i:recommendsToPursue	 ?t1 .
            ?r2	tmr4i:recommendsToPursue	 ?t2 .
            ?i	tmr4i:relates	 ?r1 .
            ?i	tmr4i:relates	 ?r2 .
}"


echo "Rule 5"

stardog query "guidelines;reasoning=SL" "ASK { ?i	a	tmr4i:ContradictionDueToSimiliarTransition, owl:NamedIndividual .}"

echo "Rule 5 antecedent check"
stardog query "guidelines;reasoning=SL" "ASK { ?i	a	tmr4i:InternalRecommendationInteraction, owl:NamedIndividual .
            ?r1	a	tmr4i:Recommendation, owl:NamedIndividual .
            ?r2	a	tmr4i:Recommendation, owl:NamedIndividual .
            ?r2	tmr4i:recommendsToAvoid	 ?t2 .
            ?r1	tmr4i:recommendsToPursue	 ?t1 .
            ?i	tmr4i:relates	 ?r1 .
            ?i	tmr4i:relates	 ?r2 .
            ?t1	tmr4i:similarToTransition	 ?t2 .
}"

echo "Rule 6"

stardog query "guidelines;reasoning=SL" "ASK { ?i	a	tmr4i:RepetitionDueToSameAction, owl:NamedIndividual .}"

echo "Rule 6 antecedent check"
stardog query "guidelines;reasoning=SL" "ASK { ?ca	a	tmr4i:CareActionType, owl:NamedIndividual .
            ?i	a	tmr4i:InternalRecommendationInteraction, owl:NamedIndividual .
            ?r1	a	tmr4i:Recommendation, owl:NamedIndividual .
            ?r2	a	tmr4i:Recommendation, owl:NamedIndividual .
            ?t1	tmr4i:promotedBy	 ?ca .
            ?t2	tmr4i:promotedBy	 ?ca .
            ?r1	tmr4i:recommendsToPursue	 ?t1 .
            ?r2	tmr4i:recommendsToPursue	 ?t2 .
            ?i	tmr4i:relates	 ?r1 .
            ?i	tmr4i:relates	 ?r2 .
            ?t1	owl:differentFrom	?t2 .
}"


echo "Rule 7 (only checking for owl:sameAs links...)"

stardog query "guidelines;reasoning=SL" "ASK { ?i1	owl:sameAs	?i2 , owl:NamedIndividual .}"

echo "Rule 7 antecedent check"
stardog query "guidelines;reasoning=SL" "ASK { ?g	a	tmr4i:Guideline, owl:NamedIndividual .
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
}"


echo "Rule 8"

stardog query "guidelines;reasoning=SL" "ASK { ?i	a	tmr4i:AlternativeDueToInverseTransition, owl:NamedIndividual .}"

echo "Rule 8 antecedent check"
stardog query "guidelines;reasoning=SL" "ASK { ?i	a	tmr4i:InternalRecommendationInteraction, owl:NamedIndividual .
            ?r1	a	tmr4i:Recommendation, owl:NamedIndividual .
            ?r2	a	tmr4i:Recommendation, owl:NamedIndividual .
            ?t1	tmr4i:inverseToTransition	 ?t2 .
            ?r2	tmr4i:recommendsToAvoid	 ?t2 .
            ?r1	tmr4i:recommendsToPursue	 ?t1 .
            ?i	tmr4i:relates	 ?r1 .
            ?i	tmr4i:relates	 ?r2 .
}"

echo "Rule 9 (sameAs check)"

stardog query "guidelines;reasoning=SL" "ASK { ?i1	owl:sameAs	?i2, owl:NamedIndividual .}"

echo "Rule 9 antecedent check"
stardog query "guidelines;reasoning=SL" "ASK { ?i1	a	tmr4i:AlternativeDueToSimilarTransition, owl:NamedIndividual .
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
            ?r1	owl:differentFrom	?r3 .
}"


echo "Rule 10"

stardog query "guidelines;reasoning=SL" "ASK { ?i	a	tmr4i:AlternativeDueToSimilarTransition, owl:NamedIndividual . }"

echo "Rule 10 antecedent check"
stardog query "guidelines;reasoning=SL" "ASK { ?i	a	tmr4i:InternalRecommendationInteraction, owl:NamedIndividual .
            ?r1	a	tmr4i:Recommendation, owl:NamedIndividual .
            ?r2	a	tmr4i:Recommendation, owl:NamedIndividual .
            ?r1	tmr4i:recommendsToPursue	 ?t1 .
            ?r2	tmr4i:recommendsToPursue	 ?t2 .
            ?i	tmr4i:relates	 ?r1 .
            ?i	tmr4i:relates	 ?r2 .
            ?t1	tmr4i:similarToTransition	 ?t2 .
}"


echo "Rule 11 (sameAs check)"

stardog query "guidelines;reasoning=SL" "ASK { ?t1	owl:sameAs	?t2 , owl:NamedIndividual . }"

echo "Rule 11 antecedent check"
stardog query "guidelines;reasoning=SL" "ASK { ?ca	a	tmr4i:CareActionType, owl:NamedIndividual .
            ?sa	a	tmr4i:SituationType, owl:NamedIndividual .
            ?sb	a	tmr4i:SituationType, owl:NamedIndividual .
            ?t1	a	tmr4i:Transition, owl:NamedIndividual .
            ?t2	a	tmr4i:Transition, owl:NamedIndividual .
            ?t1	tmr4i:hasExpectedPostSituation	 ?sb .
            ?t2	tmr4i:hasExpectedPostSituation	 ?sa .
            ?t1	tmr4i:hasTransformableSituation	 ?sa .
            ?t2	tmr4i:hasTransformableSituation	 ?sb .
            ?t1	tmr4i:promotedBy	 ?ca .
            ?t2	tmr4i:promotedBy	 ?ca .
}"