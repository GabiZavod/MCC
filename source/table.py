#!/usr/bin/env python3

import numpy as np
import sys
from scipy import stats
from errors import *

class Table:
    def __init__(self, unit, diff):
        self.table = []
        self.field_names = []
        self.allign = []
        self.unit = unit
        self.diff = diff
        self.corner = "+"
        self.horizontal = "-"
        self.vertical = "|"
        self.float_format = ".3"
        self.col_nums = 0
        return

    def set_field_names(self, names, comp_num):
        self.field_names = names
        self.allign = ["c" for _ in names]
        self.col_nums = len(self.field_names) + comp_num

    def set_allign(self, col_num, a_type):
        self.allign[col_num] = a_type

    def compare_size(self,row):
        """Check is the row that is being added matches the rest of the table"""
        if len(row) == len(self.field_names):
            return True
        else:
            raise NotMatchingSizeError(len(self.field_names), len(row))

    def add_row(self, row):
        try:
            self.compare_size(row)
        except NotMatchingSizeError as e:
            print(e.message, file=sys.stderr)
            sys.exit()
        self.table.append(row)

    def calculate_percentages(self, inp_data, lens, features, perpl):
        """Calculates percentages of inp_data/lens"""
        for row_idx,row in enumerate(inp_data):
            for i in range(1,len(row)):
                if features:
                    feat_name = row[0].split(".")[0]
                    if row[i] == 0:
                        continue
                    else:
                        if isinstance(row[i], list):
                            row[i] = [0 if (row[i][j] == 0 and lens[feat_name][i-1][j] == 0) else 100*row[i][j]/lens[feat_name][i-1][j] for j in range(len(row[i]))]
                            if self.table[row_idx][i] == 0:
                                continue
                            if len(self.table[row_idx]) >= self.col_nums-1:
                                self.table[row_idx][i] = 100*self.table[row_idx][i]/sum(lens[feat_name][i-1])
                        else:
                            row[i] = 100*(row[i]/lens[feat_name][i-1])
                            if len(self.table[row_idx]) >= self.col_nums-1:
                                self.table[row_idx][i] = 100*(self.table[row_idx][i]/lens[feat_name][i-1])

                elif perpl:
                    if isinstance(row[i], list):
                        
                        row[i] = [100*row[i][j]/lens[0][i][j] for j in range(len(row[i]))]
                        self.table[row_idx][i] = 100*self.table[row_idx][i]/sum(lens[0][i])
                    else:
                        row[i] = (row[i]/lens[0][i])          #lens[i-1][0]
                        self.table[row_idx][i] = self.table[row_idx][i]/lens[0][i]


                else:
                    if isinstance(row[i], list):
                        row[i] = [100*row[i][j]/lens[0][i][j] for j in range(len(row[i]))]
                        # row[i] = [100*row[i][j]/sum(lens[0][i]) for j in range(len(row[i]))]                #NOTE: this to be used, when I want to divide in t-test by "all words"
                        if len(self.table[row_idx]) >= self.col_nums-1:
                            self.table[row_idx][i] = 100*self.table[row_idx][i]/sum(lens[0][i])
                    else:
                        print(lens)
                        row[i] = (100*row[i]/lens[0][i])          #lens[i-1][0]
                        # NOTE: maybe not check on length, but if I will be adding anything further on
                        if len(self.table[row_idx]) >= self.col_nums-1:
                            self.table[row_idx][i] = 100*self.table[row_idx][i]/lens[0][i]
        return inp_data

    def ttest(self, x1, x2):
        """Compute paired t-test"""
        # null hypothesis: x1 and x2 have the same average
        # alternative hypothesis: the means are different
        # paired ttest
        with np.errstate(divide="raise"):
            try:
                result = stats.ttest_rel(x1,x2,alternative="two-sided")
            except FloatingPointError:
                print(f"Can't calculate t-test for two constant samples x1={x1} and x2={x2}", file=sys.stderr)
                exit(1)
        return result.pvalue            #result.statistic #

    def remove_low_comparison(self, idx):
        to_remove = []
        for i, row in enumerate(self.table):
            if (self.diff not in ["difference_W", "difference_S"] and np.isnan(row[idx])) or (self.diff in ["difference_W", "difference_S"] and abs(row[idx]) == 0):
                to_remove.append(i)
        self.table = [row for i,row in enumerate(self.table) if i not in to_remove]

    def add_diff_column(self, formatted_data, diff_type, c1, c2, length_lst=[], features=False, dont_multiply=False, add_col=False):
        """Add comparison column for c1 and c2 to the table"""
        if ("Comparison" not in self.field_names and "Comparison (p-val)" not in self.field_names) or add_col: 
            self.field_names.append("Comparison")
            self.allign.append("l")

        if diff_type != "ttest_abs":      
            formatted_data = self.calculate_percentages(formatted_data, length_lst, features, dont_multiply)

        for i, row in enumerate(formatted_data):
            diff = []
            if diff_type == "difference_S" or diff_type == "difference_W":
                diff = row[c1] - row[c2]
            elif diff_type == "ttest_abs":
                if self.field_names[-1][-1] != ")": self.field_names[-1] += " (p-val)"
                diff = self.ttest(row[c1], row[c2])
            else:
                if self.field_names[-1][-1] != ")": self.field_names[-1] += " (p-val)"
                diff = self.ttest(row[c1], row[c2])
            self.table[i].append(diff)        # append to table

    def get_col(self,field):
        i = self.field_names.index(field)
        return np.array([row[i] for row in self.table])

    def get_row_names(self):
        return [row[0] for row in self.table]

    def sort_by(self, field):
        """Sort table by field (column)"""
        col = self.get_col(field)
        indices = np.argsort(col)

        cp = self.table.copy()
        for i in range(len(self.table)):
            self.table[i] = cp[indices[i]]

    def get_max_and_min(self,n):
        max_diff = [int(row[0][3:]) for row in self.table[:n]]
        min_diff = [int(row[0][3:]) for row in self.table[-n:]]
        print(max_diff)
        print(min_diff)
        input()
        return max_diff, min_diff

    def write_sv(self, filename, separator):
        f = open("for_graphs/" + filename, 'a', newline='')
        for row in self.table:
            if row[-1] == -11:
                print(row)
                print(self.table.index(row))
            line = ""
            for i,unit in enumerate(row):
                if i == 0: line += unit + separator
                else:
                    # for datapoint in unit:
                    line += str(unit) + " "
                    line = line[:-1] + separator
            print(line[:-1], file=f)

        f.close()
        return

    def write_csv(self,filename):
        self.write_sv(filename, ",")

    def write_tsv(self, filename):
        self.write_sv(filename, "\t")

    def write_tech(self, filename):
        f = open("results/" + filename + '.tex', 'w', newline='')
        divided = False
        print(r"\begin{table}[htbp]", file=f)
        struct = "{"
        for a_type in self.allign:
            struct += a_type
        struct += "}"
        print(r"\begin{tabular}"+struct, file=f)
        print(r"\toprule", file=f)
        line = ""
        for element in self.field_names:
            line += element +" &"
        print(line[:-1] + r"\\", file=f)
        print(r"\midrule", file=f)
        for row in self.table:
            if row[-2] > 0 and not divided:
                print(r"\hline", file=f)
                divided = True
            line = ""
            for i,unit in enumerate(row):
                if i == 0: line += unit + " &"
                else:
                    # for datapoint in unit:
                    line += self.make_str(unit)+" "         #"{:.3f} ".format(unit)
                    line = line[:-1] + "&"
            # add highlight
            if self.field_names[-1] == "Comparison (p-val)":
                if round(row[-1], 3) <= 0.005:
                    if abs(row[-2]) > 1:
                        line = r"\rowcolor{purple!30}" + line
                    else:
                        line = r"\rowcolor{purple!20}" + line
            print(line[:-1] + r"\\", file=f)
        print(r"\bottomrule", file=f)
        print(r"\end{tabular}", file=f)
        # NOTE: Input caption manually here, or change after generating the table
        caption = f"Word based metrics ({self.field_names[2]} vs. {self.field_names[3]})"
        print(r"\caption{" + caption + r"}", file=f)
        # NOTE: Input label manually here, or change after generating the table
        label = f"tab:{self.field_names[2]}vs{self.field_names[3]}_wordbased"
        print(r"\label{" + label + r"}", file=f)
        print(r"\end{table}", file=f)
        f.close()

    def make_str(self, unit):
        if type(unit) == str:
            return unit
        if type(unit) == list:
            unit = sum(unit)

        if unit<0.001 and unit > 0:
            return "<0.001"
        s = ""
        s = "{:.3f}  ".format(unit)

        return s[:-2]

    def count_col_len(self):
        longests = np.array([0 for _ in self.field_names])

        for i,name in enumerate(self.field_names):
            if len(name) > longests[i]:
                longests[i] = len(name)
        for row in self.table:
            for i,unit in enumerate(row):
                if i==0 and len(unit) > longests[i]:
                    longests[i] = len(unit)
                elif i>0:
                    if len(self.make_str(unit)) > longests[i]:
                        longests[i] = len(self.make_str(unit))
        return longests

    def generate_sep(self, s):
        line = self.corner
        for l in s:
            line += self.horizontal * l
            line += self.corner
        return line

    def generate_line(self, row, s, center=False):
        line = self.vertical
        for i,data in enumerate(row):
            space = s[i] - len(self.make_str(data))
            if self.allign[i] == "c" or center:
                if space%2 == 0:
                    line += " "*(space//2) + self.make_str(data) + " "*(space//2) + self.vertical
                else:
                    line += " "*(space//2) + self.make_str(data) + " "*(space//2 + 1) + self.vertical
            elif self.allign[i] == "l":
                line += f" {self.make_str(data)}" + " "*(space-1) + self.vertical
            elif self.allign[i] == "r":
                line += " "*(space-1) + f"{self.make_str(data)} {self.vertical}"
            else:
                print("Error: unknown allignment", file=sys.stderr)
                exit(1)
        return line

    def print(self, file=sys.stdout):
        column_lengths = self.count_col_len() + 2
        sep = self.generate_sep(column_lengths)
        print(sep, file=file)
        print(self.generate_line(self.field_names, column_lengths, center=True), file=file)
        print(sep, file=file)
        for row in self.table:
            print(self.generate_line(row, column_lengths), file=file)
            print(sep, file=file)
        return

