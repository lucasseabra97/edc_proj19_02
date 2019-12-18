from django.shortcuts import render
import json
import requests
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
import math

endpoint = "http://localhost:7200"
repo_name = "edc_2019"
client = ApiClient(endpoint=endpoint)
accessor = GraphDBApi(client)

# Create your views here.
def isInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def landing(request):

    limit = 20
    page = int(request.GET.get('page')) if request.GET.get('page') else 1
    order = request.GET.get('order') or 'name'

    query = """
        PREFIX country:<http://edc_2019.org/country/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT  
        *
        WHERE
        {
            ?country rdf:type country:.
        } 
    """

    payload_query = {"query": query}
    size = len(json.loads(accessor.sparql_select(body=payload_query, repo_name=repo_name))['results']['bindings'])

    query = """
        PREFIX country:<http://edc_2019.org/country/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX pred: <http://edc_2019.org/pred/>

        SELECT  
        ?country ?plate 
        ?flag ?name 
        ?localtime ?population ?life 
        ?location ?capital
        ?inflation ?area
        ?currency ?pib 
        WHERE
        {{
         ?country rdf:type country:.
            OPTIONAL {{ ?country rdf:type country:. }}
            OPTIONAL {{ ?country pred:flag ?flag. }}
            OPTIONAL {{ ?country pred:name ?name. }}
            OPTIONAL {{ ?country pred:plate ?plate. }}
            OPTIONAL {{ ?country pred:currency ?currency. }}
            OPTIONAL {{ ?country pred:pop ?population. }}
            OPTIONAL {{ ?country pred:area ?area. }}
            OPTIONAL {{ ?country pred:inflation ?inflation. }}
            OPTIONAL {{ ?country pred:pib ?pib. }}
        }}
        ORDER BY {2}
        OFFSET {0}
        LIMIT {1}
    """.format((page - 1) * limit, limit, 'DESC(xsd:float(?{}))'.format(order) if (order in ['area', 'population', 'inflation', 'pib']) else '?' + order)

    payload_query = {"query": query}
    res = json.loads(accessor.sparql_select(body=payload_query, repo_name=repo_name))['results']['bindings']

    maxPage = math.ceil(size / limit)

    pages = [i+1 for i in range(maxPage)]
    left = [i for i in pages if page - i < 4 and i < page]
    right = [i for i in pages if i - page < 4 and i > page]

    print(left, right)

    return render(request, 'landing.html', {
        'table_order': ['plate', 'name', 'currency', 'population', 'area', 'inflation', 'pib'],
        'countries': res,
        'size': size,
        'left': left,
        'right': right,
        'page': page,
        'maxPage': maxPage,
        'showMax': (maxPage - page) >= 4,
        'showMin': page >= 4,
        'limit': limit,
    })


def country(request):
    name = request.GET.get('name')
    print(name)

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

    return render(request, 'country.html',  {
        'tmp': tmp[0]
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
        'title': 'PIB'
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