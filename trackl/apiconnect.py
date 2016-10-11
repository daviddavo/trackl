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

import time
import os
import http.client
import json
path = os.path.dirname(__file__)
prompt = "Hello again, {}"

trackl_configdir = os.path.expanduser("~/.config/trackl")

with open(path + "/.api", "r") as a:
    apikey = a.readline().strip("\n").strip(" ") #Also called client_id
    secret = a.readline().strip("\n").strip(" ")
    #print("Apikey: ", apikey)
    #print("Secret: ", secret)

redirect_uri = "http://simkl.com"
headers = {"Content-Type": "application/json",
        "simkl-api-key": apikey}

def scrobble_movie(movie_name):
    pass

def scrobble_show(show_name, season, episode):
    pass

def test():
    headers = {"Content-Type": "application/json",
    "simkl-api-key": apikey,
    "authorization": atoken}
    conn = http.client.HTTPSConnection("api.simkl.com") #MR ROBOT: 452264
    conn.request("GET", "/sync/collection", headers=headers)
    r = conn.getresponse() #302 = Found
    #print(r.status, r.reason)
    #print(r.read())

    conn.close()

def login():
    t = "/oauth/pin?client_id="
    t += apikey + "&redirect=" + redirect_uri
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
            t = "/oauth/pin/" + ucode + "?client_id=" + apikey
            log.request("GET", t, headers=headers)
            r = json.loads(log.getresponse().read().decode("utf-8"))
            if r["result"] == "OK":
                print("")
                atoken = r["access_token"]
                running = False

                with open(trackl_configdir + "/.token", "w") as f:
                    f.write(atoken)

                header = {"Content-Type": "application/json",
                    "simkl-api-key": apikey,
                    "authorization": atoken}
                
                log.request("GET", "/users/settings", headers=header)
                r = log.getresponse()
                #print(r.status, r.reason)
                #print(r.read().decode("utf-8"))
                rdic = json.loads(r.read().decode("utf-8"))
                print("Login succesfull, hello {}".format(rdic["user"]["name"]))

                return atoken

    log.close()
    return False

def logged():
    global prompt
    if os.path.isfile(trackl_configdir + "/.token"):
        with open(trackl_configdir + "/.token", "r") as f:
            tk = f.readline().strip("\n").strip(" ")
            log = http.client.HTTPSConnection("api.simkl.com")
            header = {"Content-Type": "application/json",
                    "simkl-api-key": apikey,
                    "authorization": tk}
            log.request("GET", "/users/settings", headers=header)
            rdic = json.loads(log.getresponse().read().decode("utf-8"))
            prompt = prompt.format(rdic["user"]["name"])
            return tk
    else:
        return False