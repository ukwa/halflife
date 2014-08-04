import json, sys
import urllib, datetime
from pprint import pprint

urlo=urllib.URLopener()

# First, get the number of years for which we have data:
# this works by asking for a fifty year date range form 2000-2050, faceting by year, and only returning years that have results:
yq = "http://chrome.bl.uk:8080/solr/select/?q=*:*&rows=0&wt=json&indent=true&facet=true&facet.mincount=1&facet.date=timestamp&facet.date.gap=%2B1YEAR&facet.date.start=2000-01-01T00:00:00Z&facet.date.end=2050-01-01T00:00:00Z"
urlo.retrieve(yq , "total-urls-per-year.json")
# Now parse out the years:
years = list()
with open( "total-urls-per-year.json" ) as data_file:    
    data = json.load(data_file)
    for item in data['facet_counts']['facet_dates']['timestamp']:
    	if item == "gap" or item == "start" or item == "end":
    		continue
    	timestamp = datetime.datetime.strptime( item, "%Y-%m-%dT%H:%M:%SZ" )
    	years.append(timestamp.year)

# Sort them
years = sorted(years)

# Now use the sort=random_{SEED} parameter to generate random samples:
q = "http://chrome.bl.uk:8080/solr/select/?q=*:*&rows=%s&sort=random_%s desc&wt=json&indent=true&fq=timestamp:[%s-01-01T00:00:00Z TO %s-01-01T00:00:00Z%%2B1YEAR]"
# Use this to limit the amount of data:
limiter="&fl=wct_url,timestamp,title"
# Loop over samples:
for size in [100,1000,10000,100000]:
    for y in years:
	url = q % (size,size,y,y)
	if size == 100000:
		url = url + limiter
	print(url)
	output = "sample-of-%s-for-%s.json" % (size, y)
	urlo.retrieve(url , output)
