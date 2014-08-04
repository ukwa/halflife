from halflife.checkurl import checkUrl

# Some example URLs:
urls = [('http://this-domain-does-not-exist.org/', 'UNRESOLVABLE' ),
        ('http://explorer.bl.uk', 'TIMEOUT' ),
        ('http://example.org/', 'OK' ),
        ('http://example.org:79/', 'NOROUTE' ),
        ('http://httpstat.us/302', 'REDIRECT+OK' ),
        ('http://httpstat.us/404', 'GONE' ),
        ('http://httpstat.us/500', 'ERROR') ]

# Now check these example URLs:
for url,state in urls:
    newstate = checkUrl(url)
    if state == newstate:
        print( "PASS " + url + " " + state )
    else:
        print( "FAIL " + url + " expected " + state + " got " + newstate )
        break
