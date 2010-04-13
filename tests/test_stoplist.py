import re


f = open('stopList.txt', 'r')
stopList = []
for line in f:
   li = re.sub("\n","", line)
   if li!="":
      stopList.append(li)
#print stopList

text = "if you want. Poland a good piece, the  Observer has a good piece on that. The Sunday Times, Labour hit by  cancer leaflet row. And Brown has blocked a peerage for the head of  the Army, Richard Dannatt."

words = re.findall("(([A-Z][a-z]*[ |  |,|.]){1,})",text)

wordslist = []
for x in words:
   w = x[0]
   print w
   w = re.sub(",","",w)
   w = re.sub("\.","",w)
   print w
   wordslist.append(w)  
print "removing stop words"
final_wordslist= []  

for x in wordslist:
   print " x",x
   arr = x.split(" ")
   ok = True
   for y in arr:
      z = y.lower()
      if z in stopList:
#        ok = False
         x = re.sub(y, "", x) 
   if ok:
      final_wordslist.append(x)

print "XXXX",final_wordslist


