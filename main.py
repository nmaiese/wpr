import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import csv

IGNORED_HREF = ['#', 'javascript:;', 'javascript:void(0)']

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



if __name__ == "__main__":

    base_url = 'https://enigaseluce.com'
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

        print 'Completed depth (' + str(counter) + '/' + str(depth) + ')'
        counter += 1

    print 'Total links found: ' + str(len(graph))


    with open('out.csv', 'w+') as f:
        writer = csv.DictWriter(f, fieldnames=graph[0].keys())
        writer.writeheader()
        [writer.writerow(x) for x in graph]

