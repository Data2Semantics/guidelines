:- module(
  metis,
  [
    show_graphs/0
  ]
).

/** <module> Metis

@author Veruska
@author Wouter
@version 2015/03
*/

:- use_module(library(apply)).
:- use_module(library(filesex)).
:- use_module(library(http/http_dispatch)).
:- use_module(library(http/http_json)).
:- use_module(library(http/thread_httpd)).
:- use_module(library(semweb/rdf_db)).
:- use_module(library(semweb/rdf_turtle)).

:- rdf_register_prefix(data, 'http://guidelines.data2semantics.org/data/').
:- rdf_register_prefix(
  tmr,
  'http://guidelines.data2semantics.org/vocab/tmr/'
).
:- rdf_register_prefix(
  tmr4i,
  'http://guidelines.data2semantics.org/vocab/tmr4i/'
).

:- http_handler(/, process_request, []).

:- initialization(init).



/* *********************************** */
% Initialization/Loading functions
init:-
  http_server(http_dispatch, [port(3030)]),
  load_data,
  load_schema,
  inferInternalInteractions.

load_data:-
  expand_file_name('data/instance/*.ttl', Files),
  maplist(rdf_load0, Files).

load_schema:-
  expand_file_name('data/schema/*.ttl', Files),
  maplist(rdf_load0, Files).

rdf_load0(File):-
  directory_file_path(_, LocalName, File),
  file_name_extension(Graph, _, LocalName),
  rdf_load(File, [format(turtle),graph(Graph)]).

show_graphs:-
  forall(
    rdf_statistics(triples_by_graph(G,T)),
    format(user_output, '\t~D\t~a\n', [T,G])
  ).


/* *********************************** */
% API functions

process_request(Request) :-
  memberchk(request_uri(Uri), Request),
  uri_components(Uri, uri_components(_,_,_,QueryString,_)),
  uri_query_components(QueryString, Query),
  memberchk(type=Type, Query),
  (
    Type = 'getGuidelines'
    ->
    setof(CIG, guideline(CIG), CIGsList),
    reply_json_dict(json{guidelines: CIGsList})
    ;
    Type = 'getRecommendations'
    ->
    memberchk(guideline=Guideline, Query),
    setof(Rec, rec(Rec, Guideline), RecList),
    reply_json_dict(json{recommendations: RecList})
    ;
    Type = 'getInteractions'
    ->
    %run the rules just for the requered guidelines? (instead of running on initialization?)
    memberchk(guideline=Guideline, Query),
    setof(InteractionDict, interactingRecommendations(InteractionDict, Guideline), IntRecList),
    reply_json_dict(json{interactions: IntRecList})
    %;
    %Type = 'mergeGuidelines'
    %->
    %memberchk(listCIGs=ListCIGs, Query),
    %mergeCGs(ListCIGs, newCIGURI),
    %reply_json_dict(json{mergedCIG: newCIGURI})
  ).



/* *********************************** */
% ** check if a resource is a Guideline
% ** retrieves all guidelines
guideline(G) :-
    rdf(G, rdf:type, Type),
    rdf_reachable(Type, rdfs:subClassOf, tmr:'Guideline').


/* *********************************** */
% ** given a guideline, retrieves its recommendations and features
recommendation(Rec, Guideline, Value, Belief) :-
    rdf(Rec, rdf:type, tmr:'Recommendation'),
    rdf(Rec, tmr:'partOf', Guideline),
    rdf(Rec, tmr:'hasValue', literal(type(xsd:string, Value))),
    rdf(Rec, tmr:'basedOn', Belief).

% ** retrieves guidelines and their recommendations
rec(Rec, Guideline) :-
    rdf(Rec, rdf:type, tmr:'Recommendation'),
    rdf(Rec, tmr:'partOf', Guideline).


/* *********************************** */
% ** given a belief retrieves its features
% ** retrieves all belief and its features
causationBelief(B, Value, Cause, Effect) :-
    rdf(B, rdf:type, tmr:'CausationBelief'),
    rdf(B, tmr:'hasValue', literal(type(xsd:string, Value))),
    rdf(B, tmr:'hasCause', Cause),
    rdf(B, tmr:'hasEffect', Effect).


/* *********************************** */
% ** check if a resource is a Action Type
% ** retrieves all Action Types
careActionT(A) :-
    rdf(A, rdf:type, Type),
    rdf_reachable(Type, rdfs:subClassOf, tmr:'CareActionType').

