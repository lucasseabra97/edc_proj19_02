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
SELECT ?country  ?plate ?name
WHERE
{
  ?country wdt:P31 wd:Q6256;
           wdt:P395 ?plate;
           wdt:P1448 ?name.
}
"""
r = requests.get(url, params = {'format': 'json', 'query': query})
data = r.json()
data = list(map(lambda x: [x['name']['value'], x['country']['value'].split('/')[-1], x['plate']['value']] ,  data['results']['bindings']))

i = 0
for d in data:

    query = """
        PREFIX : <http://www.semwebtech.org/mondial/10/meta#>  
        INSERT {{  
            ?country :wiki "{0}" .
        }}
        WHERE {{
            ?country :carCode "{1}" .
        }};
    """.format(d[1], d[2])

    i += 1

    payload_query = {"update": query}
    res = accessor.sparql_update(body=payload_query, repo_name=repo_name)