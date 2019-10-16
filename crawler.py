#!/usr/bin/python3
# -*- coding: utf-8 -*-


#fix hashtag recognition - using base, it thinks a hashtag reference on a page is a new page, but second/(hashtag)grid is not a new page, but a part of second, meaning redirects to parent page (wrong page)
#remove duplicate pages (mainly due to above hashtag issues, should clear up if fixed). Compare HTML code, if same, discard new found link
#upload results to mySQL database - probably best during printtofile method

import mysql.connector

from bs4 import BeautifulSoup, SoupStrainer
from bs4.element import Comment
import httplib2
import subprocess
from subprocess import call
import os
from os.path import splitext
import sys
import time
import requests

#try:
#    import urllib.request as urllib2
#except ImportError:
#    import urllib.request, urllib.error, urllib.parse
import re
#try:
#    from urllib.parse import urlparse
#except ImportError:
#    from urllib.parse import urlparse

call(["sudo", "service", "mysql", "start"])

hostname = 'localhost'
username = 'root'
password = ''
database = 'testcrawler'

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = list(filter(tag_visible, texts))
    return ((' '.join((" ".join(t.strip() for t in visible_texts)).split())).encode('ascii', 'ignore')).replace("'", "\\'")

myConnection = mysql.connector.connect(host=hostname, user=username, passwd=password, db=database, charset="utf8", use_unicode=True)

def addLinkQuery(lk, bdy, li):
    #ignore bdy
    global myConnection
    cur = myConnection.cursor()
    query = "INSERT INTO links (Link, LinkId) VALUES ('" + str(lk) + "', '" + str(li) + "')"
    cur.execute(str(query).encode('utf-8'))
    myConnection.commit()

def addRefQuery(li, ri):
    global myConnection
    cur = myConnection.cursor()
    query = "INSERT INTO refs (LinkId, RefId) VALUES ('" + str(li) + "', '" + str(ri) + "')"
    cur.execute(str(query).encode('utf-8'))
    myConnection.commit()

def addBodyQuery(li, bdy):
    #figure out encoding for bdy?
    global myConnection
    cur = myConnection.cursor()
    query = "UPDATE links SET Body = '" + str(bdy) + "' WHERE LinkId = " + str(li)
    cur.execute(str(query))
    myConnection.commit()

def getQuery():
    print("Nothing right now.")

innerlinks = []

innertext = []

innerrefs = []

outerlinks = []

outertext = []

outerrefs = []

alllinks = []

linkids = []

idnumber = 0

linktype = []

pointininnerorouter = []

base = "http://nathandharris.com"

baseslash = base + "/"

linklocations = [[]]

http = httplib2.Http()

http.force_exception_to_status_code = False

temphref = "";

currentdomain = "";

html = "";

#start = time.time()

pagebody = ""

try:
    status, response = http.request(base)
    innerlinks.append(base)
    pagebody = text_from_html(response)
    innertext.append(pagebody)
    innerrefs.append([])
    alllinks.append(base)
    linkids.append(idnumber)
    linktype.append("I")
    addLinkQuery(base, pagebody, idnumber)
    addBodyQuery(idnumber, pagebody)
    idnumber += 1
except httplib2.ServerNotFoundError:
    print "First webpage unreachable. Quitting..."
    sys.exit(0)



isInnerLink = True;

refloc = 0


