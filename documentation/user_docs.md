# User documentation for the MCC (Metric Calculation and Comparison) tool

The MCC is a command line tool developed in Python.

It can calculate metrics and compare their results for segment alligned documents.

## Installation

The tool uses various Python libraries, which need to be installed in advance. For this it is recommended to create a Python Virtual Environment.

To create it, use:

```console
$ python -m venv bc_venv
```

Activate the virtual environment using:

```console
$ source bc_venv/bin/activate
```

For installation of the required libraries, run:
```console
$ pip install -r requirements.txt
```

## Data and Language Model

### Data

To obtain the data used specifically for the thesis use the following command:

```console
$ make data
```

This will download and extract the standard reference translations (SRT) and optimal reference translations (ORT) (http://hdl.handle.net/11234/1-5141).

This attachment includes the machine translations in a compressed format (`newstest2020sgm-v2.tar.gz`). These are also extracted. Then, for each selected translation, the articles corresponding to the articles for which ORTs are available are included.

The data is split into a train and test set. Additionally, for the train test the files containing the training source (english) three times, N1 three times, and concatenated P1, P2 and P3.

The directories in which specific results of the tool are saved are also created here.

### Language Model

To train the language models used to compute LM-based metrics, run:

```console
$ make train_lm
```

This downloads the data used for training, preprocesses it, and trains the language models used in the thesis. The models are converted to a `.binary` format and saved into the `source/resources` directory.

The training requires some time, and thee trained models are too large to be submitted with the thesis, but can be provided upon request.

## Usage

### Basic invocation

To use the MCC tool, change to the `source` directory.

Usage:

`MCC.py [-h] [-m [METRIC ...]] [-i [INPUT ...]] [-o OUTPUT] [-c [CHOOSE ...]] [--model [MODEL]] [--compare COMPARE] [--add_comparison ADD_COMPARISON] [--csv [CSV]] [--tsv [TSV]] [--latex [LATEX]] [-u [UNIT]] [--extract [EXTRACT ...]] [--highlight [HIGHLIGHT]] [--test [TEST]] original`

### Files (original, input and output)

`original` stands for the original file (English in the thesis); it is an obligatory argument. It takes exactly one filename.

With the `-i` option a list of input files (Czech in the thesis) should be specified. At least two input files are required.

When the `--test` option is used, the tool searches for the input files in the `data/test/` directory, otherwise in `data/train`.

In the `.txt` format of the original or the input file, the articles should be divided by an empty line, and each article should start with `# article name`. The articles should be segment-aligned.

With the `-o` option the output file is specified. When also using one of the `--tsv`, `--csv` or `--latex` option, it is not necessary to provide an output file since it is automatically generated and named `out_inp1vsinp2` with the appropriate file extension. However, when the `-o` option is used, the name of the otput file will be the one specified here, adding to it the appropriate extension. Otherwise, when the output is not specified, standard out will be used, and the output will contain a table with the results of the calculations.

In all cases, only add the filename without the file extension. In the case of the original file and the input files, the program first tries to open a `.conllu` file. If it isn't found, it tries to open a `.txt` file, load the text from there and use the udapi (udpipe) parser to analyze the text. Once a text is analyzed, the tagged version is saved to a `.conllu` file with the same name. When the output file is specified, the program adds the appropriate file extension to the name.

### tsv, csv and latex

Always use only one of the `-csv`, `-tsv` and `-latex` options to obtain the resulting table in a `csv`, `tsv` or `tex` format. When a `.tex` file is created, it contains the values of the metrics rounded to 3 decimal places; in the other two cases, the exact values are saved. The `csv` and the `tsv` formats contain no header. The `tex` format only includes the last table computed. (Note: The purpose of the `--latex` option was to generate the tables that will be contained in the thesis; we didn't plan to input tables for each of the articles.)

### Metrics

The metrics serve to compute the metrics specified in the thesis; for a more detailed description, refer to its Section 3.

When multiple input files are provided, the metrics are calculated for each.

When only one of the metrics is to be calculated, specify it using the `-m METRIC` option. Possibilities are:
- `deprel`: Dependency Relations
- `feats`: Features
- `nominalization`: Nominalization
- `length`: Length in number of words
- `lex_density`: Lexical Density (recognized by the upos tags `ADV`, `ADJ`, `VERB`, `NOUN`, `PROPN`)
- `lm_score`: Language Model Score
- `passives`: number of occurrences of passive voice, included in the `feats` option too (not used in the thesis)
- `perplexity`: Perplexity
- `pos`: Part-of-speech Tags 
- `sent_ttr`: Sentence Type-toke Ratio
- `syntactic_comp`: Syntactic complexity
- `tree_depth`: Tree Depth
- `tree_width`: Tree Width
- `ttr`: Type-token Ratio
- `untranslated`: Untranslated
- `word_per_line`: number of words in a line (not used in the thesis)
 
At least one metric has to be specified.

When computing lm score or perplexity, the path to the model has to be specified using the `--model` option

Not all metrics are compatible, since they us a different divisor when computing a ratio (e.g. pos are divided by number of words, feats by number of occurance of a given feature, and tree depth by number of segments) The compatible metrics among the ones used in the thesis are:
- length
- deprel, nominalization, lex_density, pos, untranslated, ttr
- lm_score, perplexity, syntactic_comp, tree_depth, tree_width, sent_ttr
- feats

For selecting a concrete part of options that measure multiple elements (deprel, feats, pos), use `-c [CHOOSE ...]` and specify the desired parts (e.g. `-c NOUN PROPN -m pos` to select nouns and proper nouns from the part-of-speech tags).

### Unit

To specify for which unit of the input file the metrics should be computed, use `--unit UNIT`, where the accepted options are:
- `sentence`: to calculate the metrics on the segment level (Note: Initially, we assumed a sentence segmentation and did not rename it)
- `article`: to calculate the metrics on the article level
- `whole`: to calculate the metrics on the level of the whole document, i.e. all of the segments in the input files are considered as a whole

It is defaulted to `whole`. 
When the output is the standard output, the resulting tables are printed individually, separated by the prompt `Press ENTER to print next table`. If the output file is in `csv` or `tsv` format, the tables are not divided. 

### Comparison

For comparing two of the files containing a translation the `--compare COMPARE` option is to be used. Only the first two input files are compared, and a new column containing the comparison results is added to the output. The rows are sorted by this column, called Comparison. When a t-test is performed, the Comparison (p-val) column is added, containing the p-value of the resulting t-test. `COMPARE` can be one of the following string values:
- `difference_W`: to calculate the difference of the results of the metric in percentages - with pos and deprel, it assigns equal importance to words
- `difference_S`: to calculate the difference of the results of the metric in percentages - with pos and deprel, it assigns equal importance to segments
- `ttest_abs`: to perform a t-test on the absolute values of the results for a metric on a segment level
- `ttest_perc`: to perform a t-test on the percentual values of the results for a metric on a segment level 

The resulting table is sorted by the column resulting from this comparison. If a column for difference as well as for t-test is added, it is sorted based on the Comparison column.

When an additional comparison is to be performed, add it using `--add_comparison ADD_COMPARISON`. 

### Highlighting

To highlight a metric in a selected segment, use `--extract [EXTRACT ...] --highlight [HIGHLIGHT]`, where the `--extract` option takes the order of the segment(s) to be extracted, and the `--highlight` option the metric to be highlighted. Highlighting was only developed for length and part-of-speech tags.
