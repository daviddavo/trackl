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

#Remember to use python -m

import argparse
import os, sys
import guessit, logging
from termcolor import colored

from trackl import tracker
from trackl import apiconnect

trackl_configdir = os.path.expanduser("~/.config/trackl")
logging.basicConfig(filename=trackl_configdir + "/log.log", level=logging.DEBUG)
logging.debug("cli loaded")

def main():
    parser = argparse.ArgumentParser(description="Scrobble to simkl")
    parser.add_argument("file", metavar="file", nargs="?", type=str, 
        help="Filename to scrobble.", default="None")
    parser.add_argument("--daemon", action="store_true", 
        help="If you want to autoscrobble on the background")
    parser.add_argument("--login", action="store_true",
        help="Delete previous login or create a new one")
    args = parser.parse_args()

    if args.login:
        if apiconnect.login() != False:
            print(apiconnect.prompt)
        else:
            print("Login failed")
        sys.exit()

    if args.file != "None":
        if apiconnect.logged() != False:
            print(colored(apiconnect.prompt.split(", ")[0], 'cyan'),
                colored(apiconnect.prompt.split(", ")[1], 'blue'))
            print("File:",args.file)
            pth = os.path.abspath(args.file)

            r = apiconnect.scrobble_from_filename(pth)
            #print(r)
            if r == False:
                txt = "Error at scrobble"
            else:
                if r["type"] == "episode":
                    txt = "Scrobbling episode: {}".format(r["show"]["title"])
                    txt += " S{}E{}".format(str(r["episode"]["season"]).zfill(2), 
                        str(r["episode"]["episode"]).zfill(2))
                elif r["type"] == "movie":
                    txt = "Not yet"  
            print(txt)

        else:
            print("First you need to log in, use --login")
    else:
        if args.daemon:
            print("Starting daemon")
            tr = tracker.Tracker("mpv", 60, 6)
        else:
            parser.print_help()

if __name__ == "__main__":
    main()