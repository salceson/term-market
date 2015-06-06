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
        return step(self.offers, self.collision_dict, self.graph, [])


def step(offers, collisions, graph, list_of_cycles):
    best = graph.number_of_nodes()
    cycles = list(nx.simple_cycles(graph))
    for cycle in cycles:
        graph_v2 = copy.deepcopy(graph)
        graph_v2.remove_nodes_from(cycle)
        list_of_cycles_v2 = copy.deepcopy(list_of_cycles)
        actual_best, actual_list_of_cycles = step(offers, collisions, graph_v2, list_of_cycles_v2)
        if actual_best < best:
            if actual_list_of_cycles and is_collisional(offers, collisions, actual_list_of_cycles):
                break
            best = actual_best
            list_of_cycles = actual_list_of_cycles
            list_of_cycles.append(cycle)
    return best, cycles


def is_collisional(offers, collisions, actual_list_of_cycles):
    last_cycle = actual_list_of_cycles[-1]
    for offer_id in last_cycle:
        offer = offers[offer_id]
        donor = offer.donor
        i = iter(last_cycle)
        next_offer_id = next(i, default=None)
        while next_offer_id is not None:
            wanted_term = offers[next_offer_id].offered_term
            for c in actual_list_of_cycles:
                for o_id in c:
                    o = offers[o_id]
                    if donor == o.donnor:
                        j = iter(c)
                        next_o_id = next(j, default=None)
                        while next_o_id is not None:
                            if wanted_term in collisions[str(offers[next_o_id].offered_term)]:
                                return True
                            if next_o_id == c[0]:
                                break
                            next_o_id = next(j, default=c[0])
            if next_offer_id == last_cycle[0]:
                break
            next_offer_id = next(i, default=offer_id)
    return False


class Offer(object):
    def __init__(self, id, donor, offered_term, wanted_terms):
        self.id = id
        self.donor = donor
        self.offered_term = offered_term
        self.wanted_terms = wanted_terms
