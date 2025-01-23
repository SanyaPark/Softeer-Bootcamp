#!/usr/bin/env python3

import sys
# 출처: curl -o 1984.txt https://gutenberg.net.au/ebooks01/0100021.txt
for line in sys.stdin:
    line = line.strip()
    words = line.split()
    for w in words:
        print(f"{w}\t{1}")
        