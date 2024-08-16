all: req help

help:
	python3 metrics.py --help

###
basics: N1vsP1 N1vsP2 N1vsP3 N2vsP1 N2vsP2 N2vsP3

N1vsP1:
	./MCC.py english -i N1 P1 -u whole -m lm_score --model resources/news19_3gram.binary --compare difference_W --add_comparison ttest_abs

N1vsP2:
	./MCC.py english -i N1 P2 -u sentence -m length --compare difference_S --csv

N1vsP3:
	./MCC.py english -i N1 P3 -u sentence -m length --compare difference_S --csv

N2vsP1:
	./MCC.py english -i N2 P1 -u sentence -m length --compare difference_S --csv

N2vsP2:
	./MCC.py english -i N2 P2 -u sentence -m length --compare difference_S --csv

N2vsP3:
	./MCC.py english -i N2 P3 -u sentence -m length --compare difference_S --csv
# --extract 208 265 495

###
# deprel: 

N1vsP1_deprel:
	./MCC.py english -i N1 P1 -u whole -m deprel --compare difference_S


###
choices: N1vsP1_c N1vsP2_c N1vsP3_c N2vsP1_c N2vsP2_c N2vsP3_c

significant_pos: N1vsAll_adv N1vsAll_adp N1vsAll_pron N1vsAll_verb N1vsAll_cconj N1vsAll_punct N1vsAll_adj N1vsAll_aux N1vsAll_sconj N1vsAll_num N1vsAll_sym

N1vsAll_adv:
	./MCC.py English -i ORT SRT -u sentence -m pos --compare difference_W -c ADV --csv -o N1vsAll_s_ADV

N1vsAll_ttr:
	./MCC.py English -i ORT SRT -u sentence -m ttr --compare difference_W -c TTR --csv -o N1vsAll_s_TTR

N1vsAll_adp:
	./MCC.py English -i ORT SRT -u sentence -m pos --compare difference_W -c ADP --csv -o N1vsAll_s_ADP --extract 425 891 1204 1224 1471

N1vsAll_pron:
	./MCC.py English -i ORT SRT -u sentence -m pos --compare difference_W -c PRON --csv -o N1vsAll_s_PRON

N1vsAll_verb:
	./MCC.py English -i ORT SRT -u sentence -m pos --compare difference_W -c VERB --csv -o N1vsAll_s_VERB

N1vsAll_cconj:
	./MCC.py English -i ORT SRT -u sentence -m pos --compare difference_W -c CCONJ --csv -o N1vsAll_s_CCONJ

N1vsAll_punct:
	./MCC.py English -i ORT SRT -u sentence -m pos --compare difference_W -c PUNCT --csv -o N1vsAll_s_PUNCT

N1vsAll_adj:
	./MCC.py English -i ORT SRT -u sentence -m pos --compare difference_W -c ADJ --csv -o N1vsAll_s_ADJ --extract 100 202 401 713 777 1122 1262

N1vsAll_aux:
	./MCC.py English -i ORT SRT -u sentence -m pos --compare difference_W -c AUX --csv -o N1vsAll_s_AUX

N1vsAll_sconj:
	./MCC.py English -i ORT SRT -u sentence -m pos --compare difference_W -c SCONJ --csv -o N1vsAll_s_SCONJ

N1vsAll_num:
	./MCC.py English -i ORT SRT -u sentence -m pos --compare difference_W -c NUM --csv -o N1vsAll_s_NUM

N1vsAll_sym:
	./MCC.py English -i ORT SRT -u sentence -m pos --compare difference_W -c SYM --csv -o N1vsAll_s_SYM

N1vsP1_c:
	./MCC.py english -i N1 P1 -u article -m pos -c ADV --csv -o N1vsP1_s_ADV

N1vsP2_c:
	./MCC.py english -i N1 P2 -u article -m pos -c ADV --csv -o N1vsP2_s_ADV

N1vsP3_c:
	./MCC.py english -i N1 P3 -u article -m pos -c ADV --csv -o N1vsP3_s_ADV

N2vsP1_c:
	./MCC.py english -i N2 P1 -u article -m pos -c ADV --csv -o N2vsP1_s_ADV

N2vsP2_c:
	./MCC.py english -i N2 P2 -u article -m pos -c ADV --csv -o N2vsP2_s_ADV

N2vsP3_c:
	./MCC.py english -i N2 P3 -u article -m pos -c ADV --csv -o N2vsP3_s_ADV

###
importance_word: N1vsOnline-B_perc_whole N1vsCDT_perc_whole P2vsOnline-B_perc_whole P2vsCDT_perc_whole N1vsP1_perc_whole N1vsP2_perc_whole N1vsP3_perc_whole N2vsP1_perc_whole N2vsP2_perc_whole N2vsP3_perc_whole

ORTvsSRT_word_based:
#./MCC.py English -i ORT SRT -u whole -m nominalization length lex_density pos ttr untranslated --compare difference_W --add_comparison ttest_perc -o N1vsAll --latex
	./MCC.py English -i ORT SRT -m nominalization length lex_density pos deprel untranslated --compare difference_W --add_comparison ttest_perc -o ORTvsSRT_word_based --latex

N1vsOnline-B_perc_whole:
	./MCC.py english -i N1 B -u whole -m nominalization length lex_density pos deprel ttr untranslated --compare difference_W --add_comparison ttest_perc -o N1vsB_s --latex

N1vsCDT_perc_whole:
	./MCC.py english -i N1 DocTransformer -u whole -m nominalization length lex_density pos deprel ttr untranslated --compare difference_W --add_comparison ttest_perc -o N1vsCDT_s --latex

