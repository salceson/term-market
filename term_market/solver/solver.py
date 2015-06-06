import json
import copy

import networkx as nx


class Solver(object):
    def __init__(self, path_to_offers_file, path_to_collisions_file):
        self.path_to_offers_file = path_to_offers_file
        self.path_to_collisions_file = path_to_collisions_file
        self.offer_dict, self.collision_dict = self.parse_input_files()
        self.offers = self.construct_offers()
        self.graph = self.create_graph()

    def parse_input_files(self):
        with open(self.path_to_offers_file) as f:
            offers = json.load(f)['offers']
        with open(self.path_to_collisions_file) as f:
            collisions = json.load(f)
        return offers, collisions

    def construct_offers(self):
        offers = {}
        for offer in self.offer_dict:
            offers[offer['id']] = Offer(offer['id'], offer['donor'], offer['offered_term'], offer['wanted_terms'])
        return offers

    def create_graph(self):
        graph = nx.DiGraph()
        for offer_key in self.offers.keys():
            graph.add_node(offer_key)
        for offer_key in self.offers.keys():
            for wanted_term in self.offers[offer_key].wanted_terms:
                wanted_offers = filter(lambda off: off.offered_term == wanted_term, list(self.offers.values()))
                for wanted_offer in wanted_offers:
                    graph.add_edge(offer_key, wanted_offer.id)
        return graph

    def solve(self):
        return step(self.graph, [])


def step(graph, list_of_cycles):
    best = graph.number_of_nodes()
    cycles = list(nx.simple_cycles(graph))
    for cycle in cycles:
        graph_v2 = copy.deepcopy(graph)
        graph_v2.remove_nodes_from(cycle)
        list_of_cycles_v2 = copy.deepcopy(list_of_cycles)
        actual_best, actual_list_of_cycles = step(graph_v2, list_of_cycles_v2)
        if actual_best < best:
            best = actual_best
            list_of_cycles = actual_list_of_cycles
            list_of_cycles.append(cycle)
    return best, cycles


class Offer(object):
    def __init__(self, id, donor, offered_term, wanted_terms):
        self.id = id
        self.donor = donor
        self.offered_term = offered_term
        self.wanted_terms = wanted_terms