subsumesActionT(ActionSuperT, ActionT) :-
    (   subsumes(ActionSuperT, ActionT) ->   true
    ;
        rdf(ActionSuperT, tmr:'administrationOf', DrugSuperT),
        rdf(ActionT, tmr:'administrationOf', DrugT),
        subsumes(DrugSuperT, DrugT)
    ).

relatedActionTs(ActionT1, ActionT2) :-
    (   same(ActionT1, ActionT2) ->   true
    ;
        subsumesActionT(ActionT1, ActionT2) ->   true
    ;
        subsumesActionT(ActionT2, ActionT1)
    ).

subsumes(ST, T) :-
    ST \= T,
    rdf_reachable(ST, tmr:'subsumes', T).


/* *********************************** */
% ** check if a resource is a Transition Type
% ** retrieves all Transition Types
transitionT(T) :-
    rdf(T, rdf:type, Type),
    rdf_reachable(Type, rdfs:subClassOf, tmr:'TransitionType').
    %, !.


/* *********************************** */
% ** check if two resources are inverse transitions
% ** given a transition, retrives the inverse ones
% ** retrieves all pairs of inverse transitions
inverse(T1, T2) :-
    rdf(T1, rdf:type, tmr:'TransitionType'),
    rdf(T2, rdf:type, tmr:'TransitionType'),
    rdf(T1, tmr:'hasTransformableSituation', SitA),
    rdf(T1, tmr:'hasExpectedPostSituation', SitB),
    rdf(T2, tmr:'hasTransformableSituation', SitB),
    rdf(T2, tmr:'hasExpectedPostSituation', SitA).


relatedTransitionTs(TransitionT1, TransitionT2) :-
    (   same(TransitionT1, TransitionT2) ->   true
    ;
        subsumes(TransitionT1, TransitionT2)
    ).

/* *********************************** */
% ** check if there is an interaction of a certain type for recommendations
% ** given an Interaction Type, retrieves the interactions
% ** retrieves all interactions and related pair of recommendations
interaction2(IntType, Rec1, Rec2, Interaction) :-
   rdf_global_id(tmr4i:IntType, IntTypeURI),
   rdf(Interaction, rdf:type, IntTypeURI),
   rdf(Interaction, tmr4i:'relates', Rec1),
   rdf(Interaction, tmr4i:'relates', Rec2),
   different(Rec1, Rec2).


/* *********************************** */
% retrieves a dictionary interacting recommendations and the type
interactingRecommendations(InteractionDict, Guideline) :-
    rdf_reachable(IntTypeURI, rdfs:subClassOf, tmr4i:'InternalRecommendationInteraction'),
    rdf(Interaction, rdf:type, IntTypeURI),
    rdf_global_id(tmr4i:IntType, IntTypeURI),
    setof(Rec, interactionRecommendation(Interaction, Rec, Guideline), List),
    InteractionDict = interaction{type:IntType, recList:List}.

interactionRecommendation(Interaction, Recommendation, Guideline) :-
    (rdf_reachable(Interaction, owl:sameAs, I2)
     ;
     rdf_reachable(I2, owl:sameAs, Interaction)
    ),
    rdf(I2, tmr4i:'relates', Recommendation),
    guideline(Guideline),
    rdf_reachable(Recommendation, tmr:'partOf', Guideline).


/* *********************************** */
% ** Assert an interaction of a certain type between the two recommendations
existsInteraction(IntType, Rec1, Rec2) :-
    (   rdf_global_id(tmr4i:IntType, IntTypeURI),
        % asserting the interaction
        rdf(Int, tmr4i:'relates', Rec1, my_entailments),
        rdf(Int, tmr4i:'relates', Rec2, my_entailments),
        rdf(Int, rdf:type, IntTypeURI, my_entailments)
        ->   true
    ;
        % composing new URI for interaction
        rdf_global_id(data:NameRec1, Rec1),
        rdf_global_id(data:NameRec2, Rec2),
        concat_atom([IntType, NameRec1, NameRec2], NewID),
        rdf_global_id(data:NewID, NewURI),
        % composing new URI for IntType
        rdf_global_id(tmr4i:IntType, IntTypeURI),
        % asserting the interaction
        rdf_assert(NewURI, rdf:type, IntTypeURI, my_entailments),
        rdf_assert(NewURI, tmr4i:'relates', Rec1, my_entailments),
        rdf_assert(NewURI, tmr4i:'relates', Rec2, my_entailments)
    ).


