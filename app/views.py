from django.shortcuts import render
import json
import requests
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient

from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
import json

endpoint = "http://localhost:7200"
repo_name = "edc_2019"
client = ApiClient(endpoint=endpoint)
accessor = GraphDBApi(client)

# Create your views here.

def landing(request):

    query = """
        PREFIX country:<http://edc_2019.org/country/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT *
        {
            ?country rdf:type country:.
            ?country ?key ?value
        }
    """

    payload_query = {"query": query}
    res = json.loads(accessor.sparql_select(body=payload_query, repo_name=repo_name))['results']['bindings']
    
    countries = {}

    for d in res:
        tmp = d['country']['value'].replace('http://edc_2019.org/country/', '')
        if tmp not in countries:
            countries[tmp] = {}
        countries[tmp][d['key']['value'].replace('http://edc_2019.org/pred/', '').replace('http://www.w3.org/1999/02/22-rdf-syntax-ns#type', 'type')] = d['value']['value']


    tmp = list(map(lambda x: {
        'id': x,
        **countries[x]
    },list(countries)))

    #print(tmp)

    return render(request, 'landing.html', {
        'tmp': tmp,
    })

def teste(request):
    endpoint = "http://localhost:7200"
    repo_name = "edc_2019"
    client = ApiClient(endpoint=endpoint)
    accessor = GraphDBApi(client)

    query = """ PREFIX : <http://www.semwebtech.org/mondial/10/meta#>
                select ?country ?value ?name where { 
                    ?country :population ?value.
                    ?country :name ?name.
                    ?country rdf:type :Country.
                } order by desc(?value) limit 20
"""

    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
    res = json.loads(res)
    pop = {}
    for r in res['results']['bindings']:
        #divide value by million to get them in millions
        pop[r['name']['value']] = str(int(r['value']['value']) / 1000000)

    
    return render(request, 'teste.html', {'data': json.dumps(pop),
                                            'title': "Top 20 Populations"})
    
