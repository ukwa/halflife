# Utilities for checking network status
from urlparse import urlparse
from BeautifulSoup import BeautifulSoup, Comment
from pprint import pprint
import httplib, socket, subprocess, re, hashlib

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
        return { "status": 900, "reason": "BAD-URL" }

    o = urlparse(url)
    
    resolvable = isResolvable(o.hostname)
    if not resolvable:
        return { "status": 903, "reason": "UNRESOLVABLE" }

    try: 
        conn = httplib.HTTPConnection(o.netloc, timeout=10)
        conn.request("GET", o.path )
        res = conn.getresponse()
    except socket.timeout:
        return { "status": 924, "reason": "TIMEOUT" }
    except Exception as e:
        if str(e) == "[Errno 65] No route to host":
            return { "status": 903, "reason": "NOROUTE" }
        elif str(e) == "[Errno 51] Network is unreachable":
            return { "status": 903, "reason": "NETWORK-UNREACHABLE" }
        elif str(e) == "[Errno 61] Connection refused" or str(e) == "[Errno 111] Connection refused":
            return { "status": 903, "reason": "CONNECTION-REFUSED" }
        elif str(e) == "[Errno 54] Connection reset by peer":
            return { "status": 903, "reason": "CONNECTION-RESET" }
        else:
            return { "status": 903, "reason": "CONNECTION-FAILED: "+str(e) }
    
    if res.status / 100 == 3:
        state = checkUrl(res.getheader('location'))
        status = state['status']
        reason = state['reason']
        if reason.endswith("VIA-REDIRECT+"):
            return state
        else:
            state['reason'] = reason+" VIA-REDIRECT+" 
            return state
    elif res.status / 100 == 2:
        # Get a copy, hash it, get the title and ssdeep the text
        payload = res.read()
        # Clean up and grab the text:
        title = ""
        text = ""
        first_fragment = ""
        fh = None
        try:
            soup = BeautifulSoup(payload,convertEntities=BeautifulSoup.HTML_ENTITIES)
            if soup.title != None:
                title = soup.title.string
            [ elem.extract() for elem in soup.findAll(['script', 'link', 'style']) ]
            comments = soup.findAll(text=lambda text:isinstance(text, Comment))
            [comment.extract() for comment in comments]
            if soup.body != None:
                texts = [ unicode(x) for x in soup.body(text=True) ]
                text =  soup.title.string + " ".join(texts)
                #text = re.sub(r"\x95","?", text)
                text = re.sub(r"[^\x00-\x7F]+","?", text)
                text = re.sub(r"&amp;","&", text)
                text = re.sub(r"\s+"," ",text)
                #print(text)
            # Just pull out the first bit:
            first_fragment = text[:200]
            # Fuzzy hash
            fh = fuzzyHash(text)
        except:
            pass
        # And the binary hash:
        md5 = hashlib.md5(payload).hexdigest()
        # And return:
        return { "status": res.status, "reason": res.reason, "title": title, "first_fragment": first_fragment, "fh":fh, "md5":md5 }
    else:
        return { "status": res.status, "reason": res.reason }

# This maps the recorded status and reason to out preferred taxonomy:
def mapStatusToKey( state ):
    status = state['status']
    reason = state['reason']
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

def writeFuzzyHashFile(filename, hash, hashname):
    header = "ssdeep,1.1--blocksize:hash:hash,filename"
    f = open(filename,'w')
    f.write("%s\n" % header)
    f.write("%s,\"%s\"\n" % (hash,hashname) )
    f.close()

def fuzzyHashCompare(hash1, hash2):
    writeFuzzyHashFile("fh1",hash1,"fh1")
    writeFuzzyHashFile("fh2",hash2,"fh2")
    p = subprocess.Popen(['ssdeep','-a','-c','-k',"fh1","fh2"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    output,err = p.communicate()
    for line in output.split("\n"):
        if '"fh2","fh1",' in line:
            return line.lstrip('"fh2","fh1",')
    return ""

#
# By using the id_ hack to pass-through the original item (no re-writing):
# http://www.webarchive.org.uk/wayback/archive/20050329120000id_/http://www.royal-navy.mod.uk/static/pages/256577f4.html
def getBinHash(url, wayback_date):
    wb_url = 'http://www.webarchive.org.uk/wayback/archive/%sid_/%s' % (wayback_date,url)
    try:
        resource = urlo.open( wb_url )
        return hashlib.md5(resource.read()).hexdigest()
    except:
        print("ERROR when attempting to get: %s" % wb_url)