def referencebase(thelink):
    global isInnerLink
    global innerlinks
    global innerrefs
    global outerlinks
    global outerrefs
    if isInnerLink == True:
        refloc = innerlinks.index(thelink)
        #print refloc
        while refloc > (len(innerrefs) - 1):
            innerrefs.append([])
        #print len(innerrefs)
        if base not in innerrefs[refloc]:
            innerrefs[refloc].append(base)
            print "Upload dummy for Table 2:"
            print "Linkid: ", linkids[alllinks.index(thelink)], ", Refid: ", linkids[alllinks.index(base)]
            addRefQuery(linkids[alllinks.index(thelink)], linkids[alllinks.index(base)])
        #print "The link: ", thelink
        print "What webpages reference this link: ", innerrefs[refloc]
    else:
        refloc = outerlinks.index(thelink)
        while refloc > (len(outerrefs) - 1):
            outerrefs.append([])
        if base not in outerrefs[refloc]:
            outerrefs[refloc].append(base)
            print "Upload dummy for Table 2:"
            print "Linkid: ", linkids[alllinks.index(thelink)], ", Refid: ", linkids[alllinks.index(base)]
            addRefQuery(linkids[alllinks.index(thelink)], linkids[alllinks.index(base)])
        #print "The link: ", thelink
        print "What webpages reference this link: ", outerrefs[refloc]
    print("")

def referencenotbase(thelink,thepage, isNew):
    global isInnerLink
    global innerlinks
    global innerrefs
    global outerlinks
    global outerrefs
    if isInnerLink == True:
        refloc = innerlinks.index(thelink)
        while refloc > (len(innerrefs) - 1):
            innerrefs.append([])
        if thepage not in innerrefs[refloc]:
            innerrefs[refloc].append(thepage)
            print "Upload dummy for Table 2:"
            print "Linkid: ", linkids[alllinks.index(thelink)], ", Refid: ", linkids[alllinks.index(thepage)]
            addRefQuery(linkids[alllinks.index(thelink)], linkids[alllinks.index(thepage)])
        #print "The link: ", thelink
        if isNew == True:
            print "What webpages reference this link: ", innerrefs[refloc]
    else:
        refloc = outerlinks.index(thelink)
        while refloc > (len(outerrefs) - 1):
            outerrefs.append([])
        if thepage not in outerrefs[refloc]:
            outerrefs[refloc].append(thepage)
            print "Upload dummy for Table 2:"
            print "Linkid: ", linkids[alllinks.index(thelink)], ", Refid: ", linkids[alllinks.index(thepage)]
            addRefQuery(linkids[alllinks.index(thelink)], linkids[alllinks.index(thepage)])
        #print "The link: ", thelink
        if isNew == True:
            print "What webpages reference this link: ", outerrefs[refloc]
    print("")

def printtofile():
    global innerlinks
    global innerrefs
    global outerlinks
    global outerrefs
    f = open("links.txt","w")
    f.write("Internal links: ")
    for i in range(0, len(innerlinks)):
        f.write("\n")
        f.write(str(linkids[alllinks.index(innerlinks[i])]))
        f.write(" - ")
        f.write(str(innerlinks[i]))
        f.write(" --- References:")
        f.write(str(innerrefs[i]))
    f.write("\n\n")
    f.write("\nExternal links: ")
    for i in range(0, len(outerlinks)):
        f.write("\n")
        f.write(str(linkids[alllinks.index(outerlinks[i])]))
        f.write(" - ")
        f.write(str(outerlinks[i]))
        f.write(" --- References:")
        f.write(str(outerrefs[i]))


#Initial page

