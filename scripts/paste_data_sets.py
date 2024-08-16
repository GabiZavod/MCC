#!/usr/bin/env python3
import sys

def main(eng, ort, srts):
    with open("./data/train/English.txt", "w") as eng_out:
        with open(eng, "r") as inp_eng:
            eng_lines = inp_eng.readlines()
        for i in range(3):
            for line in eng_lines:
                if line[0] == "#":
                    line = line[:-1]
                    line += str(i)
                    print(line, file=eng_out)
                else:
                    print(line, file=eng_out, end="")
    
    with open("./data/train/ORT.txt", "w") as ort_out:
        with open(ort, "r") as inp_ort:
            ort_lines = inp_ort.readlines()
        for i in range(3):
            for line in ort_lines:
                if line[0] == "#":
                    line = line[:-1]
                    line += str(i)
                    print(line, file=ort_out)
                else:
                    print(line, file=ort_out, end="")
        
    with open("./data/train/SRT.txt", "w") as srt_out:
        for i in range(len(srts)):
            with open(srts[i], "r") as srt_inp:
                srt_lines = srt_inp.readlines()
                for srt_line in srt_lines:
                    if srt_line[0] == "#":
                        srt_line = srt_line[:-1]
                        srt_line += str(i) + "\n"
                    print(srt_line, file=srt_out, end="")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])