import requests
import json

import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient

url = 'https://query.wikidata.org/sparql'
endpoint = "http://localhost:7200"
repo_name = "edc_2019"
client = ApiClient(endpoint=endpoint)
accessor = GraphDBApi(client)

query = """
    SELECT  ?country (SAMPLE(?plate) as ?plate) 
            (SAMPLE(?flag) as ?flag) (SAMPLE(?name) as ?name) 
            (SAMPLE(?localtime) as ?localtime) (SAMPLE(?population) as ?population) (SAMPLE(?life) as ?life) 
            (SAMPLE(?location) as ?location) (SAMPLE(?capital) as ?capital)
            (SAMPLE(?inflation) as ?inflation) (SAMPLE(?area) as ?area)
            (SAMPLE(?currency) as ?currency) (SAMPLE(?pib) as ?pib) 
    WHERE
    {
        ?country wdt:P31 wd:Q6256;
                wdt:P41 ?flag;
                wdt:P1448 ?name;
        OPTIONAL { ?country wdt:P395 ?plate }
        OPTIONAL { ?country wdt:P421 ?localtime }
        OPTIONAL { ?country wdt:P1082 ?population }
        OPTIONAL { ?country wdt:P2250 ?life }
        OPTIONAL { ?country wdt:P242 ?location }
        OPTIONAL { ?country wdt:P1279 ?inflation }
        OPTIONAL { ?country wdt:P2046 ?area }
        OPTIONAL { ?country wdt:P38 ?currency }
        OPTIONAL { ?country wdt:P2219 ?pib }
        OPTIONAL { ?country wdt:P36 ?capital }.
    } 
    GROUP BY(?country)
"""

r = requests.get(url, params = {'format': 'json', 'query': query})
data = r.json()['results']['bindings']

i = 0
for d in data:

    id = d['country']['value'].split('/')[-1]
    del d['country']

    predicates = []
    string = ""
    for pred in d:
        string += ":{0} :{1} '{2}'.\n".format(id, pred, d[pred]['value'])
    print(string)

    query = """
        PREFIX : <http://countries.org/edc#/>
        DELETE WHERE {{ 
            :{0} ?pred ?val 
        }};
        INSERT DATA {{
            {1}
        }}
    """.format(id, string)
    print(query)

    payload_query = {"update": query}
    res = accessor.sparql_update(body=payload_query, repo_name=repo_name)