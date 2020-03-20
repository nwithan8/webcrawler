#!/usr/bin/python3

from bs4 import BeautifulSoup as bs
import requests
import argparse
import os
import re

IGNORED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'peg', 'gif', 'mp4', 'mkv', 'avi', 'mov', 'swf', 'pdf', 'm3u', 'm3u8']
SAVE_WEBPAGE_FOLDER = 'saved_webpages'
VISITED_PAGES = []
ID_NUMBER = 0


class PageDict:
    def __init__(self):
        self.pages = {}


class Page:
    def __init__(self, url, id_number):
        self.url = url
        self.id = id_number
        self.fromPages = []
        self.toPages = []


def is_valid_link(link: str):
    try:
        if link.startswith('#') or link.startswith('?') or link.startswith('mailto:') or link.startswith('tel:'):
            return False
        end = re.search('.*\.(.*)', link).group(1)
        if not end or end in IGNORED_EXTENSIONS:
            return False
        return True
    except Exception as e:
        return False


def clean_link(link):
    illegal_url_chars = ["#", "\?"]
    for c in illegal_url_chars:
        regex = '(.*){0}'.format(c)
        try:
            link = re.search(regex, link).group(1)
        except Exception as e:
            pass
    return link


def find_page(url, pages):
    for page in pages:
        if page.url == url:
            return page
    return None


def grab_links(start_url: str, pages: PageDict, save_pages: bool = False, restrict_domain: bool = False,
               restrict_to_domains: list = [], parentPage: Page = None):
    global VISITED_PAGES
    global ID_NUMBER
    if start_url not in VISITED_PAGES:
        print("Scraping from {}".format(start_url))
        new_entry = Page(url=start_url, id_number=ID_NUMBER)
        if parentPage:
            new_entry.fromPages.append(parentPage)
            parentPage.toPages.append(new_entry)
        pages.pages[ID_NUMBER] = new_entry
        try:
            html = bs(requests.get(start_url).content, features="lxml")
            file_path = re.search('http[s]?:\/\/(.*)', start_url).group(1)
            dir_path = file_path.rsplit('/', 1)[0]
            if save_pages and start_url.startswith('http'):
                if not os.path.exists('{}/{}'.format(SAVE_WEBPAGE_FOLDER, dir_path)):
                    os.makedirs('{}/{}'.format(SAVE_WEBPAGE_FOLDER, dir_path))
                if file_path.endswith('/'):
                    file_path = file_path[:-1]
                if not file_path.endswith('.html') and not file_path.endswith('.htm') or not file_path.endswith('.php'):
                    file_path += '.html'
                try:
                    with open('{folder}/{path}'.format(folder=SAVE_WEBPAGE_FOLDER, path=file_path), "w+") as f:
                        f.write(str(html))
                        f.close()
                    print("Saved {}".format('{folder}/{path}'.format(folder=SAVE_WEBPAGE_FOLDER, path=file_path)))
                except IsADirectoryError:
                    with open('{folder}/{path}/index.html'.format(folder=SAVE_WEBPAGE_FOLDER, path=file_path),
                              "w+") as f:
                        f.write(str(html))
                        f.close()
                    print("Saved {}".format(
                        '{folder}/{path}/index.html'.format(folder=SAVE_WEBPAGE_FOLDER, path=file_path)))
                except Exception as e:
                    print(e)
                    pass
            links = html.findAll('a', href=True)
            VISITED_PAGES.append(start_url)
            for link in links:
                link = link.get('href')
                if link.startswith('//'):
                    link = 'https:{}'.format(link)
                elif link.startswith('/'):
                    dir_path = dir_path.rsplit('/', 1)[0]
                    link = 'https://{path}{link}'.format(path=dir_path, link=link)
                link = clean_link(link)
                if is_valid_link(link):
                    base_domain = re.search('(http[s]?:\/\/[^\/]*)', start_url).group(1)
                    if restrict_domain and base_domain not in restrict_to_domains:
                        pass
                    else:
                        ID_NUMBER += 1
                        grab_links(start_url=link, pages=pages, save_pages=save_pages, restrict_domain=restrict_domain,
                                   restrict_to_domains=restrict_to_domains)
        except Exception as e:  # request timed out
            print(e)
            pass
    else:
        existing_page = find_page(start_url, pages)
        if existing_page:
            existing_page.fromPages.append(parentPage)
        print("{} already crawled".format(start_url))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('starting_url', help="URL of where to start crawling")
    parser.add_argument('-r', "--restrict", help="Don't leave the initial domain", action='store_true')
    parser.add_argument('-s', '--save', help='Save pages', action='store_true')
    args = parser.parse_args()
    restrict_to_domains = []
    if args.restrict:
        restrict_to_domains.append(args.starting_url)
    if args.starting_url[:7] not in ['https:/', 'http://']:
        args.starting_url = 'https://{}'.format(args.starting_url)
        if args.restrict:
            restrict_to_domains.append(args.starting_url)
    if args.save and not os.path.exists(SAVE_WEBPAGE_FOLDER):
        os.mkdir(SAVE_WEBPAGE_FOLDER)
    """
    with open('crawler_dict.txt', 'r') as f:
        tree = eval(f.read())
    f.close()
    """
    pages_dict = PageDict()
    grab_links(start_url=args.starting_url, pages=pages_dict, save_pages=args.save, restrict_domain=args.restrict,
               restrict_to_domains=restrict_to_domains)


main()
