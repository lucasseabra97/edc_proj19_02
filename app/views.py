from django.shortcuts import render

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