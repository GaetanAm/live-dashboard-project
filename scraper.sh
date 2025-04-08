#!/bin/bash

timestamp=$(date '+%Y-%m-%d %H:%M:%S')
html=$(curl -s -A "Mozilla/5.0" "https://www.investing.com/indices/us-30")

value=$(echo "$html" | grep -oP 'data-test="instrument-price-last">[\d,]+' | grep -oP '[\d,]+' | head -1 | tr -d ',')

echo "$timestamp,$value" >> data.csv
