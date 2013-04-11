#!/usr/bin/env python
from wsgiref.simple_server import make_server
import json
from urllib2 import urlopen, URLError
from cgi import parse_qs
import re
from time import time

cur_codes = ('USD', 'AUD', 'CAD', 'CHF', 'CNY', 'DKK', 'EUR', 'GBP', 'HKD',
             'JPY', 'NZD', 'PLN', 'RUB', 'SEK', 'SGD', 'THB')
url_re = re.compile(r'^/(?P<cur_code>%s)/$' % ("(?:%s)" % ")|(?:".join(cur_codes),))

MTGOX_TICKER_URL = "https://data.mtgox.com/api/2/BTC%s/money/ticker"

curs = {}


def fetch_rate(cur_code):
    """
    Fetch the exchange rate for a given currency code from mtgox
    """
    try:
        f = urlopen(MTGOX_TICKER_URL % (cur_code, ))
    except URLError:
        return None
    data = json.load(f)
    if data.get('result') != 'success':
        return None
    try:
        return float(data['data']['last']['value'])
    except:
        return None


def get_rate(cur_code):
    """
    Return the exchange rate for a given currency code.
    Refresh result every 180 seconds, but allow old rate to be used for up to
    an hour.
    """
    t = curs.get(cur_code)
    if t is None or t[1] < time() - 180:
        rate = fetch_rate(cur_code)
        if rate:
            curs[cur_code] = (rate, time())
        else:
            if t[1] < time() - 3600:
                return None
            print "Warning: failed to fetch current rate - using old rate"
    return curs[cur_code][0]


def application(environ, start_response):
    def respond(status, body):
        content_length = str(len(body))
        start_response(status, [('Content-Type', 'application/json'),
                                ('Content-Length', content_length)])
        return [body]

    m = url_re.match(environ['PATH_INFO'])
    if m is None:
        return respond("404 Not Found", "{'result': 'fail'}")

    rate = get_rate(m.group('cur_code'))

    GET = parse_qs(environ['QUERY_STRING'])
    cb_name = GET.get('callback', [None])[0]

    if rate is None or cb_name is None:
        return respond("500 Server Error", "{'result': 'fail'}")

    return respond("200 OK", "%s(%s)" % (cb_name,
                                         json.dumps({'result': 'success',
                                                     'btc_price': rate})))


if __name__ == '__main__':
    httpd = make_server('localhost', 8000, application)
    httpd.serve_forever()
