#!/usr/bin/env python3
import argparse
import sys

class Arg:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.args = {}
        self.possible_actions = ["deprel", "feats", "nominalization", "length", "lex_density", "lm_score", "passives", "perplexity", "pos", "sent_ttr", "syntactic_comp", "tree_depth", "tree_width", "ttr", "untranslated", "words_per_line"]

        # obligatory arguments:
        
        self.parser.add_argument("original", help= "file containing the original text")

        # optional arguments:
        self.parser.add_argument("-m", "--metric", help = "possible actions: deprel | feats | nominalization | length | lex_density | lm_score | passives | perplexity | pos | sent_ttr | syntactic_comp | tree_depth | tree_width | ttr | untranslated | words_per_line", default = "0", nargs='*')           # if metric isnt specified, all of them are calculated
        self.parser.add_argument("-i", "--input", help="Files containing translations (default is sys.stdin)", nargs='*')
        self.parser.add_argument('-o', '--output', help="Output file (default is sys.stdout)", default = sys.stdout)
        self.parser.add_argument("-c", "--choose", help="Pick a single pos or feat, must choose -m too", default=None, nargs='*')

        self.parser.add_argument("--model", help="path to model for lm score calculation", default=False, nargs="?")
        self.parser.add_argument("--compare", help="Add a difference column, possibilities: difference_W | difference_S | ttest_abs | ttest_perc", default=False)
        self.parser.add_argument("--add_comparison", help="Add another difference column, possibilities: difference_W | difference_S |  ttest_abs | ttest_perc", default=False)
        self.parser.add_argument("--csv", help="Output in csv format", default=False, const=True, nargs="?")
        self.parser.add_argument("--tsv", help="Output in tsv format", default=False, const=True, nargs="?")
        self.parser.add_argument("--latex", help="Output in latex format", default=False, const=True, nargs="?")
        self.parser.add_argument("-u", "--unit", help="the basic units: sentence | article | whole", default="whole", nargs="?")
        self.parser.add_argument("--extract", help="index of sentence/article", default=False, nargs="*")
        self.parser.add_argument("--highlight", help="Metric to be highlighted when extracting sentences", default="length", nargs="?")
        self.parser.add_argument("--test", help="Look for input in data/test/ directory", default=False, const=True, nargs="?")

    def parse(self):
        self.args = self.parser.parse_args()
        if self.args.input == None:
            print("Error: Input files not specified", file=sys.stderr)
            self.parser.print_help(sys.stderr)
            sys.exit(1)
        
    
    def get_input(self):
        print(self.args.input)