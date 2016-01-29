from subprocess import call
from time import perf_counter
from urllib import request

import pygraphviz as pg
from bs4 import BeautifulSoup

a = pg.AGraph(directed=True, strict=True)


class Node:
    def __init__(self, node_id, text=None, parent=None, children=None):
        self.id = node_id
        self.text = text
        self.parents = ({parent} if parent is not None else set())
        self.children = (children if children is not None else set())

    def add_parent(self, parent):
        self.parents.add(parent)

    def set_children(self, children):
        self.children.update(children)

    def set_text(self, text):
        self.text = text

nodes = {
    '0': Node('0'),
}


def scrape_page(url, limit=0):
    soup = BeautifulSoup(request.urlopen(url).read(), 'html.parser')
    total = len(soup.find_all('div', class_="text"))
    loop_times = []
    current = 0

    for div in soup.find_all('div', class_="text", limit=limit):
        t1 = perf_counter()

        curr_page = div['id']
        links = []
        for link in soup.select('#' + curr_page + " p u"):
            page_id = link['onclick'][4:-1]
            text = link.text

            if page_id not in nodes:
                nodes[page_id] = (Node(page_id, text=text, parent=curr_page))
            else:
                nodes[page_id].add_parent(curr_page)
                nodes[page_id].set_text(text)

            links.append(page_id)

        if curr_page in nodes:
            nodes[curr_page].set_children(links)
        else:
            nodes[curr_page] = Node(curr_page, children=links)

        current += 1

        loop_times.append(perf_counter() - t1)
        print("\rComplete: " + str(round((current / (limit if limit != 0 else total)) * 100)) + "%\t\t" +
              "Time remaining: " + str(round(((limit if limit != 0 else total) - current) * (sum(loop_times) / len(loop_times)))) + " seconds.", end="")

    print("\rComplete: 100%\n")

scrape_page("file:///Users/mac/Documents/Nspire%20Files/ndless-v3.9-beta/samples/asstr/pub/Authors/~Arthur_Saxon/Geography.html", limit=0)

for node in nodes:
    if len(nodes[node].children) == 0:
        a.add_node(nodes[node].id, label=nodes[node].text, color="red")
    else:
        a.add_node(nodes[node].id, label=nodes[node].text)

for node in nodes:
    for child in nodes[node].children:
        a.add_edge(nodes[node].id, child)

a.write('tree_Geo_text.dot')
a.layout(prog='dot')
call(['dot', 'tree_Geo_text.dot', '-Tpng', '-o', 'tree_Geo_text.png'])
