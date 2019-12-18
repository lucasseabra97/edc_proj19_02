from django.shortcuts import render
import json
import requests
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient

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


def country(request):
    name = request.GET.get('name')

    query = """PREFIX country:<http://edc_2019.org/country/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX pred: <http://edc_2019.org/pred/>

            SELECT *
            {   ?country rdf:type country:.
                ?country pred:name  \"""" + name + """\".
                ?country ?key ?value.
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

    url = 'https://query.wikidata.org/sparql'
    wiki_query = """SELECT *
                    WHERE
                    {
                    wd:""" + tmp[0]['id'] + """ p:P1279 ?p .
                    ?p pq:P585 ?year ;
                        ps:P1279 ?var .
                    }order by ?year"""
    print(tmp[0]['id'])
    r = requests.get(url, params = {'format': 'json', 'query': wiki_query})
    data = r.json()['results']['bindings']
    chartData = {}
    for d in data:
        chartData[d['year']['value']] = d['var']['value']

    print(chartData)
    return render(request, 'country.html',  {
        'tmp': tmp[0],
        'title': 'INFLATION EVOLUTION',
        'type': 'line',
        'data' : json.dumps(chartData)
    })


def pib(request):
    query = """ PREFIX country:<http://edc_2019.org/country/>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX pred: <http://edc_2019.org/pred/>

                SELECT *
                {
                    ?country rdf:type country:.
                    ?country pred:pib ?pib.
                    ?country pred:name ?name.
                    OPTIONAL {?country pred:flag ?flag.}
                    OPTIONAL {?country pred:plate ?plate.}
                }order by desc(xsd:double(?pib))
            """

    tmp = parseQuery(query)
    chartData ={}
    for t in tmp:
        chartData[t['name']] = t['pib']
    return render(request, 'pib.html',  {
        'tmp': tmp,
        'data': json.dumps(chartData),
        'title': 'PIB',
        'type': 'bar'
    })

def area(request):
    query = """ PREFIX country:<http://edc_2019.org/country/>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX pred: <http://edc_2019.org/pred/>

                SELECT *
                {
                    ?country rdf:type country:.
                    ?country pred:area ?area.
                    ?country pred:name ?name.
                    OPTIONAL {?country pred:flag ?flag.}
                    OPTIONAL {?country pred:plate ?plate.}
                }order by desc(xsd:double(?area))
            """

    tmp = parseQuery(query)

    return render(request, 'area.html',  {
        'tmp': tmp
    })

def populacao(request):
    query = """ PREFIX country:<http://edc_2019.org/country/>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX pred: <http://edc_2019.org/pred/>

                SELECT *
                {
                    ?country rdf:type country:.
                    ?country pred:pop ?populacao.
                    ?country pred:name ?name.
                    ?country pred:life ?life_expectancy
                    OPTIONAL {?country pred:flag ?flag.}
                    OPTIONAL {?country pred:plate ?plate.}
                }order by desc(xsd:double(?populacao))
            """

    tmp = parseQuery(query)

    return render(request, 'populacao.html',  {
        'tmp': tmp
    })

def inflacao(request):
    query = """ PREFIX country:<http://edc_2019.org/country/>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX pred: <http://edc_2019.org/pred/>

                SELECT *
                {
                    ?country rdf:type country:.
                    ?country pred:inflation ?inflacao.
                    ?country pred:name ?name.
                    OPTIONAL {?country pred:flag ?flag.}
                    OPTIONAL {?country pred:plate ?plate.}
                }order by desc(xsd:double(?inflacao))
            """

    tmp = parseQuery(query)

    return render(request, 'inflacao.html',  {
        'tmp': tmp
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
        #divide value by million
        pop[r['name']['value']] = str(int(r['value']['value']) / 1000000)

    
    return render(request, 'teste.html', {'data': json.dumps(pop),
                                            'title': "Top 20 Populations (in Millions)"})

    
def parseQuery(query):
    payload_query = {"query": query}
    res = json.loads(accessor.sparql_select(body=payload_query, repo_name=repo_name))['results']['bindings']
    
    countries = {}

    for c in res:
        tmp = c['country']['value'].replace('http://edc_2019.org/country/', '')
        countries[tmp] = {}
        keys = c.keys()
        for k in keys:
            countries[tmp][k] = c[k]['value']

    tmp = list(map(lambda x: {
        'id': x,
        **countries[x]
    },list(countries)))

    return tmp