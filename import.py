#! /usr/bin/python3
import requests, pprint, json
from sys import argv
import diceware

host = argv[1] if len(argv) > 1 else "http://localhost:8080/"
if not host.endswith("/geonetwork") and not host.endswith("/geonetwork/"):
    if host[-1] == "/": host = host[:-1]
    host += "/geonetwork/"
if host[-1] != "/": host += "/"

auth = (argv[2], argv[3]) if len(argv) > 3 else ("admin", "admin")

with open("dump.json", "r") as f:
    dump = json.load(f)

with requests.Session() as s:
    s.headers["Accept"] = "application/json"
    s.get(host + "srv/api/me", auth=auth).raise_for_status()
    s.headers["X-XSRF-TOKEN"] = s.cookies["XSRF-TOKEN"]

    res = s.get(host + "srv/api/groups", auth=auth)
    res.raise_for_status()
    groups = {group["name"] for group in res.json()}
    res = s.get(host + "srv/api/logos", auth=auth)
    res.raise_for_status()
    logos = set(res.json())
    for group in dump["groups"]:
        logo = group['logo']
        if logo not in logos:
            logos.add(logo)
            s.post(host + 'srv/api/logos', data = {}, auth=auth,
                    files={ 'file': (logo, open(logo, 'rb')) }).raise_for_status()

        group["allowedCategories"] = []
        group["defaultCategory"] = None
        if group["name"] not in groups:
            s.put(host + 'srv/api/groups', auth=auth, json=group).raise_for_status()

    res = s.get(host + "srv/api/groups", auth=auth)
    res.raise_for_status()
    groupsByName = {group["name"]: group["id"] for group in res.json()}

    usersByName = {user["username"]: user for user in dump["users"]}
    for group in dump["usergroups"]:
        username = group["userName"]
        if '(' in username: username = username.split('(')[-1]
        if username[-1] == ')': username = username[:-1]
        user = usersByName.get(username)

        key = "groups" + group["userProfile"]
        if key == "groupsAdministrator": key = "groupsUserAdmin"

        if key not in user: user[key] = []
        if group["groupName"] != "allAdmins":
            groupID = groupsByName[group["groupName"]]
            user[key].append(str(groupID))

    res = s.get(host + "srv/api/users", auth=auth)
    res.raise_for_status()
    users = {user["username"] for user in res.json()}
    print(users)
    for user in dump["users"]:
        password = diceware.get_passphrase(diceware.handle_options(['-d', ' ', '-n', '4']))
        del user["id"]
        del user["lastLoginDate"]
        del user["security"]
        user["password"] = password
        if user["username"] not in users:
            s.put(host + "srv/api/users", auth=auth, json=user).raise_for_status()
        print(user["username"], "\t", password)
