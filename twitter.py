# coding: utf-8
"""
Main module.
Contains OAuth token and functions generating tweets and statistics
"""
from collections import defaultdict

from flask import Flask
from flask import g, session, request, url_for, flash
from flask import redirect, render_template
from flask_oauthlib.client import OAuth
from email.utils import parsedate_tz, mktime_tz
from datetime import datetime
from geopy.geocoders import Nominatim

app = Flask(__name__)
app.debug = True
app.secret_key = 'development'

oauth = OAuth(app)

twitter = oauth.remote_app(
    'twitter',
    consumer_key='LkADU6NROui4yXczoqPpYWOfO',
    consumer_secret='zQCkhOdeJkPQXABvx5GGYlI7fnj05NcmDrdweUBSAbReSpSgbr',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate'
)

SECONDS_IN_DAY = 24 * 3600


def create_app():
    app = Flask(__name__)
    app.debug = True
    app.secret_key = 'development'
    return app


@twitter.tokengetter
def get_twitter_token():
    if 'twitter_oauth' in session:
        resp = session['twitter_oauth']
        return resp['oauth_token'], resp['oauth_token_secret']


@app.before_request
def before_request():
    g.user = None
    if 'twitter_oauth' in session:
        g.user = session['twitter_oauth']


def in_previous_24h(date_str):
    """Function used to to check whether date represented by given string
     is within 24h period from current time

    :param date_str:
        date_str: String with date. Preferred full date format
         e.g. <Fri Jun 19 12:25:37 +0000 2015>

    :return:
        The boolean value. True for date within 24h, False otherwise.
    """
    return int(
        datetime.now().timestamp()) - mktime_tz(
        parsedate_tz(date_str)
    ) <= SECONDS_IN_DAY


def get_recent_tweets():
    """Function used to get tweets posted by friends in last 24 hours"""
    friends = twitter.request('friends/ids.json').data
    recent = []
    for friend in friends['ids'][:3]:
        timeline = twitter. \
            request('statuses/user_timeline.json?user_id={}&count=200'
                    .format(friend)).data
        count = sum(1 for x in timeline if in_previous_24h(x['created_at']))
        recent.append([str(friend),
                       count + 1, count + 1
                       ])
    print(recent)
    return recent


def get_languages():
    """
    Function used to get list of languages used by friends.
    Friends' languages are derived from twitter 'lang' parameter
    Return format is ready to be used by Google Visualization API.
    """
    friends = twitter.request('friends/list.json').data
    languages = defaultdict(int)
    for friend in friends['users']:
        languages[friend['lang']] += 1
    languages_list = [[lang, count, count]
                      for lang, count in languages.items()]
    print(languages_list)
    return languages_list


def get_countries(tweets):
    """
    Function used to get list of countries from which given tweets orginate.
    Countries are derived either from a 'place' parameter or by checking
    tweet's coordinates with geopy.
    Return format is ready to be used by Google Visualization API.
    """
    countries = defaultdict(int)
    geolocator = Nominatim()
    for single_tweet in tweets:
        if single_tweet['place'] is not None:
            countries[single_tweet['place']['country']] += 1
        else:
            if single_tweet['coordinates'] is not None:
                country = geolocator.reverse(single_tweet['coordinates']
                                             .coordinates, language='en')
                countries[country] += 1
    countries_list = [[country, count, count]
                      for country, count in countries.items()]
    print(countries_list)
    return countries_list


def get_hashtags():
    """
    Function used to get list of most popular hashtags/trends
    with popularity associated with each hashtag.
    Collection is sorted by popularity.
    """
    trends = twitter.request('trends/place.json?id=1').data
    trends_list = [[x['name'], int(x['tweet_volume'])]
                   for x in trends[0]['trends']
                   if isinstance(x['tweet_volume'], int)]
    trends_list = sorted(trends_list, key=lambda x: x[1], reverse=True)
    return list(trends_list)


@app.route('/')
def index():
    """Function generating main page"""
    tweets = None
    languages = None
    countries = None
    trends = None
    if g.user is not None:
        resp = twitter.request('statuses/home_timeline.json')

        if resp.status == 200:
            tweets = resp.data
            countries = get_countries(tweets)
        else:
            flash('Unable to load tweets from Twitter.')
        try:
            languages = get_languages()
            trends = get_hashtags()
            print(trends)
        except KeyError:
            pass
            # print(tweets)
    return render_template('augmented_index.html',
                           tweets=tweets,
                           language_data=languages,
                           countries_data=countries,
                           hashtags_data=trends)


@app.route('/tweet', methods=['POST'])
def tweet():
    """Function used to post tweet passed in request data"""
    if g.user is None:
        return redirect(url_for('login', next=request.url))
    status = request.form['tweet']
    if not status:
        return redirect(url_for('index'))
    resp = twitter.post('statuses/update.json', data={
        'status': status
    })

    if resp.status == 403:
        flash("Error: #%d, %s " % (
            resp.data.get('errors')[0].get('code'),
            resp.data.get('errors')[0].get('message'))
              )
    elif resp.status == 401:
        flash('Authorization error with Twitter.')
    else:
        flash('Successfully tweeted your tweet (ID: #%s)' % resp.data['id'])
    return redirect(url_for('index'))


@app.route('/login')
def login():
    """Function used to log into application"""
    callback_url = url_for('oauthorized', next=request.args.get('next'))
    return twitter.authorize(callback=callback_url or request.referrer or None)


@app.route('/logout')
def logout():
    """Function used to log out of application"""
    session.pop('twitter_oauth', None)
    return redirect(url_for('index'))


@app.route('/oauthorized')
def oauthorized():
    resp = twitter.authorized_response()
    if resp is None:
        flash('You denied the request to sign in.')
    else:
        session['twitter_oauth'] = resp
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
