import subprocess
import os
import re
import time
import threading
from guessit import guessit #Remember to use the json kind

def get_sec(time_str):
    h, m, s = time_str.split(':')
    s, cs = s.split(".")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(cs)/100

class Tracker():
    def __init__(self, player="mpv", percentage=70, wait_s=20):
        self.process_name = "simkl-pytracker"
        self.wait_s = wait_s
        self.wait_close = 100
        self.player = player
        self.trackingfile = None
        self.percentage = percentage
        tracker_args = 0
        tracker_t = threading.Thread(target=self._tracker)#, args=tracker_args)
        tracker_t.daemon = True

        self.active = True
        tracker_t.start()

    def _get_playing_file_lsof(self, player):
        try:
            lsof = subprocess.Popen(['lsof', '+w', '-n', '-c', ''.join(
                ['/', player, '/']), '-Fn'], stdout=subprocess.PIPE)
        except OSError:
            return False

        output = lsof.communicate()[0].decode('utf-8')
        fileregex = re.compile("n(.*(\.mkv|\.mp4|\.avi))")
        filedir = re.compile("n(/.*(\.mkv|\.mp4|\.avi))")

        for line in output.splitlines():
            match = fileregex.match(line)
            if match is not None:
                trcfile = dict()
                trcfile["abspath"] = os.path.abspath(match.group(1))
                trcfile["videolen"] = get_sec(self._getvideolen(trcfile["abspath"]))
                trcfile["filename"] = os.path.basename(match.group(1))
                trcfile["added"]    = time.time()
                print("Path:", trcfile["abspath"])
                print("Video len:", self._getvideolen(trcfile["abspath"]))
                return trcfile

        return False

    def enable(self):
        self.active = True
    def disable(self):
        self.disable = False

    def _tracker(self):
        while self.active:
            filename = self._get_playing_file_lsof(self.player)
            if filename != False:
                if self.trackingfile == None:
                    #[FILENAME, startime, exptime]
                    self.trackingfile = filename
                else:
                    pct = ( time.time() - self.trackingfile["added"] ) \
                    /self.trackingfile["videolen"] * 100
                    print("Percentage: {}%".format(round(pct,3)))
                    print("Time played:", time.strftime("%H:%M:%S", 
                        time.gmtime(time.time() - self.trackingfile["added"])))

                    if pct >= self.percentage:
                        show = guessit(self.trackingfile["abspath"], "--json")

                        print("Title:", show["title"])
                        if show["type"] == "episode":
                            print("ExS:", "{}x{}".format(show["season"], show["episode"]))
                    
            else:
                self.trackingfile = None

            time.sleep(self.wait_s)

    def _getvideolen(self, filename):
        res = subprocess.Popen(["ffprobe", filename],
            stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        ret = [x.decode("utf-8") for x in res.stdout.readlines()
         if "Duration" in x.decode("utf-8")][0].strip(" ").split(",")[0][10:]

        return ret

#Example
tr = Tracker("mpv", 70, 10)