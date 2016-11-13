from __future__ import absolute_import

import json
import os
from urlparse import urlparse
import googlemaps
from flask import Flask, render_template, request, redirect, session
from flask_sslify import SSLify
from rauth import OAuth2Service
import requests
import datetime
import sendgrid

app = Flask(__name__, static_folder='static', static_url_path='')
app.requests_session = requests.Session()
app.secret_key = os.urandom(24)

sslify = SSLify(app)

with open('config.json') as f:
    config = json.load(f)


def generate_oauth_service():
    """Prepare the OAuth2Service that is used to make requests later."""
    return OAuth2Service(
        client_id=os.environ.get('UBER_CLIENT_ID'),
        client_secret=os.environ.get('UBER_CLIENT_SECRET'),
        name=config.get('name'),
        authorize_url=config.get('authorize_url'),
        access_token_url=config.get('access_token_url'),
        base_url=config.get('base_url'),
    )


def generate_ride_headers(token):
    """Generate the header object that is used to make api requests."""
    return {
        'Authorization': 'bearer %s' % token,
        'Content-Type': 'application/json',
    }


@app.route('/health', methods=['GET'])
def health():
    """Check the status of this application."""
    return ';-)'


@app.route('/', methods=['GET'])
def signup():
    """The first step in the three-legged OAuth handshake.

    You should navigate here first. It will redirect to login.uber.com.
    """
    params = {
        'response_type': 'code',
        'redirect_uri': get_redirect_uri(request),
        'scopes': ','.join(config.get('scopes')),
    }
    url = generate_oauth_service().get_authorize_url(**params)
    return redirect(url)


@app.route('/submit', methods=['GET'])
def submit():
    """The other two steps in the three-legged Oauth handshake.

    Your redirect uri will redirect you here, where you will exchange
    a code that can be used to obtain an access token for the logged-in use.
    """
    params = {
        'redirect_uri': get_redirect_uri(request),
        'code': request.args.get('code'),
        'grant_type': 'authorization_code'
    }
    response = app.requests_session.post(
        config.get('access_token_url'),
        auth=(
            os.environ.get('UBER_CLIENT_ID'),
            os.environ.get('UBER_CLIENT_SECRET')
        ),
        data=params,
    )
    session['access_token'] = response.json().get('access_token')

    return render_template(
        'success.html',
        token=response.json().get('access_token')
    )


@app.route('/demo', methods=['GET'])
def demo():
    """Demo.html is a template that calls the other routes in this example."""
    return render_template('demo.html', token=session.get('access_token'))




@app.route('/remind', methods = ['POST'])
def remind():
    url = config.get('base_uber_url') + 'estimates/time'
    gmaps = googlemaps.Client(key='AIzaSyDTZt-pkIfewSKGRIEypBJHUNhdALTz6io')

    source = request.form['sourceText']
    destination = request.form['destinationText']
    user_time = request.form['time']
    email = request.form['email']

    src_lat = source.split(',')[0]
    src_lng = source.split(',')[1]

    # dest_lat = destination.split(',')[0]
    # dest_lng = destination.split(',')[1]

    params = {
        'start_latitude': src_lat,
        'start_longitude': src_lng,
    }

    eta = gmaps.distance_matrix(source, destination)
    if eta['rows'][0]['elements'][0]['status'] == "OK":
        # duration = eta['rows']['elements']['duration']['text']
        o = 0
        for i in eta['rows']:
            d = 0
            o += 1
            for j in i['elements']:
                duration_in_seconds = j['duration']['value']
                d += 1
    maps_duration_in_hours = str(datetime.timedelta(seconds=duration_in_seconds))

    time_format = '%H:%M:%S'
    ride_time = datetime.datetime.strptime(user_time, time_format) - datetime.datetime.strptime(maps_duration_in_hours, time_format)

    response = app.requests_session.get(
        url,
        headers=generate_ride_headers(session.get('access_token')),
        params=params,
    )

    estimated_time = 0
    sourceResponse = response.text
    uberGo = json.loads(sourceResponse)
    for row in uberGo['times']:
        if 'UberGO' or 'uberGO' in row.values():
            uber_estimated_seconds = row['estimate']
            uber_estimated_hhmmss = datetime.timedelta(seconds=uber_estimated_seconds)

            email_time = ride_time - uber_estimated_hhmmss

            return render_template(
                'results.html',
                endpoint='time',
                data=email_time
            )

def send_email(email_time, email):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('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'))

    data = {
        "personalizations": [
            {
                "to": [
                    {
                        "email": email
                    }
                ],
                "subject": "Time to book Uber!"
            }
        ],
        "send_at": email_time,
        "from": {
            "email": "mayurbhangale96@gmail.com"
        },
        "content": [
            {
                "type": "text/plain",
                "value": "Hello, Its time to book your cab!"
            }
        ]
    }

    response = sg.client.mail.send.post(request_body=data)
    print(response.status_code)
    print(response.body)
    print(response.headers)

def get_redirect_uri(request):
    """Return OAuth redirect URI."""
    parsed_url = urlparse(request.url)
    if parsed_url.hostname == 'localhost':
        return 'http://{hostname}:{port}/submit'.format(
            hostname=parsed_url.hostname, port=parsed_url.port
        )
    return 'https://{hostname}/submit'.format(hostname=parsed_url.hostname)

if __name__ == '__main__':
    app.debug = os.environ.get('FLASK_DEBUG', True)
    app.run(port=7000)
