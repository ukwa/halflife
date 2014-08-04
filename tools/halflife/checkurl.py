# Utilities for checking network status
from urlparse import urlparse
import httplib, socket, subprocess


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

