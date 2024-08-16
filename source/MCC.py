#!/usr/bin/env python3

import argparse
import udapi
import sys
import os
import numpy as np

from align_metrics import Aligner
from arguments import Arg
from handler import Handler
from tool import Tool
from errors import *

def main(p):
    handler = Handler(p)
    handler.get_sent_result()

    ttest = False if p.args.compare in ["difference_W", "difference_S"] else True

    # Extracting given sentences, highlighting the differences
    if p.args.extract != False:
        aligner = Aligner(parser.args.model)

        p.args.extract = [int(x) for x in p.args.extract]
        extracted = handler.extract_text(p.args.extract)
        for i in range(len(p.args.extract)):
            t1 = extracted[1][i]            #translation 1 (0 is original, not aligning)
            t2 = extracted[2][i]            #translation 2
            aligned = aligner.align(t1, t2)
            aligner.find_metric_words(t1, t2, 0, aligned, p.args.highlight)
            aligner.find_metric_words(t2, t1, 0, aligned, p.args.highlight)
            input()
        quit()

    # get number of tables that need to be produced:
    table_num = handler.t.count_tables(p.args.unit)

    # get what to divide with for percentages
    if p.args.compare != "ttest_abs":
        handler.get_percent_denom()

    for i in range(table_num): 
        comparison_data = handler.get_data(i, ttest)
        if p.args.compare != "ttest_abs":
            handler.format_denom(i, for_ttest=ttest)
            
        handler.format_table(i)       
        handler.compare(comparison_data)
        
        
        if p.args.add_comparison != False:
            comparison_data = handler.get_data(i, (False if p.args.add_comparison in ["difference_W", "difference_S"] else True))
            if p.args.add_comparison != "ttest_abs":
                handler.get_percent_denom(for_add=True)
                handler.format_denom(i, for_ttest=(False if p.args.add_comparison in ["difference_W", "difference_S"] else True))
            handler.compare(comparison_data, add_comparison=True)
        handler.add_choice(i)
        handler.sort()
        handler.print_table()    


if __name__ == '__main__':
    parser = Arg()
    parser.parse()
    main(parser)

