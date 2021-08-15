#!/usr/bin/python3
from typing import Union, List

import bs4
from bs4 import BeautifulSoup as bs
import requests
import argparse
import os
import re

from database.pages_database import PagesDatabase, Page

IGNORED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'peg', 'gif', 'mp4', 'mkv', 'avi', 'mov', 'swf', 'pdf', 'm3u', 'm3u8', 'msi', 'exe', 'zip']
SAVE_WEBPAGE_FOLDER = 'saved_webpages'


class LinkAndParent:
    def __init__(self,
                 link: str,
                 parent_page: Page = None):
        self.link = link
        self.parent = parent_page


class LinkAndParentList:
    def __init__(self):
        self.list = []

    @property
    def _links(self):
        return [item.link for item in self.list]

    def add_item(self,
                 link_and_parent: LinkAndParent):
        if not self.link_already_being_tracked(url=link_and_parent.link):
            self.list.append(link_and_parent)

    def link_already_being_tracked(self,
                                   url: str) -> bool:
        return url in self._links

    def load_next_item(self) -> LinkAndParent:
        if not self.list:
            raise Exception("We've run out of links!")  # this will basically never happen
        next_pair = self.list[0]
        self.list.pop(0)
        return next_pair


restricted_domains = []

currently_crawling_links = []

database = PagesDatabase(sqlite_file="links.db")
tracker = LinkAndParentList()


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
    if link.endswith("/"):
        link = link[:-1]
    return link


def is_approved_domain(url: str):
    if not restricted_domains:
        return True
    base_domain = re.search('(http[s]?:\/\/[^\/]*)', url).group(1)
    return base_domain in restricted_domains


def find_page(url, pages_database) -> Page:
    return pages_database.get_page_entry_by_url(url=url)


def page_available_to_scrape(url: str):
    try:
        return bool(requests.head(url))
    except Exception as e:
        print(e)
        return False


def check_if_same_link(url: str, parent_page: Page):
    if not parent_page:
        return False
    if url.endswith("/"):
        url = url[:-1]
    parent_url = parent_page.url
    if parent_url.endswith("/"):
        parent_url = url[:-1]
    return url == parent_url


def grab_links_from_page(url: str):
    if not page_available_to_scrape(url):
        return []
    try:
        html = bs(requests.get(url).content, features="html.parser")
        a_tags = html.findAll('a', href=True)
        return [a.get('href') for a in a_tags]
    except Exception as e:  # request timed out
        print(e)
        return []


def crawl_page(url: str, parent_page: Page = None):
    global currently_crawling_links
    if url.endswith("/"):
        url = url[:-1]
    page = database.add_page_and_relationship(url=url, parent_page=parent_page)
    if is_approved_domain(url) and not check_if_same_link(url, parent_page):
        pair = LinkAndParent(link=url, parent_page=parent_page)
        tracker.add_item(link_and_parent=pair)
        link_fragments = grab_links_from_page(url=url)
        # cycle_links(parent_page=page, link_fragments=link_fragments)
        store_links(parent_page=page, link_fragments=link_fragments)


def store_links(parent_page: Page, link_fragments: List[str]):
    for link in link_fragments:
        if link in ['/', '/.']:
            pass
        elif link.startswith("#"):
            pass
        elif link.startswith('http'):
            pass
        elif link.startswith('//'):
            link = f'https:{link}'
        elif link.startswith('/'):
            link = f'{parent_page.url}{link}'
        else:
            link = f'{parent_page.url}/{link}'
        link = clean_link(link)
        global currently_crawling_links
        if link and is_valid_link(link) and not tracker.link_already_being_tracked(url=link):
            pair = LinkAndParent(link=link, parent_page=parent_page)
            tracker.add_item(link_and_parent=pair)


def cycle_links(parent_page: Page, link_fragments: List[str]):
    for link in link_fragments:
        if link in ['/', '/.']:
            pass
        elif link.startswith("#"):
            pass
        elif link.startswith('http'):
            pass
        elif link.startswith('//'):
            link = f'https:{link}'
        elif link.startswith('/'):
            link = f'{parent_page.url}{link}'
        else:
            link = f'{parent_page.url}/{link}'
        link = clean_link(link)
        if link and is_valid_link(link) and link not in currently_crawling_links:
            crawl_page(url=link, parent_page=parent_page)


def crawl_pages(url: str, parent_page: Page = None):
    crawl_page(url=url, parent_page=parent_page)
    while True:
        next_item = tracker.load_next_item()
        if not next_item:
            exit(0)
        crawl_page(url=next_item.link, parent_page=next_item.parent)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('starting_url', help="URL of where to start crawling")
    parser.add_argument('-r', "--restrict", help="Don't leave the initial domain", action='store_true')
    args = parser.parse_args()

    global restricted_domains
    if args.restrict:
        restricted_domains.append(args.starting_url)
    if args.starting_url[:7] not in ['https:/', 'http://']:
        args.starting_url = 'https://{}'.format(args.starting_url)
        if args.restrict:
            restricted_domains.append(args.starting_url)

    crawl_pages(url=args.starting_url, parent_page=None)


main()
