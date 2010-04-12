import urllib
from xml.dom import minidom
import sys
import re
import json


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

def get_subs(pid_or_url, num_secs):
     use_channelography=True
     begins=[]
     begins_as_secs = []
     subs=[]
     pid_match = re.match('.*\/([b-df-hj-np-tv-z][0-9b-df-hj-np-tv-z]{7,15}).*?',pid_or_url) 
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
       xmldoc2 = minidom.parseString(data2)
       plist = xmldoc2.getElementsByTagNameNS('http://www.w3.org/2006/10/ttaf1','p')

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
#              print "subs length is:",len(subs),"sub index is:",sub_index
#              print "Subtitle near",num_secs,"in was:",subs[sub_index]
#              print "Previous subtitle was:",subs[sub_index-1]
              print "[["
              print subs[sub_index-1]," ",subs[sub_index]
              substext= substext+subs[sub_index-1]
              substext= substext+subs[sub_index]
              if(len(subs)>sub_index+1):
                 print subs[sub_index+1]
                 substext= substext+subs[sub_index+1]
              print "]]"   
              u6 = "http://lupedia.ontotext.com/lookup/text2json?lookupText="+substext
              data6 = urllib.urlopen(u6).read()
              json_text = json.loads(data6)              
              for x in json_text:
                 for y in x:
                    for k, v in y.items():
                       #print "k",k,"v",v
                       if k=="instanceUri":
                          tag = v
                          tag = re.sub("http://","",tag)
                          tag = re.sub(".org",":",tag)
                          tag = re.sub("/resource/","",tag)
                          print "tag",tag
                       if k=="instanceClass":
                          print "class",v
           else:
              print "No subtitles found for",pid


if len(sys.argv) > 2:
   get_subs(sys.argv[1],sys.argv[2])
else:
   print "Usage: python subs.py pid_or_url secs"
   print "e.g. python subs.py b00ncr13 200"
   print "or python subs.py http://www.bbc.co.uk/programmes/b00s0vrj.rdf 500"
