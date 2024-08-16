all: req data train_lm

req:
	source bc_venv/bin/activate;	\
	pip install -r requirements.txt;	\
	echo "Installed all requierements"

data:
	mkdir data
# get source, human and optimal translations
	curl --remote-name-all https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-5141{/optimal-ref-translation-en-cs-wmt20.zip}
	unzip optimal-ref-translation-en-cs-wmt20.zip -d data
# get machine translations
	tar -xf newstest2020sgm-v2.tar.gz
	./scripts/article_names.py
	./scripts/extract_transl.py sgm/system-outputs/en-cs/newstest2020.en-cs.CUNI-DocTransformer.1450.sgm 
	mv data/CUNI-DocTransformer.txt data/translation-MT1.txt
	./scripts/extract_transl.py sgm/system-outputs/en-cs/newstest2020.en-cs.Online-B.1589.sgm
	mv data/Online-B.txt data/translation-MT2.txt
# split to train and test
	mkdir data/train data/test
	./scripts/split_all.sh 6
# create English.txt (3*source), ORT.txt (3*N1), SRT (P1,P2,P3)
	./scripts/paste_data_sets.py data/train/english.txt data/train/N1.txt data/train/P1.txt data/train/P2.txt data/train/P3.txt
# create output file for results
	mkdir source/results
	mkdir sorce/for_graphs

extract_lm:
	unzip source/resources/models.zip -d source/resources

train_lm: kenlm preprocess
	mkdir arpas;	\
	kenlm/build/bin/lmplz -o 1 -S 50% -T /tmp <data/lm/news19_tl.txt >arpas/news19_1gram.arpa;	\
	kenlm/build/bin/build_binary arpas/news19_1gram.arpa source/resources/news19_1gram.binary;	\
	kenlm/build/bin/lmplz -o 2 -S 50% -T /tmp <data/lm/news19_tl.txt >arpas/news19_2gram.arpa;	\
	kenlm/build/bin/build_binary arpas/news19_2gram.arpa source/resources/news19_2gram.binary;	\
	kenlm/build/bin/lmplz -o 3 -S 50% -T /tmp <data/lm/news19_tl.txt >arpas/news19_3gram.arpa;	\
	kenlm/build/bin/build_binary arpas/news19_3gram.arpa source/resources/news19_3gram.binary;	\
	kenlm/build/bin/lmplz -o 4 -S 50% -T /tmp <data/lm/news19_tl.txt >arpas/news19_4gram.arpa;	\
	kenlm/build/bin/build_binary arpas/news19_4gram.arpa source/resources/news19_4gram.binary;	\
	rm -rf ./arpas

preprocess: lm_data
#NOTE: need to do the preprocessing in loop for files of size 500 000, otherwise it fails on memory
	n=17; \
	while [[ $${n} -gt 0 ]] ; do \
		head -n 500000 data/lm/news19_rest.txt > data/lm/news19_1.txt; \
		./scripts/train_preprocess.py data/lm/news19_rest.txt data/lm/news19_tl.txt ; \
		tail -n +500001 data/lm/news19_rest.txt > data/lm/news19_rest1.txt ; \
		mv data/lm/news19_rest1.txt data/lm/news19_rest.txt ; \
		((n = n - 1)) || true; \
	done; \
	./scripts/train_preprocess.py data/lm/news19_rest.txt data/lm/news19_tl.txt
	
#cat data/lm/news19.txt | udapy read.Sentences udpipe.Cs online=0 tokenize=1 tag=0 parse=0 >data/lm/news19_tokenized.txt

lm_data:
	mkdir data/lm
	wget -O -  https://data.statmt.org/news-crawl/cs/news.2019.cs.shuffled.deduped.gz | gzip -d > data/lm/news19_rest.txt

kenlm: kenlm_deps
	wget -O - https://kheafield.com/code/kenlm.tar.gz | tar xz;	\
	cd kenlm;	\
	mkdir -p build;	\
	cd build;	\
	cmake ..;	\
	make -j2

kenlm_deps:
	sudo pacman -S boost zlib cmake

clean:
	rm -rf ./data
	rm -rf ./bc_venv
	rm -rf ./kenlm