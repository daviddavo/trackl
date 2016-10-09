import subprocess
import os
import re
import time
import threading
import argparse
from guessit import guessit #Remember to use the json kind

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
        import logging
        logging.basicConfig(filename="logs/{}.log".format(int(time.time())),
         level=logging.DEBUG)
        logging.info("Daemon started @ {}".format(time.time()))
        while self.active:
            filename = self._get_playing_file_lsof(self.player)
            print(filename)
            logging.info(str(filename))
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
                else:
                    pct = ( time.time() - self.trackingfile["added"] ) \
                    /self.trackingfile["videolen"] * 100
                    print("Percentage: {}%".format(round(pct,3)))
                    print("Time played:", time.strftime("%H:%M:%S", 
                        time.gmtime(time.time() - self.trackingfile["added"])))

                    if pct >= self.percentage:
                        show = guessit(self.trackingfile["abspath"], "--json")

                        print("Title:", show["title"])
                        txt = "Title: " + show["title"] + "\n"
                        if show["type"] == "episode":
                            txt += " S{}E{}".format(str(show["season"]).zfill(2),
                             str(show["episode"]).zfill(2))
                            subprocess.Popen(['notify-send', filename])
                    
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

parser = argparse.ArgumentParser(description="Scrobble to simkl")
parser.add_argument("file", metavar="file", nargs="?", type=str, 
    help="Filename to scrobble.", default="None")
parser.add_argument("--daemon", action="store_true", 
    help="If you want to autoscrobble on the background")
args = parser.parse_args()

if args.file != "None":
    print("File:",args.file)
    pth = os.path.abspath(args.file)
    show = guessit(pth)

    txt = "Scrobbling {}: {}".format(show["type"], show["title"])
    if show["type"] == "episode":
        txt += " S{}E{}".format(str(show["season"]).zfill(2), 
            str(show["episode"]).zfill(2))    
    print(txt)
else:
    if args.daemon:
        print("Starting daemon")
        tr = Tracker("mpv", 10, 10)
    else:
        parser.print_help()

#Example
#tr = Tracker("mpv", 70, 10)