import requests
from bs4 import BeautifulSoup
import pandas as pd
import sys
import json
import networkx as nx
import community
from networkx.readwrite import json_graph

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
    base_url = 'http://www.ircouncil.it/'
    base_url = 'http://www.multicentrum.it/'
    wpr = WPR(base_url)
    wpr.navigate_website('/', 2)
    pd.DataFrame(wpr.connections).to_csv(wpr.domain + '.csv', encoding='utf-8')


    wpr.connections = pd.DataFrame.from_csv(wpr.domain + '.csv')

    # read graph from dataframe
    G = nx.from_pandas_dataframe(wpr.connections, 'source', 'target')
    part = community.best_partition(G)

    for ix, deg in G.degree().items():
        G.node[ix]['degree'] = deg
        G.node[ix]['parity'] = (1 - deg % 2)


    for ix, node in part.items():
        G.node[ix]['modularity'] = part[ix]


    data = json_graph.node_link_data(G)
    with open(wpr.domain + '_d3.json', 'w') as f:
        json.dump(data, f, indent=4)


    nodes = data['nodes']
    edges = wpr.connections.to_dict(orient='records')
    graph = {'nodes': nodes, 'edges': edges }


    with open(wpr.domain + '_sigma.json', 'w') as f:
        json.dump(graph, f, indent=4)





# edges = wpr.connections
# edges['id'] = edges.index
# nodes = pd.DataFrame(list(edges['target']) + list(edges['source']), columns=['id'])
# nodes = pd.DataFrame(nodes['id'].unique(), columns=['id'])
# nodes['labels'] = nodes['id']
#
# l_edges = []
# l_nodes = []
#
# for i, x in edges.iterrows():
#     l_edges += [dict(x)]
# for i, x in nodes.iterrows():
#     l_nodes += [dict(x)]
#
# graph = {'nodes': l_nodes, 'edges' : l_edges}
#
# with open(wpr.domain + '.json', 'w') as f:
#     json.dump(graph, f)

