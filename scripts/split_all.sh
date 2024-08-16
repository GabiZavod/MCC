#!/bin/bash

for FILE in data/*.txt; do
    ./scripts/split_train-test.sh "$FILE" "$1"
done