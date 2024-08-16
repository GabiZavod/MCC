#!/usr/bin/env python3

import udapi
import kenlm
from collections import Counter, deque

class Metrics:   
    def __init__(self, lm_filename):
        self.encountered_metrics = set()
        if lm_filename != False:
            self.lm = kenlm.LanguageModel(lm_filename)

    def length(self, tree, wpl=False, id=None):
        """Return length of tree or words per line"""
        if wpl:
            self.encountered_metrics.add("Words/Line")
            return Counter({"Words/Line": len([node for node in tree.descendants])})
        else:
            self.encountered_metrics.add("Length")
            return Counter({"Length": len([node for node in tree.descendants])})
    
    def lines(self, tree):
        """Return Counter with 1 as line count"""
        return Counter({"Lines": 1})
    
    def deprel(self, tree, add=True):
        """Count number of occurances of dependency relations"""
        deprels = Counter()
        for node in tree.descendants:
            deprels[node.deprel] += 1
            if add: self.encountered_metrics.add(node.deprel)
        return deprels

    def pos(self,tree, add=True):
        """Count number of occurances of POS tags"""
        poses = Counter()
        for node in tree.descendants:
            poses[node.upos] += 1
            if add: self.encountered_metrics.add(node.upos)
        return poses
    
    def feat_keys(self, tree):
        """Count number of occurances of features"""
        features = Counter()
        for node in tree.descendants:
            for feat, _ in node.feats.items():
                features[feat] += 1
                self.encountered_metrics.add(feat)
        return features
    
    def feats(self, tree):
        """Count number of occurances with features with concrete value"""
        feat_vals = Counter()
        for node in tree.descendants:
            for feat, val in node.feats.items():
                feat_vals[feat+"."+val] += 1
                self.encountered_metrics.add(feat+"."+val)
        return feat_vals

    def lex_density(self, tree):
        lexical_pos = "ADV ADJ NOUN VERB PROPN".split()
        poses = self.pos(tree, add=False)
        lexical_words = sum([poses[pos] for pos in lexical_pos])
        self.encountered_metrics.add("Lexical density")
        return Counter({"Lexical density": lexical_words})

    def syntactic_comp(self, tree):
        clause_head_markers = "root csubj ccomp xcomp advcl acl".split()
        deprels = self.deprel(tree, add=False)
        clause_head_counts = []
        for name, count in deprels.items():
            if name.split(":")[0] in clause_head_markers:
                clause_head_counts.append(count)
        self.encountered_metrics.add("Syntactic complexity")
        return Counter({"Syntactic complexity" : sum(clause_head_counts)})
    
    def lm_score(self, tree):
        tokenized_sent = " ".join([node.form.lower() for node in tree.descendants])
        score = pow(10, self.lm.score(tokenized_sent))
        self.encountered_metrics.add("LM score")
        return Counter({"LM score": score})
    
    def perplexity(self, tree):
        tokenized_sent = " ".join([node.form.lower() for node in tree.descendants])
        score = self.lm.perplexity(tokenized_sent)
        self.encountered_metrics.add("Perplexity")
        return Counter({"Perplexity": score})
    
    def untranslated(self, orig_tree, tree):
        orig_tokens = self.token_freq(orig_tree, stop_w=True)
        transl_tokens = self.token_freq(tree, stop_w=True)

        # untranslated tokenens are contained in the original as well as in the translated sentence (intersection)
        untranslated = orig_tokens & transl_tokens

        # NOTE: uncomment following code to see untranslated words and the sentences they appear in
        # if untranslated.total() > 0: 
        #     print(untranslated.most_common())
        #     print(orig_tree.text)
        #     print(tree.text)

        self.encountered_metrics.add("Untranslated")
        return Counter({"Untranslated": untranslated.total()})
    
    def sent_ttr(self, tree, lemma=True):
        """Compute sentence TTR"""
        types = self.token_freq(tree, lemmatized=lemma).keys()
        self.encountered_metrics.add("Sentence TTR")
        return Counter({"Sentence TTR": len(types)/len([node for node in tree.descendants])})
    
    def ttr(self, tree, lemma=True):
        """Find unique types in a sentence (lemmatized or not)"""            # returning set of types 
        types = self.token_freq(tree, lemmatized=lemma).keys()
        self.encountered_metrics.add("TTR")
        return Counter({"TTR": set(types)})
    
    def tree_depth(self, tree):
        """Return the depth of tree"""
        self.encountered_metrics.add("Tree depth")
        return Counter({"Tree depth" : self.depth(tree)})
    
    def tree_width(self, tree):
        """Return level with most nodes"""
        self.encountered_metrics.add("Tree width")
        return Counter({"Tree width" : self.width(tree)})
    
    def passives(self, tree):
        """Count occurrances of passive voice"""                #TODO: check if it gives same result as Voice.Pass in feats_values
        passive = 0
        for node in tree.descendants:
            if node.feats["Voice"] == "Pass":
                passive+=1
        self.encountered_metrics.add("Passives")
        return Counter({"Passives": passive})

    def nominalization(self, tree, ns=None):
        """Return count of nominalizations"""
        en_nomi_endings = ["ing", "ion", "ity", "ment", "ness"]
        nomis = 0
        for node in tree.descendants:
            # czech nominalization
            if ns:
                if node.upos == "NOUN" and node.lemma in ns.keys():
                    nomis +=1
            # english nominalization:
            else:
                if node.upos == "NOUN" and (node.lemma[-3:] in en_nomi_endings or node.lemma[-4:] in en_nomi_endings):
                    nomis += 1
        self.encountered_metrics.add("Nominalization")
        return Counter({"Nominalization": nomis})

    def list_metric(self,tree, metric):
        """Return a list of nodes corresponding to metric"""
        words_metric = []
        #upos
        if metric in ["ADJ", "ADV", "INTJ", "NOUN", "PROPN", "VERB", "ADP", "AUX", "CCONJ", "DET", "NUM", "PART", "PRON", "SCONJ", "PUNCT", "SYM", "X"]:
            for node in tree.descendants:
                if node.upos == metric:
                    words_metric.append(node.form)
        elif metric == "length": 
            words_metric = [node.form for node in tree.descendants]
        return words_metric

    ### methods useed by other methods (pomocné metódy)
    def token_freq(self, tree, stop_w=False, lemmatized=False):
        """Calculate frequency of tokens in a tree"""
        freqs = Counter()
        # stopwords that can be found in the same form in the czech language, but have different meaning -> found as errors
        stopwords = ["a", "an", "and", "the", "on", "to", "my", "s", "do", "by", "i", "ten", "j", "k"]
        for node in tree.descendants:
            if stop_w:
                if node.upos in "PROPN PUNCT SYM NUM".split():
                    continue
                if node.form.lower() in stopwords or node.lemma.lower() in stopwords:
                    continue
            
            #TODO: is it okay if I lowercase the lemma/form?
            if lemmatized:
                freqs[node.lemma.lower()] += 1
            else:
                freqs[node.form.lower()] += 1           
        
        return freqs    

    def depth(self, node):
        """BFS - returns tree depth"""
        if not node:
            return 0
        
        if not node.children:
            return 1
        else:
            return 1 + max([self.depth(child) for child in node.children])
    
    def width(self, root):
        """DFS - returns tree width"""
        if not root:
            return 0
        
        max_width = 0
        q = deque([root])

        while q:
            level_width = len(q)
            max_width = max(max_width, level_width)

            for _ in range(level_width):
                node = q.popleft()
                for child in node.children:
                    q.append(child)
        
        return max_width
