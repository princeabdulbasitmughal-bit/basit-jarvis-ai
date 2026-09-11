import sys
with open('public/index.html', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'engine-panels' in line:
            print(i+1, line.strip())
