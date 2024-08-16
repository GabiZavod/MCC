#!/usr/bin/env python3

import os
import sys
from tool import Tool
from table import Table
from errors import *
from collections import Counter

TTEST_ON_SENTENCES = True

class Handler:
    def __init__(self, parser):
        self.p = parser
        self.to_compute = self.p.args.metric
        current_dir = os.getcwd()
        data_dir = "data/test" if parser.args.test else "data/train"

        self.t = Tool(   os.path.join(current_dir, "..", data_dir, parser.args.original),
                    [os.path.join(current_dir, "..", data_dir, inp_file) for inp_file in parser.args.input],
                    parser.args.model
                )
        
        # create output file
        if parser.args.output != sys.stdout and not parser.args.csv and not parser.args.tsv and not parser.args.latex:
            self.output = open("results/" + parser.args.output + ".txt", "wt", encoding="utf8")
        else:
            self.output = parser.args.output
        
        # initialize table
        self.table = Table(parser.args.unit, parser.args.compare)
        comparison_num = 0
        if parser.args.compare != False and parser.args.add_comparison != False:
            comparison_num = 2
        elif parser.args.compare != False:
            comparison_num = 1
        self.table.set_field_names(["Metric"] + [f for f in [parser.args.original] + parser.args.input], comparison_num)

        self.sent_result = None
        self.feat_keys = None
        self.current_denom = {}
        self.denom = None
    
    def extract_text(self,i):
        return self.t.extract_text(i)
    
    def get_sent_result(self):
        """Compute metrics for each document"""
        # get metrics to be computed
        if self.p.args.metric[0] == "all":
            self.to_compute = self.p.possible_actions
        
        # check if all actions to be computed are known
        try:
            for a in self.to_compute:
                if a not in self.p.possible_actions:
                    raise UnknownActionError(a, self.p.possible_actions)
        except UnknownActionError as e:
            print(e.message, file=sys.stderr)
            sys.exit(1)
        
        # check if model has been selected for lm_score or perplexity
        try:
            if "lm_score" in self.to_compute and self.p.args.model == False:
                raise MissingModelError("lm_score")
            if "perplexity" in self.to_compute and self.p.args.model == False:
                raise MissingModelError("perplexity")
        except MissingModelError as e:
            print(e.message, file=sys.stderr)
            sys.exit(1)
        
        # compute metrics on sentence level for each document
        self.sent_result = self.t.compute_metrics(self.to_compute)
    
    def get_percent_denom(self, for_add=False):
        # compute denominator to be able to obtain percentages
        for_result = self.p.args.add_comparison if for_add else self.p.args.compare
        # compute feature keys when computing features
        if self.to_compute[0] == "feats":
            orig_encountered = set(self.t.encountered)
            self.denom = self.t.compute_metrics(["feat_keys"])
            self.feat_keys = self.t.encountered - orig_encountered
            self.t.encountered = orig_encountered
        elif self.to_compute[0] in ["length", "lm_score", "perplexity", "syntactic_comp", "tree_depth", "tree_width", "sent_ttr"]:
            self.denom = self.t.compute_metrics(["lines"])
        # compute length otherwise
        else:
            self.denom = self.t.compute_metrics(["length"])
            if "length" not in self.to_compute:
                self.t.encountered.remove("Length")
        
    def format(self, to_format, i, use_feat_keys=True, ttest=False):
        """Return to_format based on unit"""
        changed_feat_keys = False
        if not use_feat_keys and self.feat_keys is not None:
            fk_copy = self.feat_keys.copy()
            self.feat_keys = None
            changed_feat_keys = True

        if self.p.args.unit == "whole":
            if ttest:
                whole = []
                if TTEST_ON_SENTENCES:
                    for j in range(sum(self.t.structure)):
                        
                        whole.append(self.t.format_result(to_format,self.feat_keys, sentence=j, ttest=True))
                else:
                    for j in range(len(self.t.structure)):
                        whole.append(self.t.format_result(to_format, self.feat_keys, start_s=sum(self.t.structure[:j]), end_s=sum(self.t.structure[:j+1]), ttest=True))
                r = self.t.ttest_format(whole, self.feat_keys)
                
            else:
                r = self.t.format_result(to_format, self.feat_keys)
        elif self.p.args.unit == "article":
            if ttest:
                whole = []
                # add all sentences corresponding to the article
                for j in range(sum(self.t.structure[:i]), sum(self.t.structure[:i+1])):
                    whole.append(self.t.format_result(to_format, self.feat_keys, sentence=j, ttest=True))
                r = self.t.ttest_format(whole,self.feat_keys)
            else:
                r = self.t.format_result(to_format, self.feat_keys, start_s=sum(self.t.structure[:i]), end_s=sum(self.t.structure[:i+1]))
          
        elif self.p.args.unit == "sentence":
            r = self.t.format_result(to_format, self.feat_keys, sentence=i)
        
        if changed_feat_keys:
            self.feat_keys = fk_copy

        return r

    def get_data(self, i, for_ttest):
        """Return data for comparison"""
        if for_ttest:
            return self.format(self.sent_result, i, use_feat_keys=False, ttest=True)
        else:
            return self.format(self.sent_result, i, use_feat_keys=False)
    
    def format_table(self,i):
        """Format table"""
        self.table.table = self.format(self.sent_result, i, use_feat_keys=False)
    
    def format_denom(self, i, for_ttest):
        """Format the denominator"""
        if self.to_compute[0] == "feats":
            ud_features = self.format(self.denom, i, ttest=for_ttest)
            self.current_denom = {}
            for feature in ud_features:
                self.current_denom[feature[0]] = feature[1:]
        elif self.to_compute[0] in ["length", "lm_score", "perplexity", "syntactic_comp", "tree_depth", "tree_width", "sent_ttr"]:
            self.feat_keys = set(["Lines"])
            self.current_denom = self.format(self.denom, i, ttest=for_ttest)
        else:
            self.feat_keys = set(["Length"])
            self.current_denom = self.format(self.denom, i, ttest=for_ttest)

    def compare(self, data, add_comparison=False):
        """Compare results"""
        if add_comparison and self.p.args.add_comparison != False:
            if self.p.args.add_comparison == "ttest_abs":      # or self.p.args.metric[0] == "length":
                self.table.add_diff_column(data, self.p.args.add_comparison, 2, 3, add_col=True)
            else:
                use_feats = False
                no_mult = False
                if self.to_compute[0] == "feats":
                    use_feats = True
                # metrics perplexity and syntactic complexity, we're not computing percentages
                if self.to_compute[0] in ["length", "perplexity", "syntactic_comp", "tree_depth", "tree_width", "sent_ttr"]:
                    no_mult = True
                
                self.table.add_diff_column(data, self.p.args.add_comparison, 2, 3, length_lst=self.current_denom, features=use_feats, dont_multiply=no_mult, add_col=True)
            # Remove low values according to first comparison
            self.table.remove_low_comparison(-2)
            return
        if self.p.args.compare != False:
            if self.p.args.compare == "ttest_abs":      #or self.p.args.metric[0] == "length":
                self.table.add_diff_column(data, self.p.args.compare, 2, 3)
            else:
                use_feats = False
                no_mult = False
                if self.to_compute[0] == "feats":
                    use_feats = True
                if self.to_compute[0] in ["length", "perplexity", "syntactic_comp", "tree_depth", "tree_width", "sent_ttr"]:
                    no_mult = True
                self.table.add_diff_column(data, self.p.args.compare, 2, 3, length_lst=self.current_denom, features=use_feats, dont_multiply=no_mult, add_col=True)
            if self.p.args.add_comparison == False:
                if self.p.args.choose == False:
                    self.table.remove_low_comparison(-1)

    def sort(self):
        """Sort table"""
        if self.p.args.compare != False:
            if self.p.args.compare in ["difference_S", "difference_W"]:
                self.table.sort_by("Comparison")
            else:
                self.table.sort_by("Comparison (p-val)")     

    def add_choice(self, idx):
        """Modyfi table to contaiin choosen metdrics"""
        if self.p.args.choose is not None:
            rows = self.table.get_row_names()
            
            for choice in self.p.args.choose:
                try:
                    if choice not in rows:
                        raise UnknownChoiceError(choice, rows)
                except UnknownChoiceError as e:
                    print(e.message, file=sys.stderr)
                    sys.exit(1)
            
            indices = []
            for i, row in enumerate(self.table.table):
                if row[0] in self.p.args.choose: 
                    # print(row)
                    if row[-1] >= 15:
                        print(idx)
                    indices.append(i)
        
            if indices:
                self.table.table = [row for i,row in enumerate(self.table.table) if i in indices]
                
    def print_table(self):
        # set allignment
        self.table.set_allign(0, "l")
        for i in range(1, len(self.table.field_names)):
            self.table.set_allign(i, "r")   

        #set output file
        if self.p.args.output == sys.stdout:
            out_f = "out_" + self.p.args.input[0] + "vs" + self.p.args.input[1]
        else: out_f = self.p.args.output    

        if self.p.args.csv:
            self.table.write_csv(out_f)
        
        elif self.p.args.tsv:
            self.table.write_tsv(out_f)

        elif self.p.args.latex:
            self.table.write_tech(out_f)
        
        else:
            self.table.print(file=self.output)
            input("Press ENTER to print next table")


