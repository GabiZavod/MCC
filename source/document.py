#!/usr/bin/env python3

import os
import sys
import udapi
import collections
import numpy as np

#NOTE: this class may not even be needed
class Document:
    def __init__(self, name, original=False):
        self.name = name
        self.doc = self.load(name, original)
        self.original = original
    
    def tag(self, doc, original):
        """Tokenize, tag and parse doc"""
        if original:
            udpipe = udapi.create_block("udpipe.En", parse=True)       #TODO: online=1 + parse=True
        else:
            udpipe = udapi.create_block("udpipe.Cs", parse=True)
        udpipe.process_document(doc)

    def load(self, name, original):
        """Load udapi.Document from file name"""
        try:
            doc = udapi.Document(name + ".conllu")
        except OSError:
            try:
                doc = udapi.Document(name + ".txt", newdoc_if_empty_line=True)
                doc_id = None
                for tree in list(doc.trees):
                    if tree.text[0] == "#":
                        doc_id = tree.text[2:]
                        tree.bundle.remove()
                    else:
                        if doc_id:
                            tree.newdoc = doc_id
                            doc_id = None
                self.tag(doc, original)
                doc.store_conllu(name + ".conllu")
            except OSError:
                print(f"File {name}.txt was not found.", file=sys.stderr)
                sys.exit(1)

        return doc

    def extract(self,indices):
        """Print and return sentences with index in indices"""
        sentences = []
        print(self.name)
        for i,tree in enumerate(self.doc.trees):
            if i in indices:
                sentences.append(tree)
                print(tree.text)
                print()
        return sentences

    def get_structure(self):
        """Returns a list with segment counts of each article"""
        structure = []
        article_sent_count = 0
        for tree in self.doc.trees:
            if tree.newdoc:
                structure.append(article_sent_count)
                article_sent_count = 0
            article_sent_count += 1
        structure.append(article_sent_count)
        return structure[1:]
