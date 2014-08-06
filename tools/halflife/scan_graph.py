import csv, sys, pprint
import collections

filename =  sys.argv[1]
counts = collections.defaultdict(lambda: collections.defaultdict(int))
with open(filename, 'rb') as f:
    reader = csv.reader(f, delimiter="\t")
    for row in reader:
        counts[row[0]]["TOTAL"] += 1
        counts[row[0]][row[3]] += 1
        identical = row[6]
        if identical == "True":
            counts[row[0]]["IDENTICAL"] += 1
        similarity = row[7]
        if similarity != "None" and similarity != "" and int(similarity) > 20:
            counts[row[0]]["SIMILAR"] += 1


# Create the header line
print("\t".join(['Year', 'GONE', 'ERROR', 'MISSING','MOVED','OK', 'IDENTICAL','SIMILAR','TOTAL']))
for year in sorted(counts.keys()):
    # Now build up data
    line = year
    for state in ['GONE', 'ERROR', 'MISSING','MOVED','OK','IDENTICAL','SIMILAR','TOTAL']:
        line = line + "\t" + str(counts[year][state])
    print(line)

