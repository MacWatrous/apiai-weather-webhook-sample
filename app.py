#!/usr/bin/env python

import urllib
import json
import os
import requests

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    #if req.get("result").get("action") != "yahooWeatherForecast":
        #return {}

    if req.get("result").get("action") == "drugInquiry":
    	#rxcui = returnRXCUI(req)
    	inquiry = returnInquiry(req)
    	speech = inquiry
    	return {
    		"speech": speech,
       		"displayText": speech,
        	# "data": data,
        	# "contextOut": [],
        	"source": "apiai-weather-webhook-sample"
    	}

    if req.get("result").get("action") == "drugInteractions":
    	#rxcui = returnRXCUI(req)
    	inquiry = returnInteractions(req)
    	speech = inquiry
    	return {
    		"speech": speech,
       		"displayText": speech,
        	# "data": data,
        	# "contextOut": [],
        	"source": "apiai-weather-webhook-sample"
    	}

    if req.get("result").get("action") == "drugInteractionsPrior":
    	#rxcui = returnRXCUI(req)
    	inquiry = returnInteractionsPrior(req)
    	speech = inquiry
    	return {
    		"speech": speech,
       		"displayText": speech,
        	# "data": data,
        	# "contextOut": [],
        	"source": "apiai-weather-webhook-sample"
    	}
    	#ndc = returnNDC(rxcui)

    #else if req.get("result").get("action") == "drugInteractions":
    #	baseurl = "https://rxnav.nlm.nih.gov/REST/"
    else: 
    	return {}

    #yahoo stuff
    #baseurl = "https://query.yahooapis.com/v1/public/yql?"
    #yql_query = makeYqlQuery(req)
    #if yql_query is None:
    #    return {}
    #yql_url = baseurl + urllib.urlencode({'q': yql_query}) + "&format=json"
    #result = urllib.urlopen(yql_url).read()
    #data = json.loads(result)
    #res = makeWebhookResult(data)
    #return res

# def returnNDC(rxcui):
# 	url = "https://rxnav.nlm.nih.gov/REST/ndcproperties.json?id=" + rxcui
# 	result = (requests.get(url)).text
# 	lhs, rhs = result.split("ndc9\": \"",1)
# 	lhs, rhs = rhs.split("\",\"ndc10",1)
# 	ndc = lhs
# 	return ndc;

# def returnRXCUI(req):
# 	baseurl = "https://rxnav.nlm.nih.gov/REST/approximateTerm.json?"
# 	result = req.get("result")
# 	parameters = result.get("parameters")
# 	drug = parameters.get("drug")
# 	url = baseurl + "term=" + drug + "&maxEntries=1"
# 	result = (requests.get(url)).text
# 	lhs, rhs = result.split("rxcui\":\"",1)
# 	lhs, rhs = rhs.split("\",\"rxaui",1)
# 	rxcui = lhs
# 	return rxcui;

def returnInquiry(req):
	baseurl = "https://api.fda.gov/drug/label.json?search=openfda."
	result = req.get("result")
	parameters = result.get("parameters")
	drug = parameters.get("drug")
	url = baseurl + "generic_name:\"" + drug + "\""
	result = requests.get(url)
	if result.status_code != 200:
		url = baseurl + "brand_name:\"" + drug + "\""
		result = (requests.get(url))
		print("help!")

	result = result.text
	lhs, rhs = result.split("indications_and_usage\": [\n        \"",1)
	lhs, rhs = rhs.split("\"",1)
	inquiry = lhs
	return inquiry

def returnInteractions(req):
	baseurl = "https://api.fda.gov/drug/label.json?search=openfda."
	result = req.get("result")
	parameters = result.get("parameters")
	drug = parameters.get("drug")
	drug2 = parameters.get("drug1")

	url = baseurl + "generic_name:\"" + drug + "\""
	result = requests.get(url)
	if result.status_code != 200:
		url = baseurl + "brand_name:\"" + drug + "\""
		result = (requests.get(url))
		print("help!")
	result = result.text

	url2 = baseurl + "generic_name:\"" + drug2 + "\""
	result2 = requests.get(url2)
	if result2.status_code != 200:
		url2 = baseurl + "brand_name:\"" + drug2 + "\""
		result2 = (requests.get(url2))
		print("help!2")
	result2 = result2.text

	lhs, rhs = result.split("rxcui",1)
	rhs = rhs[16:]
	rhs = rhs[:6]
	rxcui = rhs

	lhs, rhs = result2.split("rxcui",1)
	rhs = rhs[16:]
	rhs = rhs[:6]
	rxcui2 = rhs

	baseurl2 = "https://rxnav.nlm.nih.gov/REST/interaction/list.json?rxcuis="
 	url3 = baseurl2 + rxcui + "+" + rxcui2
 	result3 = requests.get(url3)
	result3 = result3.text

	if "description" in result3:
		lhs, rhs = result3.split("description\":\"",1)
		lhs, rhs = rhs.split("\"",1)
		interaction = lhs
		return interaction
	return {}

def returnInteractionsPrior(req)
	baseurl = "https://api.fda.gov/drug/label.json?search=openfda."
	result = req.get("result")
	parameters = result.get("parameters")
	drug2 = parameters.get("drug1")
	contexts = result.get("contexts")
	conParam = contexts.get("parameters")
	drug = conParam.get("inquiredDrug")

	url = baseurl + "generic_name:\"" + drug + "\""
	result = requests.get(url)
	if result.status_code != 200:
		url = baseurl + "brand_name:\"" + drug + "\""
		result = (requests.get(url))
		print("help!")
	result = result.text

	url2 = baseurl + "generic_name:\"" + drug2 + "\""
	result2 = requests.get(url2)
	if result2.status_code != 200:
		url2 = baseurl + "brand_name:\"" + drug2 + "\""
		result2 = (requests.get(url2))
		print("help!2")
	result2 = result2.text

	lhs, rhs = result.split("rxcui",1)
	rhs = rhs[16:]
	rhs = rhs[:6]
	rxcui = rhs

	lhs, rhs = result2.split("rxcui",1)
	rhs = rhs[16:]
	rhs = rhs[:6]
	rxcui2 = rhs

	baseurl2 = "https://rxnav.nlm.nih.gov/REST/interaction/list.json?rxcuis="
 	url3 = baseurl2 + rxcui + "+" + rxcui2
 	result3 = requests.get(url3)
	result3 = result3.text

	if "description" in result3:
		lhs, rhs = result3.split("description\":\"",1)
		lhs, rhs = rhs.split("\"",1)
		interaction = lhs
		return interaction
	return {}

def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')" 

def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
             ", the temperature is " + condition.get('temp') + " " + units.get('temperature')

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=False, port=port, host='0.0.0.0')
