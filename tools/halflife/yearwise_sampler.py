from __future__ import print_function
import json, sys, codecs, hashlib, csv
import urllib, datetime, re
from pprint import pprint
from checkurl import *
from unicsv import *

#
#urlo = urllib.FancyURLopener({"http":"http://explorer.bl.uk:3127"})
#
urlo=urllib.URLopener()

# Solr endpoint to use:

#solr_endpoint = "http://chrome.bl.uk:8080/solr/select/"
#date_field = "timestamp"
#url_field = "wct_url"
#wayback_date_field = "wct_wayback_date"
#text_field="text"?
#prefix="open"

#solr_endpoint = "http://192.168.45.17:8983/solr/ldwa/select"
solr_endpoint = "http://192.168.1.65:8983/solr/ldwa/select"
date_field = "crawl_date"
url_field = "url"
wayback_date_field = "wayback_date"
text_field="content"
prefix="ldwa"+datetime.datetime.now().strftime(".%Y.%m")

# First, get the number of years for which we have data:
# this works by asking for a fifty year date range form 2000-2050, faceting by year, and only returning years that have results:
yq = solr_endpoint+"?q=*:*&rows=0&wt=json&indent=true&facet=true&facet.mincount=1&facet.date="+date_field+"&facet.date.gap=%2B1YEAR&facet.date.start=2000-01-01T00:00:00Z&facet.date.end=2050-01-01T00:00:00Z"
print(yq)
urlo.retrieve(yq , "total-urls-per-year.json")
# Now parse out the years:
years = list()
with open( "total-urls-per-year.json" ) as data_file:    
    data = json.load(data_file)
    for item in data['facet_counts']['facet_dates'][date_field]:
        count = data['facet_counts']['facet_dates'][date_field][item]
        if item == "gap" or item == "start" or item == "end" or count == 0:
            continue
        timestamp = datetime.datetime.strptime( item, "%Y-%m-%dT%H:%M:%SZ" )
        years.append(timestamp.year)

# Sort them
years = sorted(years)

print("Scanning years",years)

output_template = "sample-of-%s/%s-sample-for-%s.csv"
json_template = "sample-of-%s/%s-sample-for-%s.json"

# Now use the sort=random_{SEED} parameter to generate random samples.
# This passes the 'size' field as the seed, so each list should always come out the same.
q = solr_endpoint+"?q=*:*&rows=%s&sort=random_%s desc&wt=json&indent=true&fq="+date_field+":[%s-01-01T00:00:00Z TO %s-01-01T00:00:00Z%%2B1YEAR]&fl="+url_field+","+wayback_date_field+","+date_field+",title,"+text_field
# Loop over samples:
for size in [2000]:#[100,1000]: #,10000,100000]:
    for y in years:
        with codecs.open( output_template % (size,prefix,y), "w", "utf-8") as out_file:
            # Set up the CSV writer:
            writer = UnicodeWriter(out_file)
            # Do the work:
            url = q % (size,size,y,y)
            output = json_template % (size,prefix,y)
            urlo.retrieve(url , output)

            # Now open up the JSON and process it:
            with open( output ) as data_file:
                print("Processing year %s, sample size %s..." % ( y, size ) )
                data = json.load(data_file) 

                for doc in data['response']['docs']:
                    item_url = doc[url_field]
                    wct_wayback_date = doc[wayback_date_field]

                    bin_hash = getBinHash(item_url, wct_wayback_date)

                    # Normalise the title
                    title = ''
                    if doc.has_key('title'):
                        title = normaliseText(doc['title'])

                    # Normalise the text
                    text = ''
                    if doc.has_key(text_field):
                        text = normaliseText(doc[text_field][0])

                    first_fragment = text[:200]
                    fh = fuzzyHash(text)

                    #print( '"%s"\t"%s"\t"%s"\t"%s"\t"%s"\t"%s"' % ( doc[date_field], item_url, title, first_fragment, fh, bin_hash ), file=out_file ) 
                    writer.writerow( [ doc[date_field], item_url, title, first_fragment, fh, bin_hash ] ) 

            data_file.close()
