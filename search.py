#!/usr/bin/env python

import json
import functools
import hashlib
import os
import requests

import logging
logging.getLogger('').setLevel(logging.DEBUG)

out = {}
with open('./markers3.json') as fd:
  for i in json.load(fd):
    out[i['siteName']] = (i['latitude'],i['longitude'],)


def _make_hash(key):
  h = hashlib.md5(key)
  return h.hexdigest()

def _cache_put(key, data):
  h = _make_hash(key)
  with open("./cache/%s" % h, 'w') as fd:
    json.dump(data, fd)

def _cache_get(key):
  h = _make_hash(key)
  if os.path.exists("./cache/%s" % h):
    with open("./cache/%s" % h, 'r') as fd:
      return json.load(fd)
  else:
    return None

def cache(f):
  @functools.wraps(f)
  def wrapper(*args, **kwargs):
    k = kwargs['key']
    p = kwargs['pair']

    d = _cache_get(k)
    if not d:
      try:
        resp = f(*args, **kwargs)
        resp['META'] = kwargs

        _cache_put(k, resp)
        d = resp
      except NOCACHE:
        pass
    return d
  return wrapper

class NOCACHE(Exception):
  pass

@cache
def lookup(key, pair):
  listing_ep = "https://api.zoopla.co.uk/api/v1/property_listings"
  params = {
    "listing_status": "rent",
    "page_size": 100,
    "radius": 0.01, #miles 0.01 is min
    "api_key": "p72f5svjsjhmbss9wgsebgn6",
  }
  headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
  params['latitude'], params['longitude'] = pair
  try:
    resp = requests.get(listing_ep, params=params, headers=headers)
  except Exception as e:
    logging.error("unable to fetch %s", e)
    raise NOCACHE(e)

  qres = {}
  try:
    qres = resp.json()
  except Exception as e:
    logging.error("invalid json %s", resp.text)
    raise NOCACHE(e)

  return qres

for key, pair in out.iteritems():
  print lookup(key=key, pair=pair)
  break
  # do something...



#resp
  #listing
listing_keys = [
  "details_url",
  "price"
]


