#!/usr/bin/python3

import urllib.parse as uparse
from bs4 import BeautifulSoup as bs
import requests
import sys
import argparse
import os

help_message = "USAGE: crawler.py [starting URL] [r - restrict scraping to starting domain]"

base_url="http://domain.com"
keep_within_domains = []
restrict_to_domains = False
save_pages = False
if len(sys.argv) > 1:
    if "help" in sys.argv or "h" in sys.argv:
        print(help_message)
        sys.exit(0)
if len(sys.argv) >= 1:
    base_url = "http://" + sys.argv[1]
if len(sys.argv) >= 2:
    if any(f in sys.argv for f in ['r','restrict','res']):
        restrict_to_domains = True
        keep_within_domains.append(sys.argv[1])
    if any(f in sys.argv for f in ['save','s']):
        save_pages = True

tree = {}
# Structure:
# tree[found_url] = [pages_where_url_was_found]

found_links = []

ignore_exts = ['png','jpg','peg','mp4','mkv','avi','mov','swf','pdf']

with open('crawler_dict.txt', 'r') as f:
    tree = eval(f.read())
f.close()

print("Hi!")

def isNew(link, where_found):
    cleanedLink = ("http://" + link[8:] if link.startswith("https") else link)
    illegal_url_chars = ['#','?']
    char_location = -1
    for c in illegal_url_chars:
        char_location = cleanedLink.find(c)
        if char_location >= 0:
            cleanedLink = cleanedLink[0:char_location]
    if cleanedLink.startswith("http") and cleanedLink[:-3] not in ignore_exts: #link is an http link, not a photo/video
        if cleanedLink in tree:
            if where_found not in tree[cleanedLink]:
                tree[cleanedLink].append(where_found)
        else:
            tree[cleanedLink] = [where_found]
        if cleanedLink not in found_links: #link not previously grabbed
            if restrict_to_domains:
                if any(d in cleanedLink for d in keep_within_domains):
                    return cleanedLink
                else:
                    return None
            else:
                return cleanedLink
        else:
            return None
    else:
        return None

def grab_links(start_url):
    print("Scraping from: " + start_url)
    page = bs(requests.get(start_url).content, features="lxml")
    if save_pages:
        temp_dir = start_url[7:].rsplit("/",1)[0]
        print(temp_dir)
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        filename = (start_url[7:] + ".html" if start_url[:-4] not in [".php","html"] else start_url[7:])
        try:
            with open(filename,"w+") as f:
                f.write(str(page))
                f.close()
        except (IsADirectoryError):
            with open(start_url[7:]+"/index.html","w+") as f:
                f.write(str(page))
                f.close()
    links = page.findAll('a', href=True)
    found_links.remove(start_url)
    for l in links:
        l = l['href'].strip()
        l = ("http://" + l[8:] if l.startswith("https") else l)
        validatedLink = isNew(uparse.urljoin(start_url, l), start_url)
        if validatedLink != None:
            found_links.append(validatedLink)
            #print(validatedLink)

found_links.append(base_url)
grab_links(base_url)
for l in found_links:
    grab_links(l)
    with open('crawler_dict.txt', 'w') as f:
        f.write(str(tree))
        f.close()
