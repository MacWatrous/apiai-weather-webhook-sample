#API.AI Webhook based on https://github.com/api-ai/apiai-weather-webhook-sample
#Mac Watrous for MedBot POC

#!/usr/bin/env python

import urllib
import json
import os
import requests
import re

from flask import Flask
from flask import request
from flask import make_response

#Flask app should start in global layout
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    #package API.AI information and parse it
    res = processRequest(req)

    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

#Take bot input and determine what other function to call
def processRequest(req):
    if req.get("result").get("action") == "drugInquiry":
        inquiry = returnInquiry(req)
        speech = inquiry
        #returning to API.AI to 'say'
        return {
            "speech": speech,
            "displayText": speech,
            #"data": data,
            #"contextOut": [],
            "source": "apiai-weather-webhook-sample"
        }

    if req.get("result").get("action") == "drugInteractions":
        inquiry = returnInteractions(req)
        speech = inquiry
        return {
            "speech": speech,
            "displayText": speech,
            #"data": data,
            #"contextOut": [],
            "source": "apiai-weather-webhook-sample"
        }

    #Drug Interactions with a previously entered drug as context
    if req.get("result").get("action") == "drugInteractionsPrior":
        inquiry = returnInteractionsPrior(req)
        speech = inquiry
        return {
            "speech": speech,
            "displayText": speech,
            #"data": data,
            #"contextOut": [],
            "source": "apiai-weather-webhook-sample"
        }
    if req.get("result").get("action") == "drugRoute":
        inquiry = returnRoute(req)
        speech = inquiry
        return {
            "speech": speech,
            "displayText": speech,
            #"data": data,
            #"contextOut": [],
            "source": "apiai-weather-webhook-sample"
        }
    else: 
        return {}

#Commented out functions which grab additional drug info
#def returnNDC(rxcui):
    #url = "https://rxnav.nlm.nih.gov/REST/ndcproperties.json?id=" + rxcui
    #result = (requests.get(url)).text
    #lhs, rhs = result.split("ndc9\": \"",1)
    #lhs, rhs = rhs.split("\",\"ndc10",1)
    #ndc = lhs
    #return ndc;

#def returnRXCUI(req):
    #baseurl = "https://rxnav.nlm.nih.gov/REST/approximateTerm.json?"
    #result = req.get("result")
    #parameters = result.get("parameters")
    #drug = parameters.get("drug")
    #url = baseurl + "term=" + drug + "&maxEntries=1"
    #result = (requests.get(url)).text
    #lhs, rhs = result.split("rxcui\":\"",1)
    #lhs, rhs = rhs.split("\",\"rxaui",1)
    #rxcui = lhs
    #return rxcui;

def returnInquiry(req):
    baseurl = "https://api.fda.gov/drug/label.json?search=openfda."
    result = req.get("result") #parsing our api.ai input
    parameters = result.get("parameters")
    drug = parameters.get("drug")
    url = baseurl + "generic_name:\"" + drug + "\""
    result = requests.get(url)
    if result.status_code != 200: #get generic drug info with drug name, if drug is a brand and not generic..
        url = baseurl + "brand_name:\"" + drug + "\""
        result = (requests.get(url))
        result = result.text
        lhs, rhs = result.split("indications_and_usage\": [\n        \"",1) #look for indications_and_usage field in response JSON
        rhs = rhs.replace('\"',".")
        lhs, rhs = rhs.split(".",1)
        inquiry = lhs
        return inquiry

    result = result.text
    lhs, rhs = result.split("indications_and_usage\": [\n        \"",1) #look for indications_and_usage field in response JSON
    rhs = rhs.replace('\"',".")
    lhs, rhs = rhs.split(".",1)
    inquiry = lhs
    return inquiry

def returnRoute(req):
    baseurl = "https://api.fda.gov/drug/label.json?search="
    result = req.get("result")
    parameters = result.get("parameters")
    drug = parameters.get("drug")
    url = baseurl + drug + "&count=openfda.route.exact"
    result = requests.get(url)

    result = result.text
    lhs, rhs = result.split("term\": \"",1) #look for 'term' field in response JSON
    lhs, rhs = rhs.split("\"",1)
    inquiry = lhs
    inquiry = inquiry.lower()
    return "The most common route of administration we've found for " + drug + " is " + inquiry + "."


