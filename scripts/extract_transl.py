#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import sys

def main(sgm_file):
    with open("article_names.txt", "r") as f:
        used_articles = [a[:-1] for a in f.readlines()]
        used_article = {}
        for a in used_articles:
            used_article[a] = ""
    tree = ET.parse(sgm_file)
    root = tree.getroot()

    i = 0
    
    for doc in root:
        doc_name = doc.get("docid")
        if doc_name in used_articles:
            if i != 0:
                used_article[doc_name] += ("\n")
            i+=1
            used_article[doc_name] += ("# " + doc_name + "\n")
            for p in doc:
                for seg in p:
                    used_article[doc_name] += (seg.text+ "\n")
    
    out_name = "./data/" + sgm_file.split('.')[2] + ".txt"
    out_f = open(out_name, "w")

    for val in used_article.values():
        out_f.write(val)



if __name__ == '__main__':
    main(sys.argv[1])