/* *********************************** */
% ** infer the internal interactions for all the recommendations in a guideline
inferInternalInteractions :-
    % check Opposed Beliefs
    forall((guideline(G),
     recommendation(R1, G, _, B1),
     causationBelief(B1, 'positive', A1, T1),
     recommendation(R2, G, _, B2),
     causationBelief(B2, 'positive', A2, T2),
     different(R1,R2), inverse(T1,T2), relatedActionTs(A1,A2) ),
            (existsInteraction('RelyingOpposedBeliefs', R1, R2))),

    forall((guideline(G),
     recommendation(R1, G, _, B1),
     causationBelief(B1, 'positive', A1, T1),
     recommendation(R2, G, _, B2),
     causationBelief(B2, 'negative', A2, T2),
     different(R1,R2), same(T1,T2), relatedActionTs(A1,A2) ),
            (existsInteraction('RelyingOpposedBeliefs', R1, R2))),

    % check Contradiction-Action
    forall((guideline(G),
     recommendation(R1, G, 'positive', B1),
     causationBelief(B1, 'positive', A1, _),
     recommendation(R2, G, 'negative', B2),
     causationBelief(B2, 'positive', A2, _),
     different(R1,R2), relatedActionTs(A1,A2)),
            (existsInteraction('Contradiction-Action', R1, R2))),

    % check Contradiction-Transition
    forall((guideline(G),
     recommendation(R1, G, 'positive', B1),
     causationBelief(B1, 'positive', _, T1),
     recommendation(R2, G, 'negative', B2),
     causationBelief(B2, 'positive', _, T2),
     different(R1,R2), same(T1,T2)),
            (existsInteraction('Contradiction-Transition', R1, R2))),

    forall((guideline(G),
     recommendation(R1, G, 'positive', B1),
     causationBelief(B1, 'positive', _, T1),
     recommendation(R2, G, 'positive', B2),
     causationBelief(B2, 'positive', _, T2),
     different(R1,R2), inverse(T1,T2)),
            (existsInteraction('Contradiction-Transition', R1, R2))),

    forall((guideline(G),
     recommendation(R1, G, 'positive', _),
     recommendation(SR1, R1, _, B1),
     causationBelief(B1, 'positive', A1, T1),
     recommendation(R2, G, 'negative', B2),
     causationBelief(B2, 'positive', A2, T2),
     different(R1,R2), same(T1,T2), different(A1,A2)),
            (existsInteraction('Contradiction-Transition',SR1, R2))),

    forall((guideline(G),
     recommendation(R1, G, 'positive', _),
     recommendation(SR1, R1, _, B1),
     causationBelief(B1, 'positive', A1, T1),
     recommendation(R2, G, 'positive', B2),
     causationBelief(B2, 'positive', A2, T2),
     different(R1,R2), inverse(T1,T2), different(A1,A2)),
            (existsInteraction('Contradiction-Transition',SR1, R2))),

    forall((guideline(G),
     recommendation(R1, G, 'positive', _),
     recommendation(SR1, R1, _, B1),
     causationBelief(B1, 'positive', _, T1),
     recommendation(R2, G, 'positive', _),
     recommendation(SR2, R2, _, B2),
     causationBelief(B2, 'positive', _, T2),
     different(R1,R2), inverse(T1,T2)),
            (existsInteraction('Contradiction-Transition',SR1, SR2))),

    % check RepeatedAction
    forall((guideline(G),
     recommendation(R1, G, 'positive', B1),
     causationBelief(B1, _, A1, _),
     recommendation(R2, G, 'positive', B2),
     causationBelief(B2, _, A2, _),
     different(R1,R2), relatedActionTs(A1,A2)),
            (existsInteraction('RepeatedAction',R1, R2))),

    % accumulate RepeatedAction
    forall( (interaction2('RepeatedAction', R1, R2, I1),
     interaction2('RepeatedAction', R2, R3, I2), different(R1,R3), different(I1, I2)),
     rdf_assert(I1, owl:sameAs, I2, my_entailments) ),

    % check AlternativeActions
    forall((guideline(G),
     recommendation(R1, G, 'positive', B1),
     causationBelief(B1, 'positive', A1, T1),
     recommendation(R2, G, 'positive', B2),
     causationBelief(B2, 'positive', A2, T2),
     different(R1,R2), same(T1,T2), different(A1,A2) ),
            (existsInteraction('AlternativeActions', R1, R2))),

    forall((guideline(G),
     recommendation(R1, G, 'positive', _),
     recommendation(SR1, R1, _, B1),
     causationBelief(B1, _, A1, T1),
     recommendation(R2, G, 'positive', B2),
     causationBelief(B2, 'positive', A2, T2),
     different(R1,R2), same(T1,T2), different(A1,A2)),
            (existsInteraction('AlternativeActions',SR1, R2))),

    % accumulate AlternativeActions
    forall( (interaction2('AlternativeActions', R1, R2, I1),
     interaction2('AlternativeActions', R2, R3, I2), different(R1,R3), different(I1, I2)),
     rdf_assert(I1, owl:sameAs, I2, my_entailments) ),

    % check ReparableTransition
    forall((guideline(G),
     recommendation(R1, G, 'negative', B1),
     causationBelief(B1, 'positive', A1, T1),
     recommendation(R2, G, 'positive', B2),
     causationBelief(B2, 'positive', A2, T2),
     different(R1,R2), inverse(T1,T2), different(A1,A2)),
            (existsInteraction('ReparableTransition', R1, R2))),

    forall((guideline(G),
     recommendation(R1, G, 'positive', _),
     recommendation(SR1, R1, _, B1),
     causationBelief(B1, _, A1, T1),
     recommendation(R2, G, 'negative', B2),
     causationBelief(B2, 'positive', A2, T2),
     different(R1,R2), inverse(T1,T2), different(A1,A2)),
            (existsInteraction('ReparableTransition',SR1, R2))),

    % check RepeatedSideEffect
    forall((guideline(G),
     recommendation(R1, G, 'positive', _),
     recommendation(SR1, R1, _, B1),
     causationBelief(B1, 'positive', _, T1),
     recommendation(R2, G, 'positive', _),
     recommendation(SR2, R2, _, B2),
     causationBelief(B2, 'positive', _, T2),
     different(R1,R2), same(T1,T2)),
            (existsInteraction('RepeatedSideEffect',SR1, SR2))),

    % accumulate RepeatedSideEffect
    forall( (interaction2('RepeatedSideEffect', R1, R2, I1),
     interaction2('RepeatedSideEffect', R2, R3, I2),
            different(R1,R3), different(I1, I2)),
     rdf_assert(I1, owl:sameAs, I2, my_entailments) ).



