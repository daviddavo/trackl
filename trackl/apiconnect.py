'''
    Trackl: Multiplatform simkl tracker
    Copyright (C) 2016  David Davó   david@ddavo.me

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import time, os
import http.client
import json
import logging
import guessit

path = os.path.dirname(__file__)
username = "NOT LOGGED IN"
prompt = "Hello again, {}"

trackl_configdir = os.path.expanduser("~/.config/trackl")
logging.basicConfig(filename=trackl_configdir + "/log.log", level=logging.DEBUG)
logging.debug("apiconnect loaded")

with open(path + "/.api", "r") as a:
    APIKEY = a.readline().strip("\n").strip(" ") #Also called client_id
    secret = a.readline().strip("\n").strip(" ")

redirect_uri = "http://simkl.com"
headers = {"Content-Type": "application/json",
        "simkl-api-key": APIKEY}

class Engine:
    def __init__(self):
        pass

    def get_watched(self, typestring):
        con = http.client.HTTPSConnection("api.simkl.com")
        headers["authorization"] = logged()
        con.request("GET", "/sync/all-watched/" + typestring, headers=headers)
        r = con.getresponse()
        r = json.loads(r.read().decode("utf-8"))
        return r


def scrobble_from_filename(filename):
    con = http.client.HTTPSConnection("api.simkl.com")
    headers["authorization"] = logged()

    values = {"file":filename}
    values = json.dumps(values)
    con.request("GET", "/search/file/", body=values, headers=headers)
    r = con.getresponse()
    print(r.status, r.reason)
    r = r.read().decode("utf-8")
    r2 = r.split("\n")
    dic = json.loads(r2[len(r2)-1])
    #print(dic)
    tosend = {}
    if dic == []:
        return False
    elif dic["type"] == "episode":
        episode = {}
        tosend["episodes"] = []
        episode["ids"] = dic["episode"]["ids"]
        episode["watched_at"] = time.strftime('%Y-%m-%d %H:%M:%S')

        tosend["episodes"].append(episode)
        #tosend = {"episodes":[{"watched_at":"2016-10-14 16:28:00", "ids":{"hulu":681868}}]}
    elif dic["type"] == "movie":
        movie = {}
        tosend["movies"] = []
        movie["ids"] = dic["movie"]["ids"]
        movie["watched_at"] = time.strftime('%Y-%m-%d %H:%M:%S')
        tosend["movies"].append(movie)

    tosendj = json.dumps(tosend)
    #print(tosendj)
    con.request("POST", "/sync/history/", body=tosendj, headers=headers)
    #print(r.status, r.reason)

    print()
    rdic = json.loads(con.getresponse().read().decode("utf-8"))["not_found"]
    print(rdic)
    for i in rdic:
        if rdic[i] != []:
            return False

    return dic

def login():
    t = "/oauth/pin?client_id="
    t += APIKEY + "&redirect=" + redirect_uri
    log = http.client.HTTPSConnection("api.simkl.com")
    log.request("GET", t, headers=headers)
    r = log.getresponse()
    #print(r.status, r.reason)
    rdic = json.loads(r.read().decode("utf-8"))

    #print(rdic)
    print("Now you need to connect the app with your account")
    ucode = rdic["user_code"]
    print("Enter the following url: {}".format(rdic["verification_url"]
        +"/"+rdic["user_code"]))

    i = 0
    running = True
    while running:
        i += 1
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("Program interrupted")
        if i > rdic["expires_in"]:
            running = False
            print("\nWaiting expired")
        print("Waiting response {}/{} seconds".format(str(i).zfill(3),
            rdic["expires_in"]), end="\r")

        if rdic["expires_in"] % 6 == 0:
            t = "/oauth/pin/" + ucode + "?client_id=" + APIKEY
            log.request("GET", t, headers=headers)
            r = json.loads(log.getresponse().read().decode("utf-8"))
            if r["result"] == "OK":
                print("")
                atoken = r["access_token"]
                running = False

                with open(trackl_configdir + "/token", "w") as f:
                    f.write(atoken)

                header = {"Content-Type": "application/json",
                    "simkl-api-key": APIKEY,
                    "authorization": atoken}
                
                log.request("GET", "/users/settings", headers=header)
                r = log.getresponse()
                #print(r.status, r.reason)
                #print(r.read().decode("utf-8"))
                rdic = json.loads(r.read().decode("utf-8"))
                global prompt
                prompt = "Login succesfull, hello {}".format(rdic["user"]["name"])

                return atoken

    log.close()
    return False

def logged():
    global prompt
    global username
    if os.path.isfile(trackl_configdir + "/token"):
        with open(trackl_configdir + "/token", "r") as f:
            tk = f.readline().strip("\n").strip(" ")
            if "{}" in prompt:
                log = http.client.HTTPSConnection("api.simkl.com")
                header = {"Content-Type": "application/json",
                        "simkl-api-key": APIKEY,
                        "authorization": tk}
                log.request("GET", "/users/settings", headers=header)
                rdic = json.loads(log.getresponse().read().decode("utf-8"))
                username = rdic["user"]["name"]
                prompt = prompt.format(rdic["user"]["name"])
            return tk
    else:
        return False