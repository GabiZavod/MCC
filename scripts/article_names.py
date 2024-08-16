#!/usr/bin/env python3


def main():
    articles = []
    f = open("./data/source-english.txt", "r")
    for line in f.readlines():
        if line[0] == "#":
            article_name = line.split()[1]
            articles.append(article_name + "\n")

    f.close()

    with open("article_names.txt", "w") as a:
        a.writelines(articles)

if __name__ == '__main__':
    main()