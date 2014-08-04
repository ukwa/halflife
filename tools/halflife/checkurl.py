# Utilities for checking network status
from urlparse import urlparse
import httplib
import socket

def isResolvable(hostname):
    if hostname is None:
        return False
    try:
        host = socket.gethostbyname(hostname)
        return True
    except socket.gaierror:
        return False

def checkUrl(url):
    if url is None or url == "":
        return (900, "BAD-URL")

    o = urlparse(url)
    
    resolvable = isResolvable(o.hostname)
    if not resolvable:
        return (903, "UNRESOLVABLE")

    try: 
        conn = httplib.HTTPConnection(o.netloc, timeout=10)
        conn.request("GET", o.path )
        res = conn.getresponse()
    except socket.timeout:
        return (924, "TIMEOUT")
    except Exception as e:
        if str(e) == "[Errno 65] No route to host":
            return (903, "NOROUTE")
        elif str(e) == "[Errno 51] Network is unreachable":
            return (903, "NETWORK-UNREACHABLE")
        elif str(e) == "[Errno 61] Connection refused" or str(e) == "[Errno 111] Connection refused":
            return (903, "CONNECTION-REFUSED" )
        elif str(e) == "[Errno 54] Connection reset by peer":
            return (903, "CONNECTION-RESET" )
        else:
            return (903, "CONNECTION-FAILED: "+str(e))
    
    if res.status / 100 == 3:
        status, reason = checkUrl(res.getheader('location'))
        if reason.endswith("VIA-REDIRECT+"):
            return ( status, reason )
        else:
            return ( status, reason+" VIA-REDIRECT+" )
    else:
        return ( res.status, res.reason )

