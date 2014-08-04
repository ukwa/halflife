from __future__ import print_function
import json, sys, datetime, re,subprocess
from pprint import pprint
from checkurl import checkUrl

# This maps the recorded status and reason to out preferred taxonomy:
def mapStatusToKey( status, reason ):
    if status / 100 == 2:
        if reason.endswith("VIA-REDIRECT+"):
            return "MOVED"
        else:
            return "OK"
    elif status / 100 == 3:
        return "REDIRECT"
    elif status / 100 == 4:
        return "MISSING"
    elif status / 100 == 5:
        return "ERROR"
    elif status / 100 == 9:
        return "GONE"
    else:
        return "UNKNOWN"

def fuzzyHash(text):
    # Pass through ssdeep:
    p = subprocess.Popen(['ssdeep'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    output,err = p.communicate(text.encode('utf-8','replace'))
    for line in output.split("\n"):
        if ',"stdin"' in line:
            return line.rstrip(',"stdin"')
    return ""


# Input filename template:
file_template = "2014-08-04-OUKWA-Sample/sample-of-%s-for-%s.json"
# Output filename template:
output_template = "sample-of-%s-scan-results.tsv"

# Loop over all sample sizes and check status:
for size in [100,1000,10000,100000]:
    print("Scanning sample of size %s..." % size)
    with open( output_template % size, "w") as out_file:
        for y in range(2000,2050):
            try:
                with open( file_template % (size, y) ) as data_file:
                    print("Processing year %s..." % y )
                    data = json.load(data_file)
                    for doc in data['response']['docs']:
                        url = doc['wct_url']

                        # Normalise whitespace:
                        text = re.sub(r"\s+"," ",doc['text'][0])
                        first_fragment = text[:200]
                        fh = fuzzyHash(text)
                        print('"'+first_fragment+'"', fh)

                        timestamp = datetime.datetime.strptime( doc['timestamp'], "%Y-%m-%dT%H:%M:%SZ" )    

                        status, reason = checkUrl( url )
                        key = mapStatusToKey(status, reason )           

                        try:
                            ascii_reason = reason.encode('ascii','replace')
                        except:
                            ascii_reason = "UNKNOWN REASON"         

                        month = timestamp.strftime("%m")
                        quarter = 1 + (int(month)-1)/3          

                        try:
                            print( "%s\t%s\t%s\t%s\t%s\t%s\t%s" % ( y, quarter, month, key, status, ascii_reason, url ), file=out_file )
                        except:
                            print("ERROR", y, url, key, status, ascii_reason)
                            sys.exit(1)
                        out_file.flush()
            except IOError:
                pass
                
    out_file.close()
