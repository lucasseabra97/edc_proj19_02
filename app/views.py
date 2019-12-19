from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest
from django.shortcuts import render
import json
import requests
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
import math
from django.views.decorators.csrf import csrf_exempt

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

def logReg(request):
    return render(request, "logReg.html", {})

@csrf_exempt
def register(request):
    new_user = request.body.decode()
    user = new_user.split('&')[0].split('=')[1]
    passwd = new_user.split('&')[1].split('=')[1]

    query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX pred: <http://edc_2019.org/pred/>
        select ?user ?pass where {
            ?user rdf:type foaf:Person.
            ?user pred:password ?pass
        }
    """
    payload_query = {"query": query}
    res = json.loads(accessor.sparql_select(body=payload_query, repo_name=repo_name))
    
    tmp = {}
    for r in res['results']['bindings']:
        tmp[r['user']['value'].split('/')[-1]] = r['pass']['value']
    
    if user in tmp:
        return HttpResponse(status = 400)
    else:
        query = """
        PREFIX user:<http://edc_2019.org/user/>
        PREFIX pred:<http://edc_2019.org/pred/>
        PREFIX foaf:<http://xmlns.com/foaf/0.1/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        INSERT DATA {{
            user:{0} pred:password \"{1}\";
                    rdf:type foaf:Person.
        }}
        """.format(user, passwd)

        payload_query = {"update": query}
        res = accessor.sparql_update(body=payload_query, repo_name=repo_name)

        return HttpResponse(status = 200)

@csrf_exempt
def login(request):
    log_user = request.body.decode()
    user = log_user.split('&')[0].split('=')[1]
    passwd = log_user.split('&')[1].split('=')[1]

    query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX pred: <http://edc_2019.org/pred/>
        select ?user ?pass where {
            ?user rdf:type foaf:Person.
            ?user pred:password ?pass
        }
    """
    payload_query = {"query": query}
    res = json.loads(accessor.sparql_select(body=payload_query, repo_name=repo_name))
    
    tmp = {}
    for r in res['results']['bindings']:
        tmp[r['user']['value'].split('/')[-1]] = r['pass']['value']
    
    if user in tmp:
        if passwd == tmp[user]:
            return HttpResponse(status = 200)
    else:
        return HttpResponse(status = 400)

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
        ?localtime ?population
        ?location
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
            OPTIONAL {{ ?country pred:population ?population. }}
            OPTIONAL {{ ?country pred:localtime ?localtime. }}
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
        'table_order': ['plate', 'name', 'localtime', 'currency', 'population', 'area', 'inflation', 'pib'],
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
    id = request.GET.get('id')

    query = """
        PREFIX country:<http://edc_2019.org/country/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX pred: <http://edc_2019.org/pred/>

        SELECT  
        ?plate 
        ?flag ?name 
        ?localtime ?population 
        ?location ?life 
        ?inflation ?area
        ?currency ?pib 
        ?capital ?capitalName ?capitalArea ?capitalPopulation ?capitalImg
        WHERE
        {{
            OPTIONAL {{ country:{0} rdf:type country:. }}
            OPTIONAL {{ country:{0} pred:flag ?flag. }}
            OPTIONAL {{ country:{0} pred:plate ?plate. }}
            OPTIONAL {{ country:{0} pred:name ?name. }}
            OPTIONAL {{ country:{0} pred:localtime ?localtime. }}
            OPTIONAL {{ country:{0} pred:population ?population. }}
            OPTIONAL {{ country:{0} pred:location ?location. }}
            OPTIONAL {{ country:{0} pred:life ?life. }}
            OPTIONAL {{ country:{0} pred:inflation ?inflation. }}
            OPTIONAL {{ country:{0} pred:area ?area. }}
            OPTIONAL {{ country:{0} pred:currency ?currency. }}
            OPTIONAL {{ country:{0} pred:pib ?pib. }}
            OPTIONAL {{ country:{0} pred:capital ?capital. }}
            OPTIONAL {{ 
                SELECT ?capital 
                    (SAMPLE(?capitalName) as ?capitalName)
                    (SAMPLE(?capitalArea) as ?capitalArea) 
                    (SAMPLE(?capitalPopulation) as ?capitalPopulation) 
                    (SAMPLE(?capitalImg) as ?capitalImg) {{
                        OPTIONAL {{ ?capital pred:name ?capitalName. }}
                        OPTIONAL {{ ?capital pred:area ?capitalArea. }}
                        OPTIONAL {{ ?capital pred:population ?capitalPopulation.  }}
                        OPTIONAL {{ ?capital pred:img ?capitalImg. }}
                }}
                GROUP BY ?capital
            }}
        }} 
    """.format(id)

    print(query)

    payload_query = {"query": query}
    res = json.loads(accessor.sparql_select(body=payload_query, repo_name=repo_name))['results']['bindings'][0]

    print(res)

    url = 'https://query.wikidata.org/sparql'
    wiki_query_infla = """
        SELECT *
        WHERE
        {{
            wd:{0} p:P1279 ?p .
            ?p pq:P585 ?year ;
            ps:P1279 ?inflation .
        }}
        order by ?year
    """.format(id)

    r = requests.get(url, params = {'format': 'json', 'query': wiki_query_infla})
    data = r.json()['results']['bindings']
    chartData_infla = {}
    for d in data:
        chartData_infla[d['year']['value'].split('-')[0]] = d['inflation']['value']

    wiki_query_pop = """
        SELECT *
        WHERE
        {{
            wd:{0} p:P1082 ?p .
            ?p pq:P585 ?year ;
            ps:P1082 ?population .
        }}
        order by ?year
    """.format(id)

    r = requests.get(url, params = {'format': 'json', 'query': wiki_query_pop})
    data = r.json()['results']['bindings']
    chartData_pop = {}
    for d in data:
        chartData_pop[d['year']['value'].split('-')[0]] = str(int(d['population']['value']) / 1000000)

    return render(request, 'country.html',  {
        'tmp': res,
        'title_infla': 'INFLATION EVOLUTION',
        'type_infla': 'line',
        'data_infla' : json.dumps(chartData_infla),
        'yAxe_infla' : 'inflation',
        'title_pop': 'POPULATION EVOLUTION (in Millions)',
        'type_pop': 'line',
        'data_pop' : json.dumps(chartData_pop),
        'yAxe_pop' : 'population'
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
                    ?country pred:population ?populacao.
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


