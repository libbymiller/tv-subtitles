#!/usr/bin/env python

import urllib
import urllib2
from xml.dom import minidom
from xml.parsers.expat import ExpatError
import sys
import re
import json
import unicodedata


# take the uri and try and find soemthing useful about it
        
# get http://channelography.rattlecentral.com/programmes/b00ncr13/captions.xml
# get alt
#<channelography>
#<captions>
#<link rel="alternate" href="http://www.bbc.co.uk/iplayer/subtitles/b000ncr0mh264_high_131515215.xml"/>
# look for begin and end
#<tt><body><div><p  begin="0:00:21.200" end="0:00:22.720"
# find one in the region of the secs we have
#print them out

class Subs():

  def __init__(self):
     pass

  def get_subs(self,pid_or_url, num_secs,num_subs):
     to_return=[]
     num_subs = int(num_subs)
     use_channelography=True
     begins=[]
     begins_as_secs = []
     subs=[]
     print "got pid",pid_or_url
     pid_match = re.match('.*?\/?([b-df-hj-np-tv-z][0-9b-df-hj-np-tv-z]{7,15}).*?',pid_or_url) 
     pid = pid_match.group(1)
     print "Looking for subs for ",pid
     num_secs = float(num_secs)
     links = None

     if use_channelography:
        u = "http://channelography.rattlecentral.com/programmes/"+pid+"/captions.xml"
        print "Getting channelography url",u
        data = urllib.urlopen(u).read()    
        xmldoc = minidom.parseString(data)
        links = xmldoc.getElementsByTagName('link')
# sometimes there is no channelography url
# in which case we can get the version from the rdf and then use
# http://www.bbc.co.uk/mediaselector/4/mtis/stream/b00rybrs
# <connection href="http://www.bbc.co.uk/iplayer/subtitles/ng/b00r/ybrs/b00rybrs_live.xml"
#    print "List of links size:",len(links)

# list of 'p's that we get from the subtitltes url, once we have found it
     plist = None

# if we didn't find anything from chanelograhy we go to iplayer direct

     if (links and links[0]):
       print "Channelography url found"
       u2 = links[0].attributes["href"].value
       print "iPlayer subs url",u2
       data2 = urllib.urlopen(u2).read()    
       try:
          xmldoc2 = minidom.parseString(data2)
          plist = xmldoc2.getElementsByTagNameNS('http://www.w3.org/2006/10/ttaf1','p')
       except ExpatError, e:
          print "Error:",e
     else:
# no channelography url found
# rdf url
       print "Nothing found in channelography - looking for iplayer subs urls"
       u3 = "http://www.bbc.co.uk/programmes/"+pid+".rdf"
# get the version
       print "Getting the RDF data to find the version:",u3
       data3 = urllib.urlopen(u3).read()
       xmldoc3 = minidom.parseString(data3)
       ver = xmldoc3.getElementsByTagNameNS('http://purl.org/ontology/po/','version') 
       if (len(ver)==0):
          print "No Version found - did you use a programmes pid?",pid
       else:
          ver_pid_url = ver[0].getAttributeNS("http://www.w3.org/1999/02/22-rdf-syntax-ns#","resource")

# get the pid and make the new iplayer url
          ver_pid_match = re.match('.*\/([b-df-hj-np-tv-z][0-9b-df-hj-np-tv-z]{7,15}).*?',ver_pid_url) 
          vpm = ver_pid_match.group(1)
          u4 = "http://www.bbc.co.uk/mediaselector/4/mtis/stream/"+vpm

          print "Downloading the iplayer version url",u4

          data4 = urllib.urlopen(u4).read()
          xmldoc4 = minidom.parseString(data4)
          conn = xmldoc4.getElementsByTagName("connection")

          href = None
          for c in conn:
          # pick out the links we want
             if c.getAttribute("kind")=="http":
                if c.getAttribute("href"):
                   h=c.getAttribute("href")
                   href = h
                   print "Found a subs url ",href
                   data5 = urllib.urlopen(href).read()
                   xmldoc5 = minidom.parseString(data5)
                   plist = xmldoc5.getElementsByTagName('p')
                   #print data5
                   break

# We managed to find some subtitles

     if (plist):

# get all the start times, put them in an array and use that to search or something?
# convert them to secs first

       for x in plist:
          beg = x.attributes["begin"].value
          begins.append(beg)
          arr = beg.split(":")
          secs = int(arr[0])*360+int(arr[1])*60+float(arr[2])
          begins_as_secs.append(secs)
          txt = ""
          children = x.childNodes

# sometimes the subs are wrapped in <span and similar
          for y in children:
             if y.nodeType == y.TEXT_NODE:
                txt = txt + y.data
             else:
                if(y.firstChild!=None):
                   txt = txt + " "+y.firstChild.data
          subs.append(txt)
     
# loop through our list and find the first one that's as big or bigger
# than num_secs
     sub_index = 0
     last_secs = -1
     print "looking for subtitles around secs:",num_secs 
     for x in begins_as_secs:
         last_secs = x
         if x > num_secs:
            print "matched",num_secs,"with",x                        
            break
         sub_index = sub_index+1

     if(last_secs == -1):
        print "No subtitles found for",pid
     else:
        if(last_secs < num_secs):
           print "Sorry - max secs for ",pid,"is",last_secs
        else:
           if len(begins_as_secs) > 0:
              substext=""
