import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import csv
import pandas as pd

IGNORED_HREF = ['#', 'javascript:;', 'javascript:void(0)']

def detect_domain(url):
    if 'https' in url:
        domain = url.replace('https://','')
    elif 'http' in url:
        domain = url.replace('http://','')
    elif 'www' in url:
        domain = url.replace('www.','')
    if 'www' in url:
        domain = domain.replace('www.','')
    if domain.find('/')!= -1:
        return domain[:domain.find('/')]
    else: return domain


def get_soup(link):
    """
    Return the BeautifulSoup object for input link
    """
    request_object = requests.get(link)
    soup = BeautifulSoup(request_object.content, 'html.parser')
    return soup

def get_internal_link(url, base_url):
    if url.has_attr('href'):
        url = url['href']
        if url not in IGNORED_HREF:
            if base_url in url:
                url = url.replace(base_url, '')
                return url
            elif 'http' not in url:
                if url:
                    if url[0] == '/':
                        return url



class WPR(object):
    def __init__(self, url):
        self.nodes = []
        self.connections = []
        self.domain = detect_domain(url)
        self.visited_url = []
        self.graph = []
        self.visited_url = []

    def get_links(self, url, protocol='https'):
        if url not in self.visited_url:
            self.base_url = protocol+'://' + self.domain + url
            try:
                soup = get_soup(self.base_url)
                target_url = soup.findAll('a')
                seed_targets = [get_internal_link(x, base_url) for x in target_url if get_internal_link(x, base_url)]
                self.nodes += [url]
                self.visited_url += [url]

                for target in seed_targets:
                    if target not in self.nodes:
                        self.nodes.append(target)
                print str(len(self.visited_url)) + '/' + str(len(self.nodes)) + ' Visited url'
                return [{'source': url, 'target': x} for x in seed_targets]
            except:
                print base_url + '\n Not Found'


    def navigate_website(self, url, depth=2):
        result = self.get_links(url)
        if result: self.connections += result
        counter = 1
        while counter <= depth:
            print 'depth (' + str(counter) + '/' + str(depth) + ')'
            next_urls = [x for x in self.connections if x['target'] not in self.visited_url]
            for connection in next_urls:
                base_url = connection['target']
                result = self.get_links(base_url)
                if result: self.connections += result
            print 'Completed depth (' + str(counter) + '/' + str(depth) + ')'
            counter += 1
        next_urls = [x for x in self.connections if x['target'] not in self.visited_url]
        for connection in next_urls:
            base_url = connection['target']
            result = self.get_links(base_url)
            if result: self.connections += result



if __name__ == "__main__":
    base_url = 'https://enigaseluce.com'
    base_url = 'https://www.groupm.com'
    wpr = WPR(base_url)
    wpr.navigate_website('/')

    with open(wpr.domain + '.csv', 'w+') as f:
        writer = csv.DictWriter(f, fieldnames=wpr.connections[0].keys())
        writer.writeheader()
        [writer.writerow(x) for x in wpr.connections]
    print 'saved '+ wpr.domain + 'out.csv'









"""




    soup = get_soup(base_url)
    target_url = soup.findAll('a')
    seed_targets = [get_internal_link(x, base_url) for x in target_url if get_internal_link(x, base_url)]

    graph = [{'source': '/', 'target': x} for x in seed_targets]
    visited_url = ['/']

    counter = 1
    depth = 3 # suppose

    while counter <= depth:
        print 'depth (' + str(counter) + '/' + str(depth) + ')'
        partial_graph = []
        for new_url in tqdm(graph):
            new_base = new_url['target']
            if new_base not in visited_url:
                visited_url.append(new_base)
                try:
                    soup = get_soup(base_url+new_base)
                    target_url = soup.findAll('a')
                    seed_targets = [get_internal_link(x, base_url) for x in target_url if get_internal_link(x, base_url)]
                    partial_graph += [{'source': new_base , 'target': x} for x in seed_targets]
                except:
                    print base_url+new_base + '\n Not Found'
        graph += partial_graph

    with open('out.csv', 'w+') as f:
        writer = csv.DictWriter(f, fieldnames=graph[0].keys())
        writer.writeheader()
        [writer.writerow(x) for x in graph]
        """