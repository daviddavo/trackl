import time
import http.client
import json

with open(".api", "r") as a:
    apikey = a.readline().strip("\n").strip(" ") #Also called client_id
    secret = a.readline().strip("\n").strip(" ")
    print("Apikey: ", apikey)
    print("Secret: ", secret)
atoken = None

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
    print(r)
    print(r.status, r.reason)
    print(r.read())

    conn.close()

def login():
    global atoken
    
    t = "/oauth/pin?client_id="
    t += apikey + "&redirect=" + redirect_uri
    log = http.client.HTTPSConnection("api.simkl.com")
    log.request("GET", t, headers=headers)
    r = log.getresponse()
    print(r.status, r.reason)
    rdic = json.loads(r.read().decode("utf-8"))

    print(rdic)
    print("Now you need to connect the app with your account")
    print("Enter the following url: {}".format(rdic["verification_url"]))
    ucode = rdic["user_code"]
    print("And enter this code: {}".format(ucode))

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
                atoken = r["access_token"]
                running = False
                print(atoken)

    log.close()

login()