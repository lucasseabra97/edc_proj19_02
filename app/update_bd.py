import requests
import json
import re
import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient

url = 'https://query.wikidata.org/sparql'
endpoint = "http://localhost:7200"
repo_name = "edc_2019"
client = ApiClient(endpoint=endpoint)
accessor = GraphDBApi(client)

# APAGAR BD
query = """
    DELETE WHERE {{ 
        ?c ?d ?p
    }};
"""

payload_query = {"update": query}
res = accessor.sparql_update(body=payload_query, repo_name=repo_name)

# ADICIONAR PAISES
query = """
SELECT  ?country (SAMPLE(?plate) as ?plate) 
(SAMPLE(?flag) as ?flag) (SAMPLE(?name) as ?name) 
(SAMPLE(?localtime) as ?localtime) (SAMPLE(?population) as ?population) (SAMPLE(?life) as ?life) 
(SAMPLE(?location) as ?location) (SAMPLE(?capital) as ?capital) (SAMPLE(?president) as ?president) 
(SAMPLE(?inflation) as ?inflation) (SAMPLE(?area) as ?area) 
(SAMPLE(?currency) as ?currency) (SAMPLE(?pib) as ?pib) 
WHERE
{
  ?country wdt:P31 wd:Q6256;
           wdt:P41 ?flag;
           wdt:P1448 ?name;
  OPTIONAL { ?country wdt:P395 ?plate }
  OPTIONAL { 
    ?country wdt:P421 ?localtmp.
    ?localtmp wdt:P373 ?localtime
  }
  OPTIONAL { ?country wdt:P1082 ?population }
  OPTIONAL { ?country wdt:P2250 ?life }
  OPTIONAL { ?country wdt:P242 ?location }
  OPTIONAL { ?country wdt:P1279 ?inflation }
  OPTIONAL { ?country wdt:P2046 ?area }
  OPTIONAL { 
    ?country wdt:P38 ?currencytmp.
    ?currencytmp wdt:P498 ?currency
  }.
  OPTIONAL { ?country wdt:P2219 ?pib }
  OPTIONAL { ?country wdt:P36 ?capital. }.
  OPTIONAL { 
      ?country wdt:P1906 ?presidenttmp. 
      ?presidenttmp wdt:P1308 ?president
    }.
} 
GROUP BY(?country)
"""

r = requests.get(url, params = {'format': 'json', 'query': query})
data = r.json()['results']['bindings']

i = 0
for d in data:

    i += 1
    name = d['flag']['value'].replace(".svg","").split('/')[-1:] 
    name = [re.sub('[0-9]', '', i) for i in name] 
    name = (name[0].replace("Flagof","").split("%"))
    stri =""
    name = [i for i in name[2:] if len(i)>2 and i != "the" ]
    for y in name:
        if y[0].isupper():
            stri += y + " "
    d['name']['value']=stri



    id = d['country']['value'].split('/')[-1]
    del d['country']

    predicates = []
    string = ""
    for pred in d:
        if pred == 'capital':
            string += "country:{0} pred:capital capital:{2}.\n".format(id, pred, d[pred]['value'].split('/')[-1])
        elif pred == 'president':
            string += "country:{0} pred:president president:{2}.\n".format(id, pred, d[pred]['value'].split('/')[-1])
        elif pred == 'pop':
            string += "country:{0} pred:population '{2}'.\n".format(id, pred, d[pred]['value'])
        else:
            string += "country:{0} pred:{1} '{2}'.\n".format(id, pred, d[pred]['value'])

    print(string)

    query = """
        PREFIX country:<http://edc_2019.org/country/>
        PREFIX president:<http://edc_2019.org/president/>
        PREFIX capital:<http://edc_2019.org/capital/>
        PREFIX pred:<http://edc_2019.org/pred/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX wikidata:<http://www.wikidata.org/entity/>
        INSERT DATA {{
            \t\t{1}
            country:{0} rdf:type wikidata:.
            country:{0} rdf:type country:.
        }}
    """.format(id, string)

    print(query)

    payload_query = {"update": query}
    res = accessor.sparql_update(body=payload_query, repo_name=repo_name)

# ADICIONAR CAPITAIS

query = """
SELECT  (SAMPLE(?capital) as ?capital) (SAMPLE(?img) as ?img) (SAMPLE(?name) as ?name) (SAMPLE(?population) as ?population)  (SAMPLE(?area) as ?area)
WHERE
{
    ?country wdt:P31 wd:Q6256;
             wdt:P41 ?flag;
             wdt:P1448 ?countryName.
    ?country wdt:P36 ?capital.
    OPTIONAL { ?capital wdt:P18 ?img }
    OPTIONAL { ?capital wdt:P1448 ?name }
    OPTIONAL { ?capital wdt:P1082 ?population }
    OPTIONAL { ?capital wdt:P2046 ?area }
} 
GROUP BY ?country
"""

r = requests.get(url, params = {'format': 'json', 'query': query})
data = r.json()['results']['bindings']

i = 0
for d in data:

    i += 1

    id = d['capital']['value'].split('/')[-1]
    del d['capital']

    predicates = []
    string = ""
    for pred in d:
        string += "capital:{0} pred:{1} '{2}'.\n".format(id, pred, d[pred]['value'])

    print(string)

    query = """
        PREFIX country:<http://edc_2019.org/country/>
        PREFIX capital:<http://edc_2019.org/capital/>
        PREFIX pred:<http://edc_2019.org/pred/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX wikidata:<http://www.wikidata.org/entity/>
        INSERT DATA {{
            \t\t{1}
            capital:{0} rdf:type wikidata:.
            capital:{0} rdf:type capital:.
        }}
    """.format(id, string)

    print(query)

    payload_query = {"update": query}
    res = accessor.sparql_update(body=payload_query, repo_name=repo_name)

# ADICIONAR PRESIDENTES

query = """
SELECT  (SAMPLE(?president) as ?president) (SAMPLE(?name) as ?name) (SAMPLE(?Image) as ?Image)
WHERE
{
    ?country wdt:P31 wd:Q6256;
             wdt:P41 ?flag;
             wdt:P1448 ?countryName.
    ?country wdt:P35 ?president.
    OPTIONAL { ?president wdt:P1559 ?name }
    OPTIONAL { ?president wdt:P18 ?Image }
}
GROUP BY ?country
"""

r = requests.get(url, params = {'format': 'json', 'query': query})
data = r.json()['results']['bindings']

i = 0
for d in data:

    i += 1

    id = d['president']['value'].split('/')[-1]
    del d['president']

    predicates = []
    string = ""
    for pred in d:
        string += "president:{0} foaf:{1} '{2}'.\n".format(id, pred, d[pred]['value'])

    print(string)

    query = """
        PREFIX country:<http://edc_2019.org/country/>
        PREFIX president:<http://edc_2019.org/president/>
        PREFIX foaf:<http://xmlns.com/foaf/0.1/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX wikidata:<http://www.wikidata.org/entity/>
        INSERT DATA {{
            \t\t{1}
            president:{0} rdf:type wikidata:.
            president:{0} rdf:type president:.
            president:{0} rdf:type foaf:Person.
        }}
    """.format(id, string)

    print(query)

    payload_query = {"update": query}
    res = accessor.sparql_update(body=payload_query, repo_name=repo_name)