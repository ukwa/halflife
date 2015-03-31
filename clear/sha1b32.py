import sys
import base64
import hashlib

with open(sys.argv[1], "rb") as i:
    b32 = base64.b32encode(hashlib.sha1(i.read()).digest())

print b32, sys.argv[1]

