#!/usr/bin/env python3
import sys
import udapi

def main(inp_file, out_file):
    # open as udapi document
    doc = udapi.Document(inp_file)
    print("Document loaded")
    # for tree in doc.trees:
    #     print(tree)
    # quit()
    # create tokenizer
    udpipe = udapi.create_block("udpipe.Cs", online=0, tokenize=1, tag=0, parse=0)
    # tokenize
    udpipe.process_document(doc)
    print("Tokenization complete")

    # write to output file
    with open(out_file, "a") as o:
        for tree in doc.trees:
            tokenized_sent = " ".join([node.form.lower() for node in tree.descendants])
            print(tokenized_sent, file=o)

    return

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])