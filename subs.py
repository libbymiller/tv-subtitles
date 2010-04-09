import urllib
from xml.dom import minidom
import sys
import re

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
     begins=[]
     begins_as_secs = []
     subs=[]
     pid_match = re.match('.*\/([b-df-hj-np-tv-z][0-9b-df-hj-np-tv-z]{7,15}).*?',pid_or_url) 
     pid = pid_match.group(1)
     print "pid",pid
     num_secs = float(num_secs)
     u = "http://channelography.rattlecentral.com/programmes/"+pid+"/captions.xml"
     data = urllib.urlopen(u).read()    
     xmldoc = minidom.parseString(data)
     links = xmldoc.getElementsByTagName('link')
     if (links and links[0]):
       u2 = links[0].attributes["href"].value
       data2 = urllib.urlopen(u2).read()    
       xmldoc2 = minidom.parseString(data2)
       plist = xmldoc2.getElementsByTagNameNS('http://www.w3.org/2006/10/ttaf1','p')

#perhaps get all the start times, put them in an array and use that to search or something?
#convert them to secs first

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
     last_secs = 0
     print "looking for subtitles around secs:",num_secs 
     for x in begins_as_secs:
         last_secs = x
         if x > num_secs:
            print "matched",num_secs,"with",x                        
            break
         sub_index = sub_index+1
     if(last_secs < num_secs):
         print "Sorry - max secs for ",pid,"is",last_secs
     else:

        if len(begins_as_secs) > 0:
           print "subs length is:",len(subs),"sub index is:",sub_index
           print "Subtitle near",num_secs,"in was:",subs[sub_index]
           print "Previous subtitle was:",subs[sub_index-1]
           if(len(subs)>sub_index+1):
              print "Next subtitle was:",subs[sub_index+1]
        else:
           print "No subtitles found for",pid


if len(sys.argv) > 2:
   get_subs(sys.argv[1],sys.argv[2])
else:
   print "Usage: python subs.py pid secs"
   print "e.g. python subs.py b00ncr13 200"