print "Parsing the initial page: ", base
for link in BeautifulSoup(response, "html.parser", parse_only=SoupStrainer('a')):
    if link.has_attr('href'):
        temphref = link.get('href')
        if not temphref.startswith("mailto:") and not temphref.startswith("tel:"):
            if temphref.startswith("http://") or temphref.startswith("https://") or temphref.startswith("www."):
                if temphref.startswith(base):
                    isInnerLink = True
                    if temphref not in innerlinks:
                        innerlinks.append(temphref)
                        alllinks.append(temphref)
                        linkids.append(idnumber)
                        addLinkQuery(temphref, pagebody, idnumber)
                        idnumber += 1
                        linktype.append("I")
                        pointininnerorouter.append(len(innerlinks)-1)
                        referencebase(temphref)
                else:
                    isInnerLink = False
                    if temphref not in outerlinks:
                        outerlinks.append(temphref)
                        alllinks.append(temphref)
                        linkids.append(idnumber)
                        addLinkQuery(temphref, pagebody, idnumber)
                        idnumber += 1
                        linktype.append("E")
                        pointininnerorouter.append(len(outerlinks)-1)
                        referencebase(temphref)
            else:
                isInnerLink = True
                if temphref.startswith("/"):
                    temphref = base + temphref
                    if temphref not in innerlinks:
                        innerlinks.append(temphref)
                        alllinks.append(temphref)
                        linkids.append(idnumber)
                        addLinkQuery(temphref, pagebody, idnumber)
                        idnumber += 1
                        linktype.append("I")
                        pointininnerorouter.append(len(innerlinks)-1)
                        referencebase(temphref)
                else:
                    temphref = baseslash + temphref
                    if temphref not in innerlinks:
                        innerlinks.append(temphref)
                        alllinks.append(temphref)
                        linkids.append(idnumber)
                        addLinkQuery(temphref, pagebody, idnumber)
                        idnumber += 1
                        linktype.append("I")
                        pointininnerorouter.append(len(innerlinks)-1)
                        referencebase(temphref)

print("All internal links: ",innerlinks)
print("")
print("All external links: ",outerlinks)
#for x in range(0, len(innerlinks[7].split('/')) - 1):
#    if x == 0:
#        test = innerlinks[7].split('/')[0]
#    else:
#        test = test + "/" + innerlinks[7].split('/')[x]
#test = test + '/'
#print test
stop = False
i = 1
templink = ""
tempadd = ""

#sys.exit(0)

#Crawl the starting domain (inner links)
print("\nParsing the internal links")

f = open("links.txt","w")
f.write("")