def returnInteractions(req):
    baseurl = "https://api.fda.gov/drug/label.json?search=openfda."
    result = req.get("result")
    parameters = result.get("parameters")
    drug = parameters.get("drug")

    url = baseurl + "generic_name:\"" + drug + "\""
    result = requests.get(url)
    if result.status_code != 200:
        url = baseurl + "brand_name:\"" + drug + "\""
        result = (requests.get(url))
    result = result.text
    lhs, rhs = result.split("rxcui",1)
    rhs = rhs[16:]
    array = re.findall(r"\w+",rhs) #parse arrays of RXCUIs
    rxcui = array[0]

    if "true" == parameters.get("alcohol", "true"): #if the user isn't talking about alcohol
        drug2 = parameters.get("drug1")
        url2 = baseurl + "generic_name:\"" + drug2 + "\""
        result2 = requests.get(url2)
        if result2.status_code != 200:
            url2 = baseurl + "brand_name:\"" + drug2 + "\""
            result2 = (requests.get(url2))
        result2 = result2.text
        lhs, rhs = result2.split("rxcui",1)
        rhs = rhs[16:]
        array = re.findall(r"\w+",rhs) #parse arrays of RXCUIs
        rxcui2 = array[0]
    else: #if the user is talking about alcohol set our second drug to ethanol
        rxcui2 = "448"

    baseurl2 = "https://rxnav.nlm.nih.gov/REST/interaction/list.json?rxcuis="
    url3 = baseurl2 + rxcui + "+" + rxcui2
    result3v2 = requests.get(url3)
    result3 = result3v2.text

    if "severity" in result3: #if there is an interaction
        if rxcui2 == "448":
            drug2 = "alcohol"

        lhs, rhs = result3.split("description\":\"",1) #find description in JSON
        lhs, rhs = rhs.split("\"",1)
        interaction = lhs
        result3v2 = result3v2.json()
        resultDrug = result3v2['fullInteractionTypeGroup'][0]['fullInteractionType'][0]['interactionPair'][0]['interactionConcept'][0]['minConceptItem']['name']
        resultDrug2 = result3v2['fullInteractionTypeGroup'][0]['fullInteractionType'][0]['interactionPair'][0]['interactionConcept'][1]['minConceptItem']['name']

        #if minconcept1 contains rxcui2 then switch drug 1 and drug 2
        if result3v2['fullInteractionTypeGroup'][0]['fullInteractionType'][0]['minConcept'][0]['rxcui'] == rxcui2:
            temp = drug
            drug = drug2
            drug2 = temp            

        #appending originally searched drug names to the interaction's drug names
        index = (interaction.lower()).find(resultDrug.lower())
        drug = drug.lower()
        drug = drug[0].upper() + drug[1:]
        interaction = interaction[:index] + drug + " (" + interaction[index:]
        index = index + len(resultDrug) + len(drug) + 2
        interaction = interaction[:index] + ")" + interaction[index:]

        index = (interaction.lower()).find(resultDrug2.lower())
        interaction = interaction[:index] + drug2.lower() + " (" + interaction[index:]
        index = index + len(resultDrug2) + len(drug2) + 2
        interaction = interaction[:index] + ")" + interaction[index:]
        
        return interaction
    return "There is no interaction between these drugs!"

def returnInteractionsPrior(req):
    baseurl = "https://api.fda.gov/drug/label.json?search=openfda."
    result = req.get("result")
    parameters = result.get("parameters")
    drug = parameters.get("drug")

    url = baseurl + "generic_name:\"" + drug + "\""
    result = requests.get(url)
    if result.status_code != 200:
        url = baseurl + "brand_name:\"" + drug + "\""
        result = (requests.get(url))
    result = result.text
    lhs, rhs = result.split("rxcui",1)
    rhs = rhs[16:]
    array = re.findall(r"\w+",rhs)
    rxcui = array[0]

    if "true" == parameters.get("alcohol", "true"):
        drug2 = parameters.get("drug1")
        url2 = baseurl + "generic_name:\"" + drug2 + "\""
        result2 = requests.get(url2)
        if result2.status_code != 200:
            url2 = baseurl + "brand_name:\"" + drug2 + "\""
            result2 = (requests.get(url2))
        result2 = result2.text
        lhs, rhs = result2.split("rxcui",1)
        rhs = rhs[16:]
        array = re.findall(r"\w+",rhs)
        rxcui2 = array[0]
    
    else:
        rxcui2 = "448"

    baseurl2 = "https://rxnav.nlm.nih.gov/REST/interaction/list.json?rxcuis="
    url3 = baseurl2 + rxcui + "+" + rxcui2
    result3v2 = requests.get(url3)
    result3 = result3v2.text

    if "severity" in result3: #if there is an interaction
        if rxcui2 == "448":
            drug2 = "alcohol"

        lhs, rhs = result3.split("description\":\"",1) #find description in JSON
        lhs, rhs = rhs.split("\"",1)
        interaction = lhs
        result3v2 = result3v2.json()
        resultDrug = result3v2['fullInteractionTypeGroup'][0]['fullInteractionType'][0]['interactionPair'][0]['interactionConcept'][0]['minConceptItem']['name']
        resultDrug2 = result3v2['fullInteractionTypeGroup'][0]['fullInteractionType'][0]['interactionPair'][0]['interactionConcept'][1]['minConceptItem']['name']

        #if minconcept1 contains rxcui2 then switch drug 1 and drug 2
        if result3v2['fullInteractionTypeGroup'][0]['fullInteractionType'][0]['minConcept'][0]['rxcui'] == rxcui2:
            temp = drug
            drug = drug2
            drug2 = temp     

        #appending originally searched drug names to the interaction's drug names
        index = (interaction.lower()).find(resultDrug.lower())
        drug = drug.lower()
        drug = drug[0].upper() + drug[1:]
        interaction = interaction[:index] + drug + " (" + interaction[index:]
        index = index + len(resultDrug) + len(drug) + 2
        interaction = interaction[:index] + ")" + interaction[index:]

        index = (interaction.lower()).find(resultDrug2.lower())
        interaction = interaction[:index] + drug2.lower() + " (" + interaction[index:]
        index = index + len(resultDrug2) + len(drug2) + 2
        interaction = interaction[:index] + ")" + interaction[index:]

        return interaction
    return "Looks like there is no interaction between these drugs."

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(debug=False, port=port, host='0.0.0.0')