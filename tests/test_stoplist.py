#!/usr/bin/env python

import re


f = open('../stopList.txt', 'r')
stopList = []
for line in f:
   li = re.sub("\n","", line)
   if li!="":
      stopList.append(li)
#print stopList

text = "if you want. Poland a good piece, the  Observer has a good piece on that. The Sunday Times, Labour hit by  cancer leaflet row. And Brown has blocked a peerage for the head of  the Army, Richard Dannatt."
text = "    be earning more than the Prime  Minister when maternity wards are    threatened with closure. Let us  look at another policy, which you    say is aimed at reducing inequality.  The people premium. It is that    policy by which schools would be  paid an extra premium on account of    the number of very poor children  they have attending there. Do you    know what that would bring in?  Proportionally, to the amount of    money they are presently receiving,  less than other schools. Some    schools bring in nothing at all.  The figure is 50 quid in Hackney.    Hour cut relations are of that for  the million children from the    poorest background, it represents,  at 2,500 additional spending."

text = re.sub("  "," ",text)
text = re.sub("   "," ",text)

words = re.findall("(([A-Z][a-z]*[ |,|.]){1,})",text)

wordslist = []
for x in words:
   w = x[0]
   w = re.sub(",","",w)
   w = re.sub("\.","",w)
   wordslist.append(w)  
print "removing stop words"
final_wordslist= []  

for x in wordslist:
#   print " x",x
   arr = x.split(" ")
   ok = True
   for y in arr:
      z = y.lower()
      if z in stopList:
#        ok = False
         x = re.sub(y, "", x) 
   if ok:
      final_wordslist.append(x)

print text,"\n"

print "XXXX",final_wordslist