while not stop:
    while innerlinks[i].startswith("mailto:") or innerlinks[i].startswith("tel:") or innerlinks[i].endswith(".mp4"):
        i = i + 1
        innertext.append("")
    for x in range(0, len(innerlinks[i].split('/')) - 1):
        if x == 0:
            currentdomain = innerlinks[i].split('/')[0]
        else:
            currentdomain = currentdomain + "/" + innerlinks[i].split('/')[x]
    currentdomainslash = currentdomain + '/'
    #currentdomain = urlparse(innerlinks[i])[0] + "://" + urlparse(innerlinks[i])[1]
    #currentdomainslash = currentdomain + "/"
    print("")
    print("Current domain", currentdomain)
    if (not innerlinks[i].startswith("http://") and not innerlinks[i].startswith("https://") and not innerlinks[i].startswith("www.")) and (".co" not in innerlinks[i] and ".org" not in innerlinks[i] and ".net" not in innerlinks[i] and ".gov" not in innerlinks[i] and ".edu" not in innerlinks[i]):
    #Link is a relative link, with no domain, meaning the link would belong to the same current domain
    #THIS WON'T WORK LOGICALLY. IF IT DOESN'T HAVE A DOMAIN, IT WOULDN'T HAVE EXTRACTED A DOMAIN FOR CURRENTDOMAIN, AND THEREFORE STILL WON'T RECEIVE A PROPER DOMAIN.
    #SHOULDN'T MATTER ANYMORE. YEAH, IT'S A LOGICAL LOOP, BUT ALL LINKS WITHOUT DOMAINS HAVE DOMAINS ADDED BEFORE THEY'RE PLACED IN THE LIST, SO THERE SHOULD NEVER BE A LINK WITHOUT A DOMAIN IN FRONT OF IT.
        if innerlink[i].startswith("/"):
            templink = currentdomain + innerlinks[i]
        else:
            templink = currentdomainslash + innerlinks[i]
    elif innerlinks[i].startswith("//"):
    #Bug fix for missing http(s), using same as current domain
        templink = urlparse(innerlinks[i])[0] + innerlinks[i]
    else:
    #FROM THE FIRST PASS, SINCE THEY ALL RECEIVE THE BASE DOMAIN, ALL OF THEM GO TO THIS STEP
        templink = innerlinks[i]
    print("Parsing page", templink)
    try:
        status, response = http.request(templink)
        pagebody = text_from_html(response)
        innertext.append(pagebody)
        addBodyQuery(linkids[alllinks.index(templink)], pagebody)
        linksfoundhere = 0
        newlinkhere = 0
        for link in BeautifulSoup(response, "html.parser", parse_only=SoupStrainer('a')):
            if link.has_attr('href'):
                temphref = link.get('href')
                if not temphref.startswith("mailto:") and not temphref.startswith("tel:"):
                    linksfoundhere += 1
                    isNew = False
                    if temphref.startswith("http://") or temphref.startswith("https://") or temphref.startswith("www."):
                        if temphref.startswith(base):
                            isInnerLink = True
                            if temphref not in innerlinks:
                                newlinkhere += 1
                                isNew = True
                                innerlinks.append(temphref)
                                alllinks.append(temphref)
                                linkids.append(idnumber)
                                addLinkQuery(temphref, pagebody, idnumber)
                                idnumber += 1
                                linktype.append("I")
                                pointininnerorouter.append(len(innerlinks)-1)
                                print("Found internal link", temphref)
                                #referencenotbase(temphref,templink)
                            #innerlinks.append(temphref)
                            referencenotbase(temphref,templink, isNew)
                        else:
                            isInnerLink = False
                            if temphref not in outerlinks:
                                newlinkhere += 1
                                isNew = True
                                outerlinks.append(temphref)
                                alllinks.append(temphref)
                                linkids.append(idnumber)
                                addLinkQuery(temphref, pagebody, idnumber)
                                idnumber += 1
                                linktype.append("E")
                                pointininnerorouter.append(len(outerlinks)-1)
                                print("Found external link", temphref)
                                #referencenotbase(temphref,templink)
                            #outerlinks.append(temphref)
                            referencenotbase(temphref,templink, isNew)
                    else:
                        isInnerLink = True
                        if temphref.startswith("/"):
                            temphref = currentdomain + temphref
                            if temphref not in innerlinks:
                                newlinkhere += 1
                                isNew = True
                                innerlinks.append(temphref)
                                alllinks.append(temphref)
                                linkids.append(idnumber)
                                addLinkQuery(temphref, pagebody, idnumber)
                                idnumber += 1
                                linktype.append("I")
                                pointininnerorouter.append(len(innerlinks)-1)
                                print("Found internal link", temphref)
                                #referencenotbase(temphref,templink)
                            #innerlinks.append(temphref)
                            referencenotbase(temphref,templink, isNew)
                        else:
                            temphref = currentdomainslash + temphref
                            if temphref not in innerlinks:
                                newlinkhere += 1
                                isNew = True
                                innerlinks.append(temphref)
                                alllinks.append(temphref)
                                linkids.append(idnumber)
                                addLinkQuery(temphref, pagebody, idnumber)
                                idnumber += 1
                                linktype.append("I")
                                pointininnerorouter.append(len(innerlinks)-1)
                                print("Found internal link", temphref)
                                #referencenotbase(temphref,templink)
                            #innerlinks.append(temphref)
                            referencenotbase(temphref,templink, isNew)
        #print(linksfoundhere), "links found here."
        #print(newlinkhere), "new links found here."
        print((len(innerlinks) - 1), "total internal links collected.")
        print((len(outerlinks) - 1), "total external links collected.")
        printtofile()
    except httplib2.ServerNotFoundError:
        print("Link unreachable. Skipping...")
        innertext.append("LINK UNREACHABLE.")
    except httplib2.RedirectLimit:
        print("Too many redirects. Skipping...")
        innertext.append("TOO MANY REDIRECTS.")
    if (len(innerlinks) - 1) == i:
        stop = True
        print("")
        #print innerlinks
        #print innertext
        #print outerlinks
        #totallinks.extend(innerlinks)
        #print totallinks
        #for t in range(0, len(innerlinks) - 1):
            #print ""
            #print innerlinks[t], ': ', innertext[t], "\n"
    else:
        i = i + 1