/* *********************************** */
% ** infer external interactions for all the recommendations in a guideline
inferExternalInteractions(G) :-
    guideline(G),
    loadExternalBeliefs(G).
    %forall(   )...

/* *********************************** */
% ** Load external causation beliefs relevants to a guideline
loadExternalBeliefs(G) :-
    guideline(G).
    %load relevant data from drugbank & sider

/* *********************************** */
% different(Resource1, Resource2) {CWA - Negation as failure}
% check if two resources not the same
different(Resource1, Resource2) :-
    \+ same(Resource1, Resource2).

/* *********************************** */
% same(Resource1, Resource2)    {if nothing is said, they are not the same}
% check if two resources are equal or explicitly said to be the same
same(Resource1, Resource2) :-
    (   Resource1 = Resource2
    ;
        rdf_reachable(Resource1, owl:sameAs, Resource2)
    ;
        rdf_reachable(Resource2, owl:sameAs, Resource1)
    ).


/** <examples>
 0) How can I retrieve a saved file?
        > http://localhost:3020/swish/p/InteractionRules.pl
 1) How/when to settle a prefix?
        > rdf_register_prefix(data, 'http://guidelines.data2semantics.org/data/')
 2) How to check equal and different resources?
        > same & different
 3) How to address literals (positive/negative...)
 4) How to create a URI?
    ** does the aasertion (rdf_assert) check if the triple already exists?
    ** Cut?
* 5) Can I retrieve part of an external URI (via query)?
     rdf_load('http://www.w3.org/2000/01/rdf-schema').
     rdf_unload_graph('http://www.w3.org/2000/01/rdf-schema').
     rdf_make.
 6) How to consult from one graph (or a list of graphs?)
 7) return a list as result:
    'Contradiction' , [a,b]
    'Contradiction',  [a,c]
    'Alternative',    [a,d,e]
 8) rdfs:subClassOf => subsumption
* 9) How would I use it in python ?
% https://github.com/SWI-Prolog/swish/blob/master/client/sin-table.html


*/
