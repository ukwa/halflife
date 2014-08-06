import csv, sys, pprint
import collections

filename =  sys.argv[1]
counts = collections.defaultdict(lambda: collections.defaultdict(int))
with open(filename, 'rb') as f:
    reader = csv.reader(f, delimiter="\t")
    for row in reader:
        key = row[0]+"-"+row[1]
        counts[key]["TOTAL"] += 1
        counts[key][row[3]] += 1
        identical = row[6]
        if identical == "True":
            counts[key]["IDENTICAL"] += 1
        similarity = row[7]
        if similarity != "None" and similarity != "":
            if int(similarity) > 20:
                counts[key]["SIMILAR"] += 1
            else:
                counts[key]["DISSIMILAR"] += 1

# Create the header line
print("\t".join(['Year', 'GONE', 'ERROR', 'MISSING','MOVED','OK', 'SAME','SIMILAR','DISSIM','TOTAL']))
for year in sorted(counts.keys()):
    # Now build up data
    line = year
    for state in ['GONE', 'ERROR', 'MISSING','MOVED','OK','IDENTICAL','SIMILAR','DISSIMILAR','TOTAL']:
        line = line + "\t" + str(counts[year][state])
    print(line)

