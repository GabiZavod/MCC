#!/usr/bin/env python3

from difflib import SequenceMatcher
from itertools import product
from metrics import Metrics

class Aligner:
    def __init__(self, lm_file):
        self.m = Metrics(lm_file)
        self.not_aligned = [set(), set()]

    def find_pair(self, node, idx, aligned):
        for pair in aligned:
            if node == pair[idx]:
                # print(node.form)
                # print(pair[(idx+1)%2].form)
                return pair[(idx+1)%2].form

    def find_metric_words(self, tree1, tree2, idx, aligned, metric):
        """Mark words corresponding to metric, and ones that are responsible for a difference in metric"""
        words_for_metric = [self.m.list_metric(tree1, metric), self.m.list_metric(tree2, metric)]
        for node in tree1.descendants:
            if node.form in words_for_metric[idx]:
                # zvýrazní slovo splnajúce metriku, ktoré neni alignované
                if node in self.not_aligned[idx] or (self.find_pair(node, idx, aligned) not in words_for_metric[(idx+1)%2]):
                    node.form = r"\D{" + node.form + r"}"
                else:
                    node.form = r"\M{" + node.form + r"}"

        tree1.get_sentence()
        print(" ".join([node.form for node in tree1.descendants]))

    def similarity(self, node1, node2):
        """Return similarity of two nodes, considering their form and their order"""
        return SequenceMatcher(None, node1.form, node2.form).ratio() * SequenceMatcher(None, node1.upos, node2.upos).ratio()    # / divisor

    def align(self, tree1, tree2):
        """Align the words in tree1 with the words in tree2"""
        #NOTE: prip. optimalizovat product
        all_pairs = product(tree1.descendants, tree2.descendants)

        all_pairs = sorted(all_pairs, key=lambda x: self.similarity(*x), reverse=True)

        aligned = []
        used1 = set()
        used2 = set()

        # can I compare nodes on equality - yep, this way Im not just considering word forms, nice
        for w1, w2 in all_pairs:
            if w1 not in used1 and w2 not in used2:
                aligned.append((w1,w2))
                used1.add(w1)
                used2.add(w2)

        self.not_aligned = [set(tree1.descendants) - used1, set(tree2.descendants) - used2]

        print(f"Not aligned in 1st: {self.not_aligned[0]}")
        print(f"Not aligned in 2nd: {self.not_aligned[1]}")

        return aligned

