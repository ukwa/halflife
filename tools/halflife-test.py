from halflife.checkurl import *

# Some example URLs:
urls = [('http://this-domain-does-not-exist.org/', 'GONE' ),
        ('http://explorer.bl.uk', 'GONE' ),
        ('http://example.org/', 'OK' ),
        ('http://example.org:79/', 'GONE' ),
        ('http://httpstat.us/302', 'MOVED' ),
        ('http://httpstat.us/404', 'MISSING' ),
        ('http://httpstat.us/500', 'ERROR') ]

# Now check these example URLs:
for url,state in urls:
    newstatus, response = checkUrl(url)
    newstate = mapStatusToKey(newstatus, response)
    if state == newstate:
        print( "PASS " + url + " " + state )
    else:
        print( "FAIL " + url + " expected " + state + " got " + newstate )
        break
