#!/usr/bin/env python

import urllib2

req = urllib2.Request('http://swordfish.rdfweb.org/xxxx')
try: 
   urllib2.urlopen(req) 
except urllib2.HTTPError, e:
   print e.code

