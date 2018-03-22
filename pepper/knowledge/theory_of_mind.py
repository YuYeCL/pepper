import subprocess
import json
import requests

from rdflib import Dataset, Graph, URIRef, Literal, Namespace, RDF, RDFS, OWL
from iribaker import to_iri
from hashids import Hashids
from SPARQLWrapper import SPARQLWrapper, JSON

from pepper.knowledge.brainFacts import statements
from pepper.knowledge.brainQuestions import questions

REMOTE_BRAIN = "http://145.100.58.167:50053/sparql"
LOCAL_BRAIN = "http://localhost:7200/repositories/leolani_test2"


class TheoryOfMind(object):
    def __init__(self, address=LOCAL_BRAIN, debug=False):
        """
        Interact with Triple store

        Parameters
        ----------
        address: str
            IP address and port of the Triple store
        """

        self.address = address
        self.debug = debug
        self.namespaces = {}
        self.ontology_paths = {}
        self.dataset = Dataset()
        self.query_prefixes = """
                    prefix gaf: <http://groundedannotationframework.org/gaf#> 
                    prefix grasp: <http://groundedannotationframework.org/grasp#> 
                    prefix leolaniFriends: <http://cltl.nl/leolani/friends/> 
                    prefix leolaniTalk: <http://cltl.nl/leolani/talk/> 
                    prefix leolaniTime: <http://cltl.nl/leolani/date/> 
                    prefix leolaniWorld: <http://cltl.nl/leolani/world/> 
                    prefix n2mu: <http://cltl.nl/leolani/n2mu/> 
                    prefix ns1: <urn:x-rdflib:> 
                    prefix owl: <http://www.w3.org/2002/07/owl#> 
                    prefix prov: <http://www.w3.org/ns/prov#> 
                    prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
                    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
                    prefix sem: <http://semanticweb.cs.vu.nl/2009/11/sem/> 
                    prefix skos: <http://www.w3.org/2004/02/skos/core#> 
                    prefix time: <http://www.w3.org/TR/owl-time/#> 
                    prefix xml: <http://www.w3.org/XML/1998/namespace> 
                    prefix xml1: <https://www.w3.org/TR/xmlschema-2/#> 
                    prefix xsd: <http://www.w3.org/2001/XMLSchema#>
                    """

        self.__define_namespaces__()
        self.__get_ontology_path__()
        self.__bind_namespaces__()

    def __define_namespaces__(self):
        # Namespaces for the instance layer
        instance_vocab = 'http://cltl.nl/leolani/n2mu/'
        self.namespaces['N2MU'] = Namespace(instance_vocab)
        instance_resource = 'http://cltl.nl/leolani/world/'
        self.namespaces['LW'] = Namespace(instance_resource)

        # Namespaces for the mention layer
        mention_vocab = 'http://groundedannotationframework.org/gaf#'
        self.namespaces['GAF'] = Namespace(mention_vocab)
        mention_resource = 'http://cltl.nl/leolani/talk/'
        self.namespaces['LTa'] = Namespace(mention_resource)

        # Namespaces for the attribution layer
        attribution_vocab = 'http://groundedannotationframework.org/grasp#'
        self.namespaces['GRASP'] = Namespace(attribution_vocab)
        attribution_resource = 'http://cltl.nl/leolani/friends/'
        self.namespaces['LF'] = Namespace(attribution_resource)

        # Namespaces for the temporal layer-ish
        time_vocab = 'http://www.w3.org/TR/owl-time/#'
        self.namespaces['TIME'] = Namespace(time_vocab)
        time_resource = 'http://cltl.nl/leolani/date/'
        self.namespaces['LTi'] = Namespace(time_resource)

        # The namespaces of external ontologies
        skos = 'http://www.w3.org/2004/02/skos/core#'
        self.namespaces['SKOS'] = Namespace(skos)

        prov = 'http://www.w3.org/ns/prov#'
        self.namespaces['PROV'] = Namespace(prov)

        sem = 'http://semanticweb.cs.vu.nl/2009/11/sem/'
        self.namespaces['SEM'] = Namespace(sem)

        xml = 'https://www.w3.org/TR/xmlschema-2/#'
        self.namespaces['XML'] = Namespace(xml)

    def __get_ontology_path__(self):
        self.ontology_paths['n2mu'] = './../../knowledge_representation/ontologies/leolani.ttl'
        self.ontology_paths['gaf'] = './../../knowledge_representation/ontologies/gaf.rdf'
        self.ontology_paths['grasp'] = './../../knowledge_representation/ontologies/grasp.rdf'
        self.ontology_paths['sem'] = './../../knowledge_representation/ontologies/sem.rdf'

    def __bind_namespaces__(self):
        self.dataset.bind('n2mu', self.namespaces['N2MU'])
        self.dataset.bind('leolaniWorld', self.namespaces['LW'])
        self.dataset.bind('gaf', self.namespaces['GAF'])
        self.dataset.bind('leolaniTalk', self.namespaces['LTa'])
        self.dataset.bind('grasp', self.namespaces['GRASP'])
        self.dataset.bind('leolaniFriends', self.namespaces['LF'])
        self.dataset.bind('time', self.namespaces['TIME'])
        self.dataset.bind('leolaniTime', self.namespaces['LTi'])
        self.dataset.bind('skos', self.namespaces['SKOS'])
        self.dataset.bind('prov', self.namespaces['PROV'])
        self.dataset.bind('sem', self.namespaces['SEM'])
        self.dataset.bind('xml', self.namespaces['XML'])

        self.dataset.bind('owl', OWL)

        # self.dataset.default_context.parse(self.ontology_paths['n2mu'], format='turtle')

    def __serialize__(self, file_path):
        format = 'trig'

        # Save to file but return the python representation
        with open(file_path+format, 'w') as f:
            self.dataset.serialize(f, format=format)

        return self.dataset.serialize(format=format)

    def __upload_to_brain__(self, data):
        if self.debug:
            print("Posting triples")

        # From serialized string
        post_url = self.address + "/statements"
        response = requests.post(post_url,
                                 data=data,
                                 headers={'Content-Type': 'application/x-trig'})

        return str(response.status_code)

    def _paradiso_simple_model_(self, parsed_statement):
        # Instance graph
        instance_graph_uri = URIRef(to_iri(self.namespaces['LW'] + 'instances'))
        instance_graph = self.dataset.graph(instance_graph_uri)

        # Create Leolani
        leolani_id = 'Leolani'
        leolani_label = 'Leolani'

        leolani = URIRef(to_iri(self.namespaces['LW'] + leolani_id))
        leolani_label = Literal(leolani_label)
        leolani_type1 = URIRef(to_iri(self.namespaces['N2MU'] + 'ROBOT'))
        leolani_type2 = URIRef(to_iri(self.namespaces['GAF'] + 'Instance'))

        instance_graph.add((leolani, RDFS.label, leolani_label))
        instance_graph.add((leolani, RDF.type, leolani_type1))
        instance_graph.add((leolani, RDF.type, leolani_type2))

        # Subject
        if parsed_statement['subject']['type'] == '':  # We only get the label
            subject_id = parsed_statement['subject']['label']
            subject_label = parsed_statement['subject']['label']
            subject_vocab = OWL
            subject_type = 'Thing'
        else:
            subject_id = parsed_statement['subject']['label']
            subject_label = parsed_statement['subject']['label']
            subject_vocab = self.namespaces['N2MU']
            subject_type = parsed_statement['subject']['type']

        subject = URIRef(to_iri(self.namespaces['LW'] + subject_id))
        subject_label = Literal(subject_label)
        subject_type1 = URIRef(to_iri(subject_vocab + subject_type))
        subject_type2 = URIRef(to_iri(self.namespaces['GAF'] + 'Instance'))

        instance_graph.add((subject, RDFS.label, subject_label))
        instance_graph.add((subject, RDF.type, subject_type1))
        instance_graph.add((subject, RDF.type, subject_type2))

        # Object
        if parsed_statement['object']['type'] == '':  # We only get the label
            object_id = parsed_statement['object']['label']
            object_label = parsed_statement['object']['label']
            object_vocab = OWL
            object_type = 'Thing'
        else:
            object_id = parsed_statement['object']['label']
            object_label = parsed_statement['object']['label']
            object_vocab = self.namespaces['N2MU']
            object_type = parsed_statement['object']['type']

        object = URIRef(to_iri(self.namespaces['LW'] + object_id))
        object_label = Literal(object_label)
        object_type1 = URIRef(to_iri(object_vocab + object_type))
        object_type2 = URIRef(to_iri(self.namespaces['GAF'] + 'Instance'))

        instance_graph.add((object, RDFS.label, object_label))
        instance_graph.add((object, RDF.type, object_type1))
        instance_graph.add((object, RDF.type, object_type2))

        # Predicate
        predicate = parsed_statement['predicate']['type'].replace(" ", "_")

        # Statement

        # Create hashed id from name for this statement
        statement_id = hash_id([parsed_statement['subject']['label'], parsed_statement['predicate']['type'], parsed_statement['object']['label']])
        statement = URIRef(to_iri(self.namespaces['LW'] + statement_id))
        statement_type1 = URIRef(to_iri(self.namespaces['GRASP'] + 'Statement'))
        statement_type2 = URIRef(to_iri(self.namespaces['GAF'] + 'Instance'))

        # Create graph and add triple
        graph = self.dataset.graph(statement)
        graph.add((subject, self.namespaces['N2MU'][predicate], object))

        instance_graph.add((statement, RDF.type, statement_type1))
        instance_graph.add((statement, RDF.type, statement_type2))

        # Time
        date = parsed_statement["date"]
        time = URIRef(to_iri(self.namespaces['LTi'] + str(date.isoformat())))
        time_type = URIRef(to_iri(self.namespaces['TIME'] + 'DateTimeDescription'))
        day = Literal(date.day, datatype=self.namespaces['XML']['gDay'])
        month = Literal(date.month, datatype=self.namespaces['XML']['gMonthDay'])
        year = Literal(date.year, datatype=self.namespaces['XML']['gYear'])
        time_unitType = URIRef(to_iri(self.namespaces['TIME'] + 'unitDay'))

        self.dataset.add((time, RDF.type, time_type))
        self.dataset.add((time, self.namespaces['TIME']['day'], day))
        self.dataset.add((time, self.namespaces['TIME']['month'], month))
        self.dataset.add((time, self.namespaces['TIME']['year'], year))
        self.dataset.add((time, self.namespaces['TIME']['unitType'], time_unitType))

        # Actor
        actor_id = parsed_statement['author']
        actor_label = parsed_statement['author']

        actor = URIRef(to_iri(to_iri(self.namespaces['LF'] + actor_id)))
        actor_label = Literal(actor_label)
        actor_type1 = URIRef(to_iri(self.namespaces['SEM'] + 'Actor'))
        actor_type2 = URIRef(to_iri(self.namespaces['GAF'] + 'Instance'))

        instance_graph.add((actor, RDFS.label, actor_label))
        instance_graph.add((actor, RDF.type, actor_type1))
        instance_graph.add((actor, RDF.type, actor_type2))

        # Add leolani knows actor
        instance_graph.add((leolani, self.namespaces['N2MU']['knows'], actor))

        # Chat and turn
        chat_id = 'chat%s' % parsed_statement['chat']
        turn_id = chat_id + '_turn%s' % parsed_statement['turn']
        turn = URIRef(to_iri(self.namespaces['LTa'] + turn_id))
        turn_type = URIRef(to_iri(self.namespaces['SEM'] + 'Event'))

        self.dataset.add((turn, RDF.type, turn_type))
        self.dataset.add((turn, self.namespaces['SEM']['hasActor'], actor))
        self.dataset.add((turn, self.namespaces['SEM']['hasTime'], time))

        chat = URIRef(to_iri(self.namespaces['LTa'] + chat_id))
        chat_type = URIRef(to_iri(self.namespaces['SEM'] + 'Event'))

        self.dataset.add((chat, RDF.type, chat_type))
        self.dataset.add((chat, self.namespaces['SEM']['hasActor'], actor))
        self.dataset.add((chat, self.namespaces['SEM']['hasSubevent'], turn))
        self.dataset.add((chat, self.namespaces['SEM']['hasTime'], time))

        # Perspective graph
        perspective_graph_uri = URIRef(to_iri(self.namespaces['LTa'] + 'perspectives'))
        perspective_graph = self.dataset.graph(perspective_graph_uri)

        # Mention
        mention_id = turn_id + '_char%s' % parsed_statement['position']
        mention = URIRef(to_iri(self.namespaces['LTa'] + mention_id))
        mention_type = URIRef(to_iri(self.namespaces['GAF'] + 'Mention'))

        perspective_graph.add((mention, RDF.type, mention_type))

        # Attribution
        attribution_id = mention_id + '_CERTAIN'
        attribution = URIRef(to_iri(self.namespaces['LTa'] + attribution_id))
        attribution_type = URIRef(to_iri(self.namespaces['GRASP'] + 'Attribution'))
        attribution_value = URIRef(to_iri(self.namespaces['GRASP'] + 'CERTAIN'))

        perspective_graph.add((attribution, RDF.type, attribution_type))
        perspective_graph.add((attribution, RDF.value, attribution_value))

        # Interconnections
        instance_graph.add((subject, self.namespaces['GAF']['denotedIn'], mention))
        instance_graph.add((object, self.namespaces['GAF']['denotedIn'], mention))
        instance_graph.add((statement, self.namespaces['GRASP']['denotedBy'], mention))

        perspective_graph.add((mention, self.namespaces['GAF']['containsDenotation'], subject))
        perspective_graph.add((mention, self.namespaces['GAF']['containsDenotation'], object))
        perspective_graph.add((mention, self.namespaces['GAF']['denotes'], statement))
        perspective_graph.add((mention, self.namespaces['GRASP']['wasAttributedTo'], actor))
        perspective_graph.add((mention, self.namespaces['GRASP']['hasAttribution'], attribution))

        perspective_graph.add((attribution, self.namespaces['GRASP']['isAttributionFor'], mention))

    def update(self, parsed_statement):
        # Paradiso use case
        self._paradiso_simple_model_(parsed_statement)

        data = self.__serialize__('./../../knowledge_representation/brainOutput/learned_facts.')

        code = self.__upload_to_brain__(data)

        # Create JSON output
        parsed_statement["date"] = str(parsed_statement["date"])
        output = {'response': code, 'statement': parsed_statement}

        return output

    def _create_query_(self, parsed_question):
        _ = hash_id([parsed_question['subject']['label'], parsed_question['predicate']['type'], parsed_question['object']['label']])

        # Query subject
        if parsed_question['subject']['label'] == "":
            query = """
                SELECT ?slabel ?authorlabel
                        WHERE { 
                            ?s n2mu:%s ?o . 
                            ?s rdfs:label ?slabel . 
                            ?o rdfs:label '%s' .  
                            GRAPH ?g {
                                ?s n2mu:%s ?o . 
                            } . 
                            ?g grasp:denotedBy ?m . 
                            ?m grasp:wasAttributedTo ?author . 
                            ?author rdfs:label ?authorlabel .
                        }
                """ % (parsed_question['predicate']['type'],
                       parsed_question['object']['label'],
                       parsed_question['predicate']['type'])

        # Query object
        elif parsed_question['object']['label'] == "":
            query = """
                SELECT ?olabel ?authorlabel
                        WHERE { 
                            ?s n2mu:%s ?o .   
                            ?s rdfs:label '%s' .  
                            ?o rdfs:label ?olabel .  
                            GRAPH ?g {
                                ?s n2mu:%s ?o . 
                            } . 
                            ?g grasp:denotedBy ?m . 
                            ?m grasp:wasAttributedTo ?author . 
                            ?author rdfs:label ?authorlabel .
                        }
                """ % (parsed_question['predicate']['type'],
                       parsed_question['subject']['label'],
                       parsed_question['predicate']['type'])

        # Query existence
        else:
            query = """
                SELECT ?authorlabel ?v
                        WHERE { 
                            ?s n2mu:%s ?o .   
                            ?s rdfs:label '%s' .  
                            ?o rdfs:label '%s' .  
                            GRAPH ?g {
                                ?s n2mu:%s ?o . 
                            } . 
                            ?g grasp:denotedBy ?m . 
                            ?m grasp:wasAttributedTo ?author . 
                            ?author rdfs:label ?authorlabel .
                            ?m grasp:hasAttribution ?att .
                            ?att rdf:value ?v .
                        }
                """ % (parsed_question['predicate']['type'],
                       parsed_question['subject']['label'],
                       parsed_question['object']['label'],
                       parsed_question['predicate']['type'])

        query = self.query_prefixes + query

        return query

    def _submit_query_(self, query):
        # Set up connection
        sparql = SPARQLWrapper(self.address)

        # Response parameters
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        sparql.addParameter('Accept', 'application/sparql-results+json')
        response = sparql.query().convert()

        return response

    def query_brain(self, parsed_question):
        """
        Get features from query, such as keywords (relevance,text) and entities

        Parameters
        ----------
        query: str
            Query to be executed in the knowledge store

        Returns
        -------
        result: json
            Analysis of the query
        """

        # Generate query
        query = self._create_query_(parsed_question)

        # Perform query
        response = self._submit_query_(query)

        # Create JSON output
        if 'date' in parsed_question.keys():
            parsed_question["date"] = str(parsed_question["date"])
        output = {'response': response["results"]["bindings"], 'question': parsed_question}

        return output

    def get_last_chat_id(self):
        query = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX sem: <http://semanticweb.cs.vu.nl/2009/11/sem/>
    
            select ?s where { 
            ?s rdf:type sem:Event .
            FILTER(!regex(str(?s), "turn")) .
            }
        """

        response = self._submit_query_(query)

        last_chat = 0
        for chat in response['results']['bindings']:
            chat_uri = chat['s']['value']
            chat_id = chat_uri.split('/')[-1][4:]
            chat_id = int(chat_id)

            if chat_id > last_chat:
                last_chat = chat_id

        return last_chat

    def get_last_turn_id(self, chat_id):
        query = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX sem: <http://semanticweb.cs.vu.nl/2009/11/sem/>

            select ?s where { 
            ?s rdf:type sem:Event .
            FILTER(regex(str(?s), "chat%s_turn")) .
            }
        """ % chat_id

        response = self._submit_query_(query)

        last_turn = 0
        for turn in response['results']['bindings']:
            turn_uri = turn['s']['value']
            turn_id = turn_uri.split('/')[-1][10:]
            turn_id = int(turn_id)

            if turn_id > last_turn:
                last_turn = turn_id

        return last_turn


def hash_id(triple):
    print('This is the triple: {}'.format(triple))
    temp = '_'.join(triple)
    temp.replace(" ", "_")

    # hashids = Hashids(min_length=10)
    # id = hashids.encode(temp)

    return temp


if __name__ == "__main__":
    # Create brain connection
    brain = TheoryOfMind()

    # Test statements
    # for statement in statements:
    #     response = brain.update(statement)
    #     print(json.dumps(response, indent=4, sort_keys=True))
    #
    # # Separation
    # print('#######################################################')
    #
    # # Test questions
    # for question in questions:
    #     response = brain.query_brain(question)
    #     print(json.dumps(response, indent=4, sort_keys=True))

    id = brain.get_last_turn_id(1)
    print('\n%s' % id)
