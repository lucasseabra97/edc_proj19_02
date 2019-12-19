from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest
from django.shortcuts import render
import json
import requests
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
import math
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect

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
        PREFIX user: <http://edc_2019.org/user/>
        select * {{
            user:{0} rdf:type user:
        }}
    """.format(user)
    payload_query = {"query": query}
    res = json.loads(accessor.sparql_select(body=payload_query, repo_name=repo_name))['results']['bindings']
    
    print("HERE", res)
    if len(res):
        return HttpResponse(status = 400)
    else:
        query = """
        PREFIX user:<http://edc_2019.org/user/>
        PREFIX pred:<http://edc_2019.org/pred/>
        PREFIX foaf:<http://xmlns.com/foaf/0.1/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        INSERT DATA {{
            user:{0} pred:password \"{1}\";
                     rdf:type user:;
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

@csrf_exempt
def notes(request):
    
    username = request.COOKIES.get('username')
    password = request.COOKIES.get('password')

    query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX pred: <http://edc_2019.org/pred/>
        PREFIX user: <http://edc_2019.org/user/>
        select ?note where {{
            user:{0} rdf:type user:.
            user:{0} pred:password '{1}'.
            user:{0} pred:note ?note
        }}
    """.format(username, password)
    payload_query = {"query": query}
    res = json.loads(accessor.sparql_select(body=payload_query, repo_name=repo_name))['results']['bindings']
    
    return render(request, 'notes.html',  {
        'notes': res,
        'username': username
    })
    
@csrf_exempt
def addnote(request):
    
    username = request.COOKIES.get('username')
    password = request.COOKIES.get('password')
    note = request.GET.get('note')

    query = """
        PREFIX user:<http://edc_2019.org/user/>
        PREFIX pred:<http://edc_2019.org/pred/>
        INSERT DATA {{
            user:{0} pred:password '{1}';
                     pred:note '{2}'
        }}
    """.format(username, password, note)

    print(query)

    payload_query = {"update": query}
    res = accessor.sparql_update(body=payload_query, repo_name=repo_name)
    
    print("HERE", res)
    return redirect('notes')
    
@csrf_exempt
def removenote(request):
    
    username = request.COOKIES.get('username')
    password = request.COOKIES.get('password')
    note = request.GET.get('note')

    query = """
        PREFIX user:<http://edc_2019.org/user/>
        PREFIX pred:<http://edc_2019.org/pred/>
        DELETE {{
            user:{0} pred:note '{2}'
        }} WHERE {{
            user:{0} pred:password '{1}'
        }}
    """.format(username, password, note)

    print(query)

    payload_query = {"update": query}
    res = accessor.sparql_update(body=payload_query, repo_name=repo_name)
    
    print("HERE", res)
    return redirect('notes')

def landing(request):

    limit = 20
    page = int(request.GET.get('page')) if request.GET.get('page') else 1
    order = request.GET.get('order') or 'name'
    search = (request.GET.get('search') or '').lower()
    dir = (request.GET.get('dir') or '').upper()

    query = """
        PREFIX country:<http://edc_2019.org/country/>
        PREFIX pred:<http://edc_2019.org/pred/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT  
        *
        WHERE
        {{
            ?country rdf:type country:.
            ?country pred:name ?name
            FILTER (CONTAINS(lcase(?name), '{0}') || CONTAINS(lcase(?plate), '{0}')) 
        }}
    """.format(search)

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
            FILTER (CONTAINS(lcase(?name), '{3}') || CONTAINS(lcase(?plate), '{3}')) 
            OPTIONAL {{ ?country pred:plate ?plate. }}
            OPTIONAL {{ ?country pred:currency ?currency. }}
            OPTIONAL {{ ?country pred:population ?population. }}
            OPTIONAL {{ ?country pred:localtime ?localtime. }}
            OPTIONAL {{ ?country pred:area ?area. }}
            OPTIONAL {{ ?country pred:inflation ?inflation. }}
            OPTIONAL {{ ?country pred:pib ?pib. }}
        }}
        ORDER BY {4}({2})
        OFFSET {0}
        LIMIT {1}
    """.format(
        (page - 1) * limit, 
        limit, 
        'xsd:float(?{})'.format(order) if (order in ['area', 'population', 'inflation', 'pib']) else '?' + order,
        search,
        dir
    )

    payload_query = {"query": query}
    res = json.loads(accessor.sparql_select(body=payload_query, repo_name=repo_name))['results']['bindings']

    maxPage = math.ceil(size / limit)

    pages = [i+1 for i in range(maxPage)]
    left = [i for i in pages if page - i < 3 and i < page]
    right = [i for i in pages if i - page < 3 and i > page]

    print(left, right)

    return render(request, 'landing.html', {
        'table_order': ['plate', 'name', 'localtime', 'currency', 'population', 'area', 'inflation', 'pib'],
        'units': ['','','','','',' km2','%','%'],
        'countries': res,
        'size': size,
        'left': left,
        'right': right,
        'page': page,
        'maxPage': maxPage,
        'showMax': (maxPage - page) >= 3,
        'showMin': page >= 3,
        'showing': size % limit if page == maxPage and size % limit != 0 else limit,
    })


def country(request):
    id = request.GET.get('id')

    query = """
        PREFIX country:<http://edc_2019.org/country/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX pred: <http://edc_2019.org/pred/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>

        SELECT  
        ?plate 
        ?flag ?name 
        ?localtime ?population 
        ?location ?life 
        ?inflation ?area
        ?currency ?pib 
        ?capital ?capitalName ?capitalArea ?capitalPopulation ?capitalImg
        ?president ?presidentName ?presidentImage
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
            OPTIONAL {{ country:{0} pred:president ?president. }}
            OPTIONAL {{ 
                SELECT ?president 
                (SAMPLE(?presidentName) as ?presidentName)
                (SAMPLE(?presidentImage) as ?presidentImage)  {{
                    OPTIONAL {{ ?president foaf:name ?presidentName. }}
                    OPTIONAL {{ ?president foaf:Image ?presidentImage. }}
                }}
                GROUP BY ?president
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
        'country': {
            'id': id,
            **res
        },
        'country_order': ['inflation', 'pib', 'area', 'population', 'life'],
        'units': ['%','%','Km2','',' years'],


        'title_infla': 'INFLATION EVOLUTION',
        'type_infla': 'line',
        'data_infla' : json.dumps(chartData_infla),
        'yAxe_infla' : 'inflation',
        'title_pop': 'POPULATION EVOLUTION (in Millions)',
        'type_pop': 'line',
        'data_pop' : json.dumps(chartData_pop),
        'yAxe_pop' : 'population'
    })


def presidents(request):
    query =   """ 
            PREFIX country:<http://edc_2019.org/presidents/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX pred: <http://edc_2019.org/pred/>

            SELECT  ?country ?ministro ?imag ?republica 
            WHERE
            {
            ?country wdt:P31 wd:Q6256;
                    wdt:P41 ?flag;
                    wdt:P6  ?president;
                    wdt:P35  ?rep.
            ?president wdt:P735 ?presidentname.
            OPTIONAL{?presidentname wdt:P1705 ?ministro.}
            ?president wdt:P18 ?imag.
                OPTIONAL{?rep  wdt:P1559 ?republica.}
            }ORDER BY desc(?presidentname)                
            """
    tmp = parseQuery(query)

    return render(request, 'presidents.html',  {
        'tmp': tmp
    })

        