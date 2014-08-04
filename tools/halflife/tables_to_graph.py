import csv, sys, pprint
import collections

filename = 'halflife/sample-v2-3.tsv'
counts = collections.defaultdict(lambda: collections.defaultdict(int))
with open(filename, 'rb') as f:
    reader = csv.reader(f, delimiter="\t")
    for row in reader:
        #print row
        counts[row[0]][row[3]] += 1

# Create the header line
print("\t".join(['Year', 'GONE', 'ERROR', 'MISSING','MOVED','OK']))
for year in sorted(counts.keys()):
    # Now build up data
    line = year
    for state in ['GONE', 'ERROR', 'MISSING','MOVED','OK']:
        line = line + "\t" + str(counts[year][state])
    print(line)

