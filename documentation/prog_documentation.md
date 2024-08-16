# Programmer documentation for the MCC (Metric Calculation and Comparison) tool

## Command line arguments

The command line arguments are processed by the `argparse` library and defined in the `argparse.py` folder.

For details on the positional and optional arguments use  `./MCC.py --help` or read the user documentation.

## Handler class

This class manages the communication between input, computation and output creation. It contains a Tool object and a Table object

```python
Handler.get_sent_result(self)
```
Checks if the options for metrics obtained from the command line are known, and computes them and stores in `Handler.sent_result`. Raises an exception if a metric is not known, or if a metric that requires a language model is requested to be computed, and no language model is provided via the `--model` option.

```python
Handler.get_percent_denom(self, for_add=False)
```
Computes the denominator to be used to calculate percentages:
- for features it's the Feature keys (i.e. for the feature VerbForm.Fin, the feature key is VerbForm)
- for length, lm_score, perplexity, syntactic_comp, tree_depth, tree_width, sent_ttr it's the number of lines
- otherwise it's the length (token count)

```python
Handler.format(self, to_format, i, use_feat_keys=True, ttest=False)
```

```python
Handler.compare(self, data, add_comparison=False)
```
Manages adding a comparison column to the Table and the removment of values that give low differences.

```python
Handler.sort(self)
```
Manages sorting of the table. If comparison for difference as well as for ttest was performed, it is sorted according to the column containing the difference.

```python
Handler.add_choice(self, idx)
```
Modifies the Table to only contain submetrics (e.g. ADJ is a submetric of pos) specified by the `-c` option on the command line. If a submetric is not between the ones that were computed, raises an exception.

```python
Handler.print_table(self)
```
Manages Table printing based on the output file - whether to print to a .csv, .tsv, .txt, .tex or to command line.

Formats the data in `to_format` using `Tool.format()` or `Tool.ttest_format()`. Is used by methods `Handler.format_table()` and `Handler.format_denom()` to format either the table or the denominator used for percentage calculation, and also by method `Handler.get_data()` to obtain data for comparison.

## Tool class

This class is managing the Documents, the computation of the metrics and the extraction of selected parts and formatting of the result. It contains:
- `Tool.documents`: a list of the documents, where the first is the original (!) and the rest are the translations
- `Tool.structure`: the structure of all the documents, it should be the same for each Document, since segment alignment is expected. This is checked using the `Tool.compare_structure()` method, and an exeption is raised
- `Tool.m`: an instance of the Metric class
- `Tool.encountered`: initialized as none, later containing the metrics that have been computed, is used for extraction of a part of the results

```python
Tool.compute_metrics(self, metrics)
```
This metric returns a list containing a list of Counters for each segment for each document. 

If nominalization is to be counted, loads the file containing the Czech nominalizations from the resources directory. Then it presets the Counter for the English text with 0 for metrics, where it doesn't make any sense to compute the metric for that language (e.g. untranslated, or lm_score). Computes the metrics for each segment in each document.

```python
Tool.format_result(self, res, encoun, sentence=None, start_s=None, end_s=None, ttest=False)
```
Returns the result formatted for the unit or t-test. When formatting for t-test, since it is computed on segment level, this method is called for each segment and returns a list of Counters with the computed metrics for the segment. When formatting for unit (i.e. to the form that goes in the table), it returns a list of lists, where each of the inner lists contain the name of the metric and its result for the unit.

If the `sentence` parameter is provided, the formatted results for the segment with this index are returned. If parameters `start_s` and `end_s`, containing the index of the first and the last segment of an article, the formatted results for this article are returned. Otherwise, the formatted results for the whole document are returned.

```python
Tool.extract_part(self, res, sentence=None, start_s=None, end_s=None)
```
Returns a list of Counters for all documents the part of res either:
- `extract_part(res, sentence=n)`: corresponding to the sentence at the n-th sentence
- `extract_part(res, start_s=i, end_s=j)`: corresponding to the article ranging from the i-th sentence to the j-th sentence
- `extract_part(res)`: corresponding to the whole

## Document class

This class serves for representing a document (collection of articles divided to segments). It has three properties: 
- the `Document.name` containing the name of the document, 
- the `Document.original`, a boolean value indicating whether it is the document in the source language (English), needed to determine which parser to use,
- the `Document.doc` containing the tokenized, tagged and parsed `udapi.Document` object

```python
Document.load(self, name, original)
```
This method is responsible for assigning the `Document.doc`. First tries to initialize the `udapi.Document` object with a `.conllu` file (created as `name + ".conllu"`). If this fails, it attempts to initialize it with a `.txt` file (`name + ".txt"`), removing the empty lines and the lines starting with `#`. Then the document is processed using the `Document.tag()` method. After parsing the document, a `.conllu` file is created with the document, since multiple uses of a single document are expected, and parsing costs more time. If the `.txt` file is not found, ends in an Exception.