stop = False
i = 0
templink = ""
tempadd = ""

#print "What webpages reference http://nathandharris.com: ", innerrefs[0]
#print "Testing arrays:"
#print alllinks
#pointinalllinks = len(alllinks)-1
#print "Last link: ",alllinks[pointinalllinks]
#print "Place in alllinks: ",pointinalllinks
#thelinkid = linkids[pointinalllinks]
#print "Id: ",thelinkid
#type = str(linktype[pointinalllinks])
#print "Type: ",type
#if type == "I":
#    print "The HTML code of this page: ",innertext[pointininnerorouter[pointinalllinks]]
#    print "What pages have this link on them: ",innerrefs[pointininnerorouter[pointinalllinks]]
#else:
#    print "The HTML code of this page: ",outertext[pointininnerorouter[pointinalllinks]]
#    print "What pages have this link on them: ",outerrefs[pointininnerorouter[pointinalllinks]]
#sys.exit(0)

#Crawl external links
print("\nParsing the external links")

while not stop:
    while outerlinks[i].startswith("mailto:") or outerlinks[i].startswith("tel:"):
        i = i + 1
    for x in range(0, len(outerlinks[i].split('/')) - 1):
        if x == 0:
            currentdomain = outerlinks[i].split('/')[0]
        else:
            currentdomain = currentdomain + "/" + outerlinks[i].split('/')[x]
    if currentdomain == "http:/" or currentdomain == "https:/":
        currentdomain = outerlinks[i]
    currentdomainslash = currentdomain + '/'
    #currentdomain = urlparse(outerlinks[i])[0] + "://" + urlparse(outerlinks[i])[1]
    #currentdomainslash = currentdomain + "/"
    print("")
    print("Current domain", currentdomain)
    if (not outerlinks[i].startswith("http://") and not outerlinks[i].startswith("https://") and not outerlinks[i].startswith("www.")) and (".co" not in outerlinks[i] and ".org" not in outerlinks[i] and ".net" not in outerlinks[i] and ".gov" not in outerlinks[i] and ".edu" not in outerlinks[i]):
    #Link is a relative link, with no domain, meaning the link would belong to the same current domain
    #THIS WON'T WORK LOGICALLY. IF IT DOESN'T HAVE A DOMAIN, IT WOULDN'T HAVE EXTRACTED A DOMAIN FOR CURRENTDOMAIN, AND THEREFORE STILL WON'T RECEIVE A PROPER DOMAIN.
        if outerlink[i].startswith("/"):
            templink = currentdomain + outerlinks[i]
        else:
            templink = currentdomainslash + outerlinks[i]
    elif outerlinks[i].startswith("//"):
    #Bug fix for missing http(s), using same as current domain
        templink = urlparse(outerlinks[i])[0] + outerlinks[i]
    else:
    #FROM THE FIRST PASS, SINCE THEY ALL RECEIVE THE BASE DOMAIN, ALL OF THEM GO TO THIS STEP
        templink = outerlinks[i]
    print("Parsing page", templink,", referred to by:", outerrefs[i])
    try:
        status, response = http.request(templink)
        pagebody = text_from_html(response)
        outertext.append(pagebody)
        addBodyQuery(linkids[alllinks.index(templink)], pagebody)
        for link in BeautifulSoup(response, "html.parser", parse_only=SoupStrainer('a')):
            if link.has_attr('href'):
                temphref = link.get('href')
                if not temphref.startswith("mailto:") and not temphref.startswith("tel:"):
                    isNew = False
                    if temphref.startswith("http://") or temphref.startswith("https://") or temphref.startswith("www."):
                        if temphref.startswith(base):
                            isInnerLink = True
                            if temphref not in innerlinks:
                                isNew = True
                                innerlinks.append(temphref)
                                alllinks.append(temphref)
                                linkids.append(idnumber)
                                addLinkQuery(temphref, pagebody, idnumber)
                                idnumber += 1
                                linktype.append("I")
                                pointininnerorouter.append(len(innerlinks)-1)
                                print("Found new internal link", temphref)
                                #referencenotbase(temphref,templink)
                            #innerlinks.append(temphref)
                            referencenotbase(temphref,templink, isNew)
                        else:
                            isInnerLink = False
                            if temphref not in outerlinks:
                                isNew = True
                                outerlinks.append(temphref)
                                alllinks.append(temphref)
                                linkids.append(idnumber)
                                addLinkQuery(temphref, pagebody, idnumber)
                                idnumber += 1
                                linktype.append("E")
                                pointininnerorouter.append(len(outerlinks)-1)
                                print("Found external link", temphref)
                                #referencenotbase(temphref,templink)
                            #outerlinks.append(temphref)
                            referencenotbase(temphref,templink, isNew)
                    else:
                        isInnerLink = False
                        if temphref.startswith("/"):
                            temphref = currentdomain + temphref
                            if temphref not in outerlinks:
                                isNew = True
                                outerlinks.append(temphref)
                                alllinks.append(temphref)
                                linkids.append(idnumber)
                                addLinkQuery(temphref, pagebody, idnumber)
                                idnumber += 1
                                linktype.append("E")
                                pointininnerorouter.append(len(outerlinks)-1)
                                print("Found external link", temphref)
                                #referencenotbase(temphref,templink)
                            #outerlinks.append(temphref)
                            referencenotbase(temphref,templink, isNew)
                        else:
                            temphref = currentdomainslash + temphref
                            if temphref not in outerlinks:
                                isNew = True
                                outerlinks.append(temphref)
                                alllinks.append(temphref)
                                linkids.append(idnumber)
                                addLinkQuery(temphref, pagebody, idnumber)
                                idnumber += 1
                                linktype.append("E")
                                pointininnerorouter.append(len(outerlinks)-1)
                                print("Found external link", temphref)
                                #referencenotbase(temphref,templink)
                            #outerlinks.append(temphref)
                            referencenotbase(temphref,templink, isNew)

        print((len(innerlinks) - 1), "total internal links collected.")
        print((len(outerlinks) - 1), "total external links collected.")
        printtofile()
        print("Reminder of what page(s) refer to ", templink, ": ", outerrefs[i])
    except httplib2.ServerNotFoundError:
        print("Link unreachable. Skipping...")
        outertext.append("LINK UNREACHABLE.")
    except httplib2.RedirectLimit:
        print("Too many redirects. Skipping...")
        outertext.append("TOO MANY REDIRECTS.")
    if (len(outerlinks) - 1) == i:
        stop = True
        #print innerlinks
        #print outerlinks
        #totallinks.extend(outerlinks)
        #print totallinks
    else:
        i = i + 1

#end = time.time()
#time1 = end - start
#print len(links)
#print('httplib2 time: ', end - start)




#links = []

#start = time.time()

#html_page = urllib2.urlopen(base)
#soup = BeautifulSoup(html_page, "html.parser", parse_only=SoupStrainer('a'))

#for link in soup:
#    if link.has_attr('href'):
#        links.append(link.get('href'))

#end = time.time()
#time2 = end - start
#print(len(links))
#print('urllib2 time: ', end - start)


#links = []

#start = time.time()
#resp = requests.get(base)

#for link in BeautifulSoup(resp.content, "html.parser", parse_only=SoupStrainer('a')):
#    if link.has_attr('href'):
#        links.append(link.get('href'))

#end = time.time()
#time3 = end - start
#print(len(links))
#print('Requests time: ', end - start)

#if time1 < time2 and time1 < time3:
#    print('httplib2 wins.')
#elif time2 < time3:
#    print('urllib2 wins.')
#else:
#    print('Requests wins.')
