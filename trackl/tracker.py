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
import subprocess
import os
import re
import time
import threading
from guessit import guessit #Remember to use the json kind
from trackl import apiconnect
import notify2 as notify
notify.init("trackl")

#logging.basicConfig(filename="logs/{}.log".format(int(time.time())), level=logging.DEBUG)

def get_sec(time_str):
    h, m, s = time_str.split(':')
    s, cs = s.split(".")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(cs)/100

class Tracker():
    def __init__(self, player="mpv", percentage=70, wait_s=20):
        self.process_name = "simkl-pytracker-{}".format(player)
        self.wait_s = wait_s
        self.wait_close = 100
        self.player = player
        self.trackingfile = None
        self.percentage = percentage
        tracker_args = 0
        tracker_t = threading.Thread(target=self._tracker)#, args=tracker_args)
        tracker_t.name = self.process_name
        tracker_t.daemon = True

        self.active = True
        tracker_t.start()
        tracker_t.join()

    def _get_playing_file_lsof(self, player):
        try:
            lsof = subprocess.Popen(['lsof', '+w', '-n', '-c', ''.join(
                ['/', player, '/']), '-Fn'], stdout=subprocess.PIPE)
        except OSError:
            return False

        output = lsof.communicate()[0].decode('utf-8')
        fileregex = re.compile("n(.*(\.mkv|\.mp4|\.avi))")

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
        self.active = False

    def _tracker(self):
        subprocess.Popen(['notify-send', "Starting daemon"])
        while self.active:
            filename = self._get_playing_file_lsof(self.player)
            print(filename)
            if filename != False:
                if self.trackingfile == None:
                    #[FILENAME, startime, exptime]
                    self.trackingfile = filename
                    g = guessit(filename["abspath"])
                    txt = g["title"]
                    if g["type"] == "episode":
                        txt += "\nS{}E{}".format(str(g["season"]).zfill(2),
                             str(g["episode"]).zfill(2))
                    subprocess.Popen(['notify-send', "-i", "tmp.png", txt])
                    self.trackingfile["scrobbled"] = False
                else:
                    pct = ( time.time() - self.trackingfile["added"] ) \
                    /self.trackingfile["videolen"] * 100
                    print("Percentage: {}%".format(round(pct,3)))
                    print("Time played:", time.strftime("%H:%M:%S", 
                        time.gmtime(time.time() - self.trackingfile["added"])))

                    if pct >= self.percentage and not self.trackingfile["scrobbled"]:
                        show = guessit(self.trackingfile["abspath"], "--json")

                        print("Title:", show["title"])
                        txt = "Title: " + show["title"] + "\n"
                        if show["type"] == "episode":
                            txt += " S{}E{}".format(str(show["season"]).zfill(2),
                             str(show["episode"]).zfill(2))

                        apiconnect.scrobble_show( self.trackingfile["abspath"] )
                        n = notify.Notification(txt, icon="trackl/resources/logo_simkl_black_with_white_bg.png")
                        n.show()
                        self.trackingfile["scrobbled"] = True
                    elif self.trackingfile["scrobbled"]:
                        pass
                    
            else:
                self.trackingfile = None

            try:
                time.sleep(self.wait_s)
            except KeyboardInterrupt:
                logging.info("Daemon stop")
                print("Daemon stopped")

    def _getvideolen(self, filename):
        res = subprocess.Popen(["ffprobe", filename],
            stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        ret = [x.decode("utf-8") for x in res.stdout.readlines()
         if "Duration" in x.decode("utf-8")][0].strip(" ").split(",")[0][10:]

        return ret

#Example
#tr = Tracker("mpv", 70, 10)