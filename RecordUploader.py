import httplib
import glob
import time
import zipfile
import hashlib
import random
import ConfigParser
import base64
import os
from MultiPartForm import *  


config = ConfigParser.RawConfigParser()
config.read('uploader.cfg')

targetURL = config.get('receiver', 'targeturl')
encryptKey = config.get('receiver', 'key')

imageList = glob.glob("./[0-9]*.jpg")
if len(imageList) > 0:
    zipFileName = time.strftime('%Y%m%d%H%M%S')+'.zp'
    zipFile = zipfile.ZipFile(zipFileName,'w',zipfile.ZIP_DEFLATED)
    for imageFile in imageList:
        zipFile.write(imageFile)
    zipFile.close()
    for imageFile in imageList:
        os.remove(imageFile)
    #generateparams
    m = hashlib.sha1()
    fd = open(zipFileName, 'rb')
    m.update(fd.read())
    fd.close()

    fileDigest = m.hexdigest()
    random = random.randint(1,100000000)
    timeStamp = int(round(time.time() * 1000))
    key = encryptKey

    m = hashlib.sha256()
    headerInfo = ':'.join([key,fileDigest,str(timeStamp),str(random)])
    m.update(headerInfo)
    requestDegist = base64.b64encode(m.digest())

    # print headerInfo+':'+requestDegist
    # send
    form = MultiPartForm()
    fd = open(zipFileName, 'rb')
    form.add_file('pkg', zipFileName, fileHandle=fd)
    fd.close()

    body = str(form)
    h = httplib.HTTPConnection(targetURL)
    headers = {"Content-type": form.get_content_type(),
                "time": timeStamp,
                "sha1": fileDigest,
                "random": random,
                "Content-length":len(body),
                "hash": requestDegist}
    h.connect()
    resp = h.request('POST', '/receive', body, headers)
    if h.getresponse().status==200:
        os.remove(zipFileName)
    h.close()


