import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import csv
import pandas as pd
import sys

IGNORED_HREF = ['#', 'javascript:;', 'javascript:void(0)']

def detect_domain(url):
    protocol = None
    if 'https' in url:
        domain = url.replace('https://','')
        protocol = 'https'
    elif 'http' in url:
        domain = url.replace('http://','')
        protocol = 'http'
    elif 'www' in url:
        domain = url.replace('www.','')
    if 'www' in url:
        domain = domain.replace('www.','')
    if domain.find('/')!= -1:
        return domain[:domain.find('/')], protocol
    else: return domain, protocol


def get_soup(link):
    """
    Return the BeautifulSoup object for input link
    """
    request_object = requests.get(link)
    soup = BeautifulSoup(request_object.content, 'html.parser')
    return soup


def get_internal_link(url, domain):
    if url.has_attr('href'):
        url = url['href']
        if url not in IGNORED_HREF:
            if domain in url:
                url = url[url.find(domain):].replace(domain, '')
                return url
            elif 'http' not in url:
                if url:
                    if url[0] == '/':
                        return url



class WPR(object):
    def __init__(self, url):
        self.nodes = []
        self.connections = pd.DataFrame(columns=['source','target'])
        self.domain, self.protocol = detect_domain(url)
        self.visited_url = []
        self.graph = []
        self.visited_url = []

    def get_internal_link(self, url):
        if url.has_attr('href'):
            url = url['href']
            if url not in IGNORED_HREF:
                if self.domain in url:
                    url = url[url.find(self.domain):].replace(self.domain, '')
                    return url
                elif 'http' not in url:
                    if url:
                        if url[0] == '/':
                            return url

    def get_links(self, url, protocol='https'):
        if self.protocol: protocol = self.protocol
        self.base_url = protocol+'://' + self.domain + url
        try:
            soup = get_soup(self.base_url)
            target_url = soup.findAll('a')
            seed_targets = [wpr.get_internal_link(x) for x in target_url if wpr.get_internal_link(x)]
            return pd.DataFrame([{'source': url, 'target': x} for x in seed_targets])

        except:
            print base_url + '\n Not Found'
            return pd.DataFrame(columns=['source', 'target'])


    def navigate_website(self, url, depth=2, protocol='https'):
        result = self.get_links(url, protocol)
        self.visited_url += [url]
        self.connections = self.connections.append(result, ignore_index=True)
        counter = 1
        while counter <= depth:
            next_urls = list(self.connections[~self.connections['target'].isin(self.visited_url)]['target'].unique())
            #next_urls = list(set([x['target'] for x in self.connections if x['target'] not in self.visited_url]))
            self.nodes = self.connections['target'].unique()
            for url in next_urls:
                result = self.get_links(url, protocol)
                self.visited_url += [url]
                self.connections = self.connections.append(result, ignore_index=True)
                sys.stdout.write(str(len(self.visited_url)) + '/' + str(len(self.nodes)) + ' url '
                                            '@ depth (' + str(counter) + '/' + str(depth) + ')\r')
                sys.stdout.flush()
            counter += 1


if __name__ == "__main__":
    base_url = 'https://enigaseluce.com'
    #base_url = 'https://www.groupm.com'
    #base_url = 'http://www.ircouncil.it/'
    wpr = WPR(base_url)
    wpr.navigate_website('/', 4)

    pd.DataFrame(wpr.connections).to_csv(wpr.domain + '.csv', encoding='utf-8')





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