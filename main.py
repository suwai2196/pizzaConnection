import urllib
import json
import os

import psycopg2
from pprint import pprint

from flask import Flask
from flask import request
from flask import make_response
from owlready2 import *

def ConnectOnto():
    my_world = World()
    my_world.get_ontology('file://owl/pizza.owl').load()  # path to the owl file is given here
    # reasoner is started and synchronized here
    graph = my_world.as_rdflib_graph()
    return graph

graph = ConnectOnto()

@app.route('/webhook', methods=['POST'])

def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

    def makeWebhookResult(req):
        if req.get("result").get("action") == "listPizza":
            graph = ConnectOnto()
            result = req.get("result")
            parameters = result.get("parameters")
            a = None
            



            query = ("PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>  \
                                                PREFIX owl: <http://www.w3.org/2002/07/owl#>  \
                                                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>  \
                                                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>  \
                                                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \
                                                SELECT ?pizza   \
                                                WHERE {?pizza rdfs:subClassOf pz:NamedPizza .}")
            results = graph.query(query)
            response = []
            for item in results:
                pizza = str(item['pizza'].toPython())
                pizza = re.sub(r'.*#', "", pizza)
                response.append('-' + pizza)
                a = '\n'.join(map(str, response))

            if a is None:
                b = "Sorry, we don't have offfer for you now."
            else:
                b = "These are offered pizza for you  \n" + a


            fulfillmentText = b
            print("Response:")
            print(fulfillmentText)
            return {
                # "data": {},
                # "contextOut": [],
                "speech": fulfillmentText,
                "fulfillmentText": fulfillmentText,
                "displayText": '25',
                "source": "webhookdata"
            }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % (port))

    app.run(debug=True, port=port, host='0.0.0.0')