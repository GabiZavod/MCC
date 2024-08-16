#!/bin/bash

# Check if input file is provided
if [ $# -lt 2 ]; then
    echo "Usage: $0 <input_file> <test_num>"
    exit 1
fi

input_file="$1"
test_num="$2"

# Check if input file exists
if [ ! -f "$input_file" ]; then
    echo "Input file '$input_file' not found."
    exit 1
fi

# Create temporary directory
temp_dir=$(mktemp -d)

# Use awk to separate file on empty lines
awk -v RS= '{ print > "'"$temp_dir"'/part_" NR ".txt" }' "$input_file"

# Get total number of parts
total_parts=$(find "$temp_dir" -type f | wc -l)

# Check if there are enough parts to separate
if [ "$total_parts" -lt $((test_num+1)) ]; then
    echo "Not enough parts to separate."
    exit 1
fi

# Get the last test_num parts
last_six=$(seq "$((total_parts - $((test_num-1))))" "$total_parts")
rest=$(seq "$((total_parts - $((test_num))))")

# Create a file for the last test_num parts
test_file="data/test/$(echo "$input_file" | cut -d "-" -f 2)"
touch "$test_file"

# Concatenate the last test_num parts into one file
for part_num in $last_six; do
    cat "$temp_dir/part_$part_num.txt" >> "$test_file"
    echo '' >> "$test_file"
done

# Create a file for the other parts
train_file="data/train/$(echo "$input_file" | cut -d "-" -f 2)"
touch "$train_file"

# Concatenate the other parts into one file
for part_num in $rest; do
    cat "$temp_dir/part_$part_num.txt" >> "$train_file"
    echo '' >> "$train_file"
done

# Clean up temporary directory
rm -r "$temp_dir"

echo "Separation complete."