#!/bin/python3

import sys
from Htg import Application

Manifest = { "components": dict() }
App = Application("hastag.linux.git-cloner", Manifest, "src")

Manifest["launcher"] = "TestActivity"

from py.TestActivity import TestActivity
Manifest["components"]["TestActivity"] = { "class": TestActivity, "single-instance": False, "custom-header": True }

App.run(sys.argv[1:])
