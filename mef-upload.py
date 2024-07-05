#! /usr/bin/python3
import requests
from sys import argv

if len(argv) <= 1:
    print("USAGE: mef-upload.py MEF_FILE [http(s)://domain:port/] [username] [password] [TEMPLATE|METADATA]")
    exit(1)

host = argv[2] if len(argv) > 2 else "https://localhost:8080/"
if not host.endswith("/geonetwork") and not host.endswith("/geonetwork/"):
    if host[-1] == "/": host = host[:-1]
    host += "/geonetwork/"
if host[-1] != "/": host += "/"

auth = (argv[3], argv[4]) if len(argv) > 4 else ("admin", "admin")

if len(argv) > 5: metadataType = argv[5]
else: metadataType = "TEMPLATE"

with requests.Session() as s:
    s.headers["Accept"] = "application/json"
    s.get(host + "srv/api/me", auth=auth).raise_for_status()
    s.headers["X-XSRF-TOKEN"] = s.cookies["XSRF-TOKEN"]

    s.post(host + "srv/api/records", auth=auth, data={
        '_csrf': s.cookies["XSRF-TOKEN"],
        'metadataType': metadataType,
        'uuidProcessing': "OVERWRITE",
        'transformWith': "_none_",
        'assignToCatalog': 'on',
      }, files = {
          'file': open(argv[1], 'rb')
      }).raise_for_status()