```python
Document.tag(self, doc, original)
```
Depending on whether it is the original (English) or translated (Czech) document, the model for parsing is selected. For tokenizing, tagging and parsing the [udapi](https://github.com/udapi/udapi-python) tool is used, with the pretrained UDPipe parsers. 

```python
Document.get_structure(self)
```
This method returns a list with segment counts of each article contained in the document. The first segment of an article is marked with a `newdoc` flag, contained in the root node of the tree.

```python
Document.extract(self, indices)
```
Used to extract (return and print) selected sentences, contained in the `indices` list. It traverses all the sentences in the document, and check if it is contained in the `inidces` list.

## Metrics class

This class is responsible for calculating the metrics on the segment level. It has a variable called `Mentrics.encountered_metrics`, where the metric that have been computed are stored. This variable then serves for selecting the metrics when the data is formatted to produce a table.

The names of the method is called exactly like the command line argument that should be provided with the `-m` option for calculating the metric. For each metric a `collections.Counter()` is returned containing either the value of the metric for the given tree (sent_ttr, tree_depth, tree_width, syntactic_comp, perplexity, lm_score, length, lines), the counts of underlying metrics (pos,deprel, feats, lex_density, nominalization, untranslated) or specifically for ttr, the set of types in the sentence. For detailed 

```python
Metrics.list_metric(self, tree, metric)
```
Used by the Aligner, returnes list of nodes from the tree, which correspond to the metric.

```python
Metrics.token_freq(self, tree, stop_w=False, lemmatized=False)
```

Used by methods `Metrics.untranslated()`, `Metrics.sent_ttr()` and `Metrics.ttr()` to obtain a token frequency list (a python `dict` with word:count pairs). For the counting of untranslated words, the stop words are excluded. These stop words are words that have the same form in English and Czech, but have different meanings (e.g. _my_, _to_ or _by_). Both types of type-token ratio can request the frequency list counted for lemmas or forms. A handler for this was not implemented, so it needs to be changed manually in the definition of the methods.

The methods `Metrics.depth(self, node)` and `Metrics.width(self, root)` implement recursive Depth-First Search, and Breadt-First Search, to obtain the depth and the width of the tree.

## Table class

This class manages the table. it has a variable called `Table.table` which contains a two-dimensional array of its rows.

For standart output and plain-text it implements an own character-based table design, which looks like this:
```
+--------+-----------+-----------+-----------+--------------------+
| Metric |  English  |    ORT    |    SRT    | Comparison (p-val) |
+--------+-----------+-----------+-----------+--------------------+
| Length | 55095.000 | 53700.000 | 50921.000 |             <0.001 |
+--------+-----------+-----------+-----------+--------------------+
```
When printing this format, the `Table.print()` method is used.

For printing a table in a specific format (csv, tsv, tech) the corresponding methods beginning with `write` followed by the format are used.

It is responsible for executing the percentage calculation, difference computation, and the printing of the table.

```python
Table.calculate_percentages(self, inp_data, lens, features, perpl)
```
This method divides `inp_data` by `lens`. The `lens` were computed and formatted previously based on the metrics computed. If the `features` parameter is set to True, a special approach is used, given the different format of the `lens` for features (contains value for each feature key, and the key corresponding to the feature has to be used). The `perpl` methot indicates, whether the result is or isn't multiplied by 100.

```python
Table.ttest(self, x1, x2)
```
Performs a paired t-test on samples `x1` and `x2` usingy the `stats.ttest_rel()` method, whose `alternative` parameter is preset to `"two-sided"` calculating the two-tailed paired t-test. To compute an upper-tailed or lower-tailed t-test, this parameter needs to be manually changed here to `"greater"` or `"lower"`, no hnadler is implemented for this. If the format of `x1` or `x2` is not supported, an exception is raised. Returns the obtained p-value.

```python
Table.add_diff_column(self, formatted_data, diff_type, c1, c2, length_lst=[], features=False, dont_multiply=False, add_col=False):
```
Adds a comparison column based on the `diff_type` for columns `c1` and `c2`. If a comparison other than the t-test on absolute values is performed, computes the percentages using `Table.calculate_percentages()`. Computes the differenc, or if t-test is required, calls the `Table.ttest()` method.

```python
Table.remove_low_comparison(self, idx)
```
Removes rows where the comparison is low, i.e. the difference is 0, or the p-value is nan.

## Aligner

The Aligner class implements a simple word aligner, which is used to facilitate the identification of words responsible for a difference at a segment level. It aligns the words, and it highlights the words.

```python
Aligner.align(self, tree1, tree2)
```
Alignes the nodes from tree1 with the nodes in tree2. All pairs of nodes are produced, then sorted by similarity. The similarity takes into account the word form and the order of the word in the segmnet, and is obtained using `difflib.SequenceMatcher()`. The sorted list is then traversed and the alignment pairs are selected hungrily, marking the nodes already aligned. The nodes that were left unaligned are saved in the `Aligner.not_aligned` variable.

```python
Aligner.find_metric_words(self, tree1, tree2, idx, aligned, metric)
```
Marks the words corresponding to metric, and the ones that are responsible for a difference in the metric. First, it identifies the words that correspond to metric via the `Metrics.list_metric()` method. Then for each word in the tree, it checks if it belogs to this list. If yes, it's marked with the "\M{}" mark, showing it belongs to the metric. If it also has not been aligned, or is aligned with a word, that does not correspond to the metric, it's marked with the "\D{}" mark, signifying it is responsible for the difference.

## errors

Some custom errors are defined in the `errors.py` file.

## MCC

The `MCC.py` is the file containing the `main()` function. It uses one instance of the `Handler` object to compute the desired tables containing the results and comparisons of the metrics, or an instance of Handler and an instance of Aligner to extract selected segments and highlight a given metric.