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
            offers = json.load(f)
        with open(self.path_to_collisions_file) as f:
            collisions = json.load(f)
        return offers, collisions

    def construct_offers(self):
        offers = []
        for offer in self.offer_dict:
            offers.append(
                Offer(offer['id'], offer['donor_id'], offer['offered_term_id'], offer['wanted_terms_id_list']))
        return offers

    def create_graph(self):
        graph = nx.DiGraph()
        for offer in self.offers:
            graph.add_node(offer)
        for offer in self.offers:
            for wanted_term in offer.wanted_terms_id_list:
                wanted_offers = filter(lambda off: off.offered_term_id == wanted_term, list(self.offers))
                for wanted_offer in wanted_offers:
                    graph.add_edge(self.offers[offer.id], self.offers[wanted_offer.id])
        return graph

    def solve(self):
        return step(self.graph)


def step(graph):
    best = graph.number_of_nodes()
    list_of_cycles = []
    cycles = nx.simple_cycles(graph)
    for cycle in cycles:
        graph_v2 = copy.deepcopy(graph)
        graph_v2.remove_nodes_from(cycle)
        actual_best, actual_list_of_cycles = step(graph_v2)
        if actual_best < best:
            best = actual_best
            list_of_cycles = actual_list_of_cycles
            list_of_cycles.append(cycle)
    return best, list_of_cycles


class Offer(object):
    def __init__(self, id, donor_id, offered_term_id, wanted_terms_id_list):
        self.id = id
        self.donor_id = donor_id
        self.offered_term_id = offered_term_id
        self.wanted_terms_id_list = wanted_terms_id_list