#             print "subs length is:",len(subs),"sub index is:",sub_index
              print "[["
# get the subs around this point
              c = int( num_subs / 2 )
              min_sub = sub_index - c
              r = num_subs % 2
              max_sub = sub_index + c
              if (r > 0):
                 max_sub = max_sub + 1
# if min_sub < 0 or 
# if max_sub is greater than len(subs)
# sort it out!
              if min_sub < 0:
                 diff = min_sub
                 max_sub = min_sub + diff
              if max_sub > len(subs):
                 diff = len(subs) - max_sub
                 max_sub = len(subs) 

              for i in range(min_sub,max_sub):
                  print i," ",subs[i]
                  substext = substext + " " + subs[i]

              print "]]"   
              to_return.append(substext)

              # get lupedia entities

              print "\nLupedia entities:"
              lup_data = self.get_lupedia_entities(substext)
              lup_arr=[]
              if(lup_data==None or len(lup_data)==0):
                 print "No Lupedia entities found"             
              for r in lup_data:
                 print "tag",r
                 lup_arr.append(r)
              print "\nRegexed entities:"
              # get regexed entities
              regex_arr=[]
              regexed_entities = self.get_regexed_entities(substext)
            
              if(regexed_entities==None or len(regexed_entities)==0):
                 print "No entities found"             
              for r in regexed_entities:
                 print "tag",r
                 regex_arr.append(r)                 
              to_return.append(lup_arr)
              to_return.append(regex_arr)
           else:
              print "No subtitles found for",pid
     return to_return

# Ask Lupedia for entities

  def get_lupedia_entities(self,substext):

# Read items from stoplist
     f = open('stopList.txt', 'r')
     stopList = []
     for line in f:
        li = re.sub("\n","", line)
        if li!="":
           stopList.append(li)

# experimentally remove the stop list words
# note this is a diferent technique to with the regex, which removes them after terms are found

     words = []
    
     arr = substext.split(" ")
     for x in arr:
        if x not in stopList:
           words.append(x)

     substext2 = " ".join(words)
     substext2 = unicode(substext2)

# lupedia only accepts ascii 
     ascii_substext = unicodedata.normalize('NFKD', substext2).encode('ascii','ignore')
     u6 = "http://lupedia.ontotext.com/lookup/text2json?lookupText="+ascii_substext
     data6 = urllib.urlopen(u6).read()
     json_text = json.loads(data6)              

     final_words = []
     for x in json_text:
        for y in x:
           for k, v in y.items():
              #print "k",k,"v",v
              if k=="instanceUri":
                 tag = v
                 tag = re.sub("http://","",tag)
                 tag = re.sub(".org",":",tag)
                 tag = re.sub("/resource/","",tag)
                 final_words.append(tag)
                 if k=="instanceClass":
                    print "class",v

     return final_words


# Baseline extra-simple regex-based entity regognition

  def get_regexed_entities(self,substext):

# Read items from stoplist
     f = open('stopList.txt', 'r')
     stopList = []
     for line in f:
        li = re.sub("\n","", line)
        if li!="":
           stopList.append(li)

     substext = re.sub("  "," ",substext)
     substext = re.sub("   "," ",substext)

     words = re.findall("(([A-Z][a-z]*[ |,|.]){1,})",substext)

     wordslist = []
     for x in words:
       w = x[0]
       w = re.sub(",","",w)
       w = re.sub("\.","",w)
       wordslist.append(w)

# remove stop words
     final_wordslist= []

     for x in wordslist:
        arr = x.split(" ")
        for y in arr:
           z = y.lower()
           if z in stopList:
              x = re.sub(y, "", x)
        term_name = re.sub("^\s*","",x)
        term_name = re.sub("\s*$","",term_name)
        if term_name!="" and term_name not in final_wordslist:
# now do a dbpedia lookup
          tn = re.sub(" ","_",term_name)
          term_url = "http://dbpedia.org/page/"+tn
          req = urllib2.Request(term_url)
          try:
             u = urllib2.urlopen(req)
             if "dbpedia:"+tn not in final_wordslist:
                final_wordslist.append("dbpedia:"+tn)
          except urllib2.HTTPError, e:
#            print e.code
             if term_name not in final_wordslist:
                final_wordslist.append(term_name)

#  print "XXXX",final_wordslist
     return final_wordslist


if len(sys.argv) > 2:
   s = Subs()
   if len(sys.argv) == 3:
      print s.get_subs(sys.argv[1],sys.argv[2],3)
   if len(sys.argv) > 3:
      print s.get_subs(sys.argv[1],sys.argv[2],sys.argv[3])
else:
   print "Usage: python subs.py pid_or_url secs [num_subs]"
   print "e.g. python subs.py b00ncr13 200"
   print "or python subs.py http://www.bbc.co.uk/programmes/b00s0vrj.rdf 500 4"
