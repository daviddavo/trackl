import http.client

#Client ID: IMPORTANT MAKE IT VARIABLE:

with open(".api", "r") as a:
    apikey = a.readline().strip("\n").strip(" ")
    secret = a.readline().strip("\n").strip(" ")
    print("Apikey: ", apikey)
    print("Secret: ", secret)

redirect_uri = "http://simkl.com"
headers = {"Content-Type": "application/json", 
        "simkl-api-key": apikey}

def scrobble_movie(movie_name):
    pass

def scrobble_show(show_name, season, episode):
    pass

def test():
    conn = http.client.HTTPSConnection("api.simkl.com") #MR ROBOT: 452264
    conn.request("GET", "/sync/collection", headers=headers)
    r = conn.getresponse() #302 = Found
    print(r)
    print(r.status, r.reason)
    print(r.read())

    conn.close()

def login():
    import oauth2 as oauth
    
    t = "/oauth/authorize?response_type=code&client_id="
    t += apikey + "&redirect_uri=" + redirect_uri
    log = http.client.HTTPSConnection("simkl.com")
    log.request("GET", t, headers=headers)
    r = log.getresponse()
    print(r.status, r.reason)
    print(r.read())

    log.close()

login()