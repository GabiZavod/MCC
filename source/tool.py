#!/usr/bin/env python3

import sys
import copy
import pprint
import udapi
from collections import Counter
from document import Document
from metrics import Metrics
from scipy import stats
import numpy as np


class Tool:
    def __init__(self, original, translations, lm):
        # initialize documents - first one is the original, the rest are the translations
        self.documents = [Document(original, original=True)]
        for i in range(len(translations)):
            self.documents.append(Document(translations[i]))
        
        # check if documents have the same structure (same number of articles, same number of sentences in articles)
        self.structure = []
        try:
            self.compare_structure()
        except ValueError as e:
            print(e)
            sys.exit(1)
        
        self.m = Metrics(lm)
        self.encountered = None
    
    def compare_structure(self):
        """Check if Documents have same structure"""
        structures = []
        for d in self.documents:
            structures.append(d.get_structure())
        original_struct = structures[0]
        for n, translation_struct in enumerate(structures[1:]):
            if translation_struct != original_struct:
                print(original_struct, file=sys.stderr)
                print(translation_struct, file=sys.stderr)
                raise ValueError(f"Structure of input {n+1} is different than structure of original")
        # set structure, since its same for all documents 
        self.structure = original_struct

    def extract_text(self, i):
        doc_sents = []
        for d in self.documents:
            doc_sents.append(d.extract(i))
        return doc_sents

    def count_tables(self, unit):
        """Return number of tables that will be produced in total"""
        if unit == "sentence":
            return sum(self.structure)
        if unit == "article":
            return len(self.structure)
        return 1 # for whole

    def compute_metrics(self, metrics):
        """Returns a list containing a list of Counters for each segment for each document"""
        result = [[Counter() for t in d.doc.trees] for d in self.documents]
        if "nominalization" in metrics:
            # load file with czech nominalized lemmas
            noms = {}
            with open("resources/ni-ti.tsv", "r") as nominalized:
                i = 0
                while True:
                    line = nominalized.readline()

                    if not line:
                        break

                    if i == 0: i+=1
                    elif i % 2 != 0:
                        noms[nominalized.readline().split("\t")[1][:-1]] = line.split("\t")[1][:-1]
        if "untranslated" in metrics:
            # create list of trees from the original
            orig_trees = [t for t in self.documents[0].doc.trees]

        for i, d in enumerate(self.documents):
            for j, t in enumerate(d.doc.trees):
                for metric in metrics:
                    # measuring nominalization differently for english vs czech
                    if metric == "nominalization":
                        if i == 0:
                            result[i][j] += self.m.nominalization(t)
                        else:
                            result[i][j] += self.m.nominalization(t,ns=noms)
                    # defaulting untranslated words in the original to 0
                    elif metric == "untranslated":
                        if i == 0:
                            result[i][j] += Counter({"Untranslated": 0})
                        else:
                            result[i][j] += self.m.untranslated(orig_trees[j], t)
                    elif metric == "lm_score":
                        if i == 0:
                            result[i][j] += Counter({"LM score": 0})
                        else:
                            result[i][j].update(self.m.lm_score(t))
                    elif metric == "perplexity":
                        if i == 0:
                            result[i][j] = Counter({"Perplexity": 0})
                        else:
                            result[i][j].update(self.m.perplexity(t))
                    elif metric == "words_per_line":
                        result[i][j] += self.m.length(t,wpl=True)
                    else:
                        # call method to compute metric
                        metric_result = getattr(self.m, metric)(t)
                        # add result of metric to counter corresponding to the tree
                        result[i][j].update(metric_result)
        

        self.encountered = self.m.encountered_metrics
        return result 

    def extract_part(self, res, sentence=None, start_s=None, end_s=None) -> list[Counter()]:
        """
        Returns a list of Counters for all documents the part of res either:
        - extract_part(res, sentence=n): corresponding to the sentence at the n-th sentence
        - extract_part(res, start_s=i, end_s=j): corresponding to the article ranging from the i-th sentence to the j-th sentence
        - extract_part(res): corresponding to the whole
        """
        result = []
        res_cp = None
        if res[0][0]["TTR"] != 0:
            res_cp = copy.deepcopy(res)
        to_traverse = res_cp if res_cp != None else res
        # from all documents extract results for sentence
        if sentence is not None:
            for d in range(len(self.documents)):
                if to_traverse[d][sentence]["TTR"] !=0:
                    to_traverse[d][sentence]["TTR"] = len(res_cp[d][sentence]["TTR"])
                result.append(to_traverse[d][sentence])

        # from all documents extract results for article starting with start_s and ending with end_s into single Counter
        elif start_s is not None and end_s is not None:
            for d in range(len(self.documents)):
                article_counter = Counter()
                for i in range(start_s, end_s):
                    # add Counter corresponting to sentence
                    article_counter.update(res[d][i])
                result.append(article_counter)

        # from all documents extract results for the whole into a single Counter
        else:
            for d in range(len(self.documents)):
                whole_counter = Counter()
                unique_types = set()
                for counter in to_traverse[d]:
                    if counter["TTR"] != 0:
                        unique_types = unique_types.union(counter["TTR"])
                        del counter["TTR"]
                    whole_counter.update(counter)
                
                if len(unique_types) > 0:
                    whole_counter["TTR"] = len(unique_types)
                result.append(whole_counter)

        return result

    def format_result(self, res, encoun, sentence=None, start_s=None, end_s=None, ttest=False):
        """Return result formatted for the unit, or t-test"""
        if encoun is None:
            new_res = [[metric]+[0 for doc in self.documents] for metric in self.encountered]
        else:
            new_res = [[metric]+[0 for doc in self.documents] for metric in encoun]
        # extract counter for the part needed
        part_res = []
        if sentence is not None:
            part_result = self.extract_part(res, sentence=sentence)
        elif start_s is not None and end_s is not None:
            part_result = self.extract_part(res, start_s=start_s, end_s=end_s)
        else:
            part_result = self.extract_part(res)
        
        if ttest:
            return part_result
        
        for m in new_res:
            for d in range(len(self.documents)):
                # On the first (0) position of m is the name of the metric, 
                # the results for this metric for each of the documents are therefore moved one position ti the right
                m[d+1] = part_result[d][m[0]]
        return new_res
    
    def ttest_format(self, res, encoun):
        if encoun is None:
            new_res = [[metric]+[[] for doc in self.documents] for metric in self.encountered]
        else:
            new_res = [[metric]+[[] for doc in self.documents] for metric in encoun]
        for m in new_res:
            for unit in range(len(res)):
                for doc in range(len(res[unit])):
                    m[doc+1].append(res[unit][doc][m[0]])
        
        return new_res
                