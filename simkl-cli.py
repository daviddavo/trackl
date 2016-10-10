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

import argparse
import os, sys
import guessit
from termcolor import colored

import tracker
import apiconnect

parser = argparse.ArgumentParser(description="Scrobble to simkl")
parser.add_argument("file", metavar="file", nargs="?", type=str, 
    help="Filename to scrobble.", default="None")
parser.add_argument("--daemon", action="store_true", 
    help="If you want to autoscrobble on the background")
parser.add_argument("--login", action="store_true",
    help="Delete previous login or create a new one")
args = parser.parse_args()

if args.login:
    apiconnect.login()
    sys.exit()

if args.file != "None":
    if apiconnect.logged() != False:
        print(colored(apiconnect.prompt.split(", ")[0], 'cyan'),
            colored(apiconnect.prompt.split(", ")[1], 'blue'))
        print("File:",args.file)
        pth = os.path.abspath(args.file)
        show = guessit.guessit(pth)

        txt = "Scrobbling {}: {}".format(show["type"], show["title"])
        if show["type"] == "episode":
            txt += " S{}E{}".format(str(show["season"]).zfill(2), 
                str(show["episode"]).zfill(2))    
        print(txt)

    else:
        print("First you need to log in, use --login")
else:
    if args.daemon:
        print("Starting daemon")
        tr = tracker.Tracker("mpv", 10, 10)
    else:
        parser.print_help()