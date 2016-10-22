#!/usr/bin/python3
# -*- coding: utf-8 -*-
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

import sys
from trackl.ui.QtUi import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets

from trackl import tracker
from trackl import apiconnect

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog=QtWidgets.QMainWindow()

    prog = Ui_MainWindow.__init__(dialog)

    dialog.show()
    sys.exit(app.exec_())