import subprocess
import os
import re
import time
import threading

def get_sec(time_str):
    h, m, s = time_str.split(':')
    s, cs = s.split(".")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(cs)/100

class Tracker():
    def __init__(self, player, percentage):
        self.process_name = "simkl-pytracker"
        self.wait_s = 20
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
                abspath = os.path.abspath(match.group(1))
                print("Path:", abspath)
                print("Video len:", self._getvideolen(abspath))
                return os.path.basename(match.group(1)), self._getvideolen(abspath)

        return False, None

    def enable(self):
        self.active = True
    def disable(self):
        self.disable = False

    def _tracker(self):
        while self.active:
            filename, videolen = self._get_playing_file_lsof(self.player)
            if filename != False:
                if self.trackingfile == None:
                    #[FILENAME, startime, exptime]
                    #self.percentage/100
                    duration = get_sec(videolen)
                    self.trackingfile = [filename, time.time(), duration]
                else:
                    pct = ( time.time() - self.trackingfile[1] ) \
                    /self.trackingfile[2] * 100
                    print("Percentage: {}%".format(round(pct,3)))
                    print("Time played:", time.strftime("%H:%M:%S", 
                        time.gmtime(time.time() - self.trackingfile[1])))

                    if pct >= self.percentage:
                        print("SCROBBLE TO SIMKL (pct reached)")
                    elif time.time() - self.trackingfile[1] <= self.trackingfile[2] + self.wait_s:
                        print("SCROBBLE TO SIMKL (time)")

            else:
                self.trackingfile = None

            time.sleep(self.wait_s)

    def _getvideolen(self, filename):
        res = subprocess.Popen(["ffprobe", filename],
            stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        ret = [x.decode("utf-8") for x in res.stdout.readlines()
         if "Duration" in x.decode("utf-8")][0].strip(" ").split(",")[0][10:]

        return ret

tr = Tracker("mpv", 75)