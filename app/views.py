from django.shortcuts import render
import json
import requests
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient

# Create your views here.

def landing(request):
    return render(request, 'landing.html', {
        
    })

def teste(request):
    endpoint = "http://localhost:7200"
    repo_name = "edc_2019"
    client = ApiClient(endpoint=endpoint)
    accessor = GraphDBApi(client)

    query = """ PREFIX : <http://countries.org/edc#/>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                select ?value ?name where { 
                    ?country :pop ?value.
                    ?country :name ?name.
                } order by desc(xsd:integer(?value)) limit 20
"""

    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
    res = json.loads(res)
    pop = {}
    for r in res['results']['bindings']:
        #divide value by million to get them in millions
        pop[r['name']['value']] = str(int(r['value']['value']) / 1000000)

    
    return render(request, 'teste.html', {'data': json.dumps(pop),
                                            'title': "Top 20 Populations (in Millions)"})
    