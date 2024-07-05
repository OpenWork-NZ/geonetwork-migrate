#! /usr/bin/python3
import requests, json
from sys import argv

host = argv[1] if len(argv) > 1 else "https://localhost:8080/"
if not host.endswith("/geonetwork") and not host.endswith("/geonetwork/"):
    if host[-1] == "/": host = host[:-1]
    host += "/geonetwork/"
if host[-1] != "/": host += "/"

auth = (argv[2], argv[3]) if len(argv) > 3 else ("admin", "admin")

with requests.Session() as s:
    s.headers["Accept"] = "application/json"
    s.get(host + "srv/api/me", auth=auth).raise_for_status()
    #s.headers["X-XSRF-TOKEN"] = s.cookies["XSRF-TOKEN"]
    res = s.get(host + "srv/api/groups", auth=auth)
    res.raise_for_status()
    groups = res.json()
    for group in groups:
        with open(group["logo"], "wb") as f:
            res = s.get(host + "srv/api/groups/" + str(group["id"]) + "/logo", auth=auth, stream = True)
            res.raise_for_status()
            for chunk in res.iter_content(512):
                f.write(chunk)

    res = s.get(host + "srv/api/users/groups", auth=auth)
    res.raise_for_status()
    usergroups = res.json()

    res = s.get(host + "srv/api/users", auth=auth)
    res.raise_for_status()
    users = res.json()

with open("dump.json", "w") as f:
    json.dump({"groups": groups, "usergroups": usergroups, "users": users}, f)
