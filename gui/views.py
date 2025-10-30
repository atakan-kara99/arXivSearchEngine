import collections
from numpy import empty
import requests
from ctypes import util
from email import utils
from django.shortcuts import render
from se import settings

from se.main import SearchEngine
from se.utils import preprocessing, transformQueryForSolr
from se.evaluation import Evaluation

""" View for the search engine """
def index(request):
    # get the typed query
    query = request.GET.get('query')

    # get the flag for evaluation
    evaluation_flag = request.GET.get('evaluation')
    #print(evaluation_flag)


    if query == '' or query == None:
        return render(request, 'gui/index.html', {'documents':None, 'query': 'Please type down a query to work with!'})
    
    se = SearchEngine()
    ids = se.search(query) # loads the data into main mem
    #se.create_arxiv()
    json_data: dict = se.get_info_by_id( ids )

    #print(f"ids: {ids}")

    ordered_json_values = list(json_data.values())

    boogle_ids: list = []
    
    for item in ordered_json_values:
        item['journal'] = item['journal-ref']
        item['snippet'] = se.compute_snippet(item['abstract'], preprocessing(query))
        boogle_ids.append(item['id'])

    # when no evaluation flag is setted, we do not need to compute further..
    if evaluation_flag is None:
        return render(request, 'gui/index.html', {'documents':ordered_json_values, 'query': 'Results for query: ' + query})

    # transforming our query for a solr understandable query
    solrQuery = transformQueryForSolr(query)
    #print(solrQuery)

    # requesting solr for results
    URL: str = f"http://localhost:8983/solr/inf_ret/select?indent=true&q.op=OR&rows={settings.NUM_OF_SOLR_DOCS}&q={solrQuery.replace(':', '%3A')}"
    response = requests.post(URL, headers={"Content-Type": 'application/json'}) # get the results from solr
    docs: list = response.json()['response']['docs']

    # store the solr ids as a list
    solr_ids: list = [d['id'] for d in docs]

    # the evaluation measures..
    eval = Evaluation(solr_ids, boogle_ids)

    return render(
        request, 
        'gui/index.html', 
        {
            'documents':ordered_json_values, 
            'query': 'Results for query: ' + query, 
            'measures': {
                'prec': eval.precisionAt10(),
                'mean': eval.meanAveragePrecision(),
                'norm': eval.normalizedDCG()
            }
    })


""" 
Handles the searching via solr search engine.
Makes request to solr via REST and get a response as json.
"""
def ging(request):
    se = SearchEngine()
    # get the typed query
    query = request.GET.get('query')
    
    # show hint when no query was used to work with
    if query == '' or query is None:
        return render(request, 'gui/ging.html', {'documents':None, 'query': 'Please type down a query to work with!'})

    # transforming our query for a solr understandable query
    solrQuery = transformQueryForSolr(query)
    #print(solrQuery)

    # requesting solr for results
    URL: str = f"http://localhost:8983/solr/inf_ret/select?indent=true&q.op=OR&rows={settings.NUM_OF_SOLR_DOCS}&q={solrQuery.replace(':', '%3A')}"
    response = requests.post(URL, headers={"Content-Type": 'application/json'}) # get the results from solr
    docs: list = response.json()['response']['docs']

    for item in docs:
        try: 
            item['journal'] = item['journal-ref'][0]
        except KeyError:
            item['journal'] = None

        if not('doi' in item.keys()):
            item['doi'] = [None]

        item['snippet'] = se.compute_snippet(item['abstract'][0], preprocessing(query))

    # request to solr and print response here..
    return render(request, 'gui/ging.html', {'documents':docs, 'query': "Results for query: " + query})