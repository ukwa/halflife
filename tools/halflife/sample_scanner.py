from __future__ import print_function
import json, sys, datetime, re, csv, codecs
from pprint import pprint
from checkurl import *


# Input filename template:
file_template = "archive-sample/sample-of-%s/sample-for-%s.csv"
# Output filename template:
output_template = "sample-of-%s-scan-results.csv"

# Loop over all sample sizes and check status:
for size in [100,1000,10000,100000]:
    print("Scanning sample of size %s..." % size)
    with codecs.open( output_template % size, "w", "utf-8") as out_file:
        for y in range(2013,2050):
            try:
                with open( file_template % (size, y) ) as data_file:
                    print("Processing year %s..." % y )
                    reader = csv.reader(data_file, delimiter="\t")
                    for row in reader:
                        timestamp = datetime.datetime.strptime( row[0], "%Y-%m-%dT%H:%M:%SZ" )    
                        url = row[1]
                        title = row[2]
                        text_frag = row[3]
                        ssdeep = row[4]
                        md5 = row[5]


                        state = checkUrl( url )
                        status = state['status']
                        reason = state['reason']
                        key = mapStatusToKey( state )

                        # Also check content, if present:
                        identical = None
                        if state.has_key('md5'):
                            if state['md5'] == md5:
                                identical = True
                            else:
                                identical = False
                        # Similarity tactic:
                        similarity = None
                        if state.has_key('fh'):
                            similarity = fuzzyHashCompare(state['fh'], ssdeep)

                        # Clean up the reason:
                        try:
                            ascii_reason = reason.encode('ascii','replace')
                        except:
                            ascii_reason = "UNKNOWN REASON"         

                        month = timestamp.strftime("%m")
                        quarter = 1 + (int(month)-1)/3          

                        try:
                            print( "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % ( y, quarter, month, key, status, ascii_reason, identical, similarity, url ), file=out_file )
                            out_file.flush()
                        except:
                            print("ERROR", y, url, key, status, ascii_reason)
                            sys.exit(1)
                        out_file.flush()
            except IOError:
                pass
                
    out_file.close()
