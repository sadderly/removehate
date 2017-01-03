import base64
import os
import json

from flask import Flask, render_template
from urllib2 import Request, urlopen, HTTPError
from urllib import urlencode

app = Flask(__name__)

bearer_token = None

def get_access_token():
    # encode consumer key and secret
    consumer_key = ("%s:%s") % (
        os.environ['REMOVE_HATE_TWITTER_KEY'],
        os.environ['REMOVE_HATE_TWITTER_SECRET'])
    encoded_consumer_key = base64.b64encode(consumer_key)

    # obtain a bearer token
    request = Request("https://api.twitter.com/oauth2/token")
    request.add_header('Authorization', 'Basic %s' % encoded_consumer_key)
    request.add_header('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')
    request.add_data('grant_type=client_credentials')
    response = urlopen(request)

    data = json.loads(response.read().decode('utf-8'))
    if data['token_type'] != 'bearer':
        raise HTTPError('invalid token type')
    return data['access_token']

@app.route('/')
def get_hate_crimes():
    global bearer_token
    if not bearer_token:
        bearer_token = get_access_token()

    query= {'q': "%23hatecrime"}
    resource_url = 'https://api.twitter.com/1.1/search/tweets.json'
    url = "%s?%s" % (resource_url, urlencode(query, True))

    request = Request(url)
    request.add_header('Authorization', 'Bearer %s' % bearer_token)

    response = urlopen(request)
    data = json.loads(response.read().decode('utf-8'))
    return render_template('result.html', result=data)