P2vsOnline-B_perc_whole:
	./MCC.py english -i P2 B -u whole -m nominalization length lex_density pos deprel ttr untranslated --compare difference_W --add_comparison ttest_perc -o P2vsB_s --latex

P2vsCDT_perc_whole:
	./MCC.py english -i P2 DocTransformer -u whole -m nominalization length lex_density pos deprel ttr untranslated --compare difference_W --add_comparison ttest_perc -o P2vsCDT_s --latex
 
N1vsP1_perc_whole:
	./MCC.py english -i N1 P1 -u whole -m nominalization length lex_density pos deprel ttr untranslated --compare difference_W --add_comparison ttest_perc -o N1vsP1_s --latex

N1vsP2_perc_whole:
	./MCC.py english -i N1 P2 -u whole -m nominalization length lex_density pos deprel ttr untranslated --compare difference_W --add_comparison ttest_perc -o N1vsP2_s --latex

N1vsP3_perc_whole:
	./MCC.py english -i N1 P3 -u whole -m nominalization length lex_density pos deprel ttr untranslated --compare difference_W --add_comparison ttest_perc -o N1vsP3_s --latex

N2vsP1_perc_whole:
	./MCC.py english -i N2 P1 -u whole -m nominalization length lex_density pos deprel ttr untranslated --compare difference_W --add_comparison ttest_perc -o N2vsP1_s --latex

N2vsP2_perc_whole:
	./MCC.py english -i N2 P2 -u whole -m nominalization length lex_density pos deprel ttr untranslated --compare difference_W --add_comparison ttest_perc -o N2vsP2_s --latex

N2vsP3_perc_whole:
	./MCC.py english -i N2 P3 -u whole -m nominalization length lex_density pos deprel ttr untranslated --compare difference_W --add_comparison ttest_perc  -o N2vsP3_s --latex

####
N1vsAll_LM:
	./MCC.py English -i ORT SRT -u whole -m lm_score --model resources/news19_4gram.binary --compare difference_W --add_comparison ttest_abs -o N1vsAll_lm --latex

N1vsAll_Perp:
	./MCC.py English -i ORT SRT -u whole -m perplexity --model resources/news19_3gram.binary --compare difference_W --add_comparison ttest_abs -o N1vsAll_perp --latex

N1vsAll_synt:
	./MCC.py English -i ORT SRT -u whole -m tree_depth tree_width syntactic_comp --compare difference_W --add_comparison ttest_abs -o N1vsAll_synth --latex

N1vsAll_SC:
	./MCC.py English -i ORT SRT -u whole -m syntactic_comp --compare difference_W --add_comparison ttest_abs -o N1vsAll_syntactic --latex

#####
ttest_perc_whole_feats: N1vsOnline-B_perc_whole_feats N1vsCDT_perc_whole_feats P2vsOnline-B_perc_whole_feats P2vsCDT_perc_whole_feats N1vsP1_perc_whole_feats N1vsP3_perc_whole_feats N2vsP1_perc_whole_feats N2vsP2_perc_whole_feats N2vsP3_perc_whole_feats

N1vsAll_feats:
	./MCC.py English -i ORT SRT -u whole -m feats --compare difference_W --add_comparison ttest_perc -o N1vsAll --latex

N1vsOnline-B_perc_whole_feats:
	./MCC.py english -i N1 B -u whole -m feats --compare difference_W --add_comparison ttest_perc -o N1vsB_feats

N1vsCDT_perc_whole_feats:
	./MCC.py english -i N1 DocTransformer -u whole -m feats --compare difference_W --add_comparison ttest_perc -o N1vsCDT_feats

P2vsOnline-B_perc_whole_feats:
	./MCC.py english -i P2 B -u whole -m feats --compare difference_W --add_comparison ttest_perc -o P2vsB_feats

P2vsCDT_perc_whole_feats:
	./MCC.py english -i P2 DocTransformer -u whole -m feats --compare difference_W --add_comparison ttest_perc -o P2vsCDT_feats
 
N1vsP1_perc_whole_feats:
	./MCC.py english -i N1 P1 -u whole -m feats --compare difference_W --add_comparison ttest_perc -o N1vsP1_feats

N1vsP2_perc_whole_feats:
	./MCC.py english -i N1 P2 -u whole -m feats --compare difference_W --add_comparison ttest_perc -o N1vsP2_feats

N1vsP3_perc_whole_feats:
	./MCC.py english -i N1 P3 -u whole -m feats --compare difference_W --add_comparison ttest_perc -o N1vsP3_feats

N2vsP1_perc_whole_feats:
	./MCC.py english -i N2 P1 -u whole -m feats --compare difference_W --add_comparison ttest_perc -o N2vsP1_feats

N2vsP2_perc_whole_feats:
	./MCC.py english -i N2 P2 -u whole -m feats --compare difference_W --add_comparison ttest_perc -o N2vsP2_feats

N2vsP3_perc_whole_feats:
	./MCC.py english -i N2 P3 -u whole -m feats --compare difference_W --add_comparison ttest_perc -o N2vsP3_feats

###
graphs:
	./extrac_graphs.py for_graphs/N1vsAll_ADV.csv
	./extrac_graphs.py N1vsP1_s_ADV.csv 
	./extrac_graphs.py N1vsP2_s_ADV.csv 
	./extrac_graphs.py N1vsP3_s_ADV.csv 
	./extrac_graphs.py N2vsP1_s_ADV.csv 
	./extrac_graphs.py N2vsP2_s_ADV.csv 
	./extrac_graphs.py N2vsP3_s_ADV.csv 
