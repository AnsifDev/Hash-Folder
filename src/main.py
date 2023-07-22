#!/bin/python3

import sys
from Htg import Application

from py.MyApp import MyApp
if not issubclass(MyApp, Application): raise Exception("Invalid Application Class")

Manifest = { "components": dict() }
App = MyApp("hastag.linux.git-cloner", Manifest, "src")

Manifest["launcher"] = "TestActivity"

from py.TestActivity import TestActivity
Manifest["components"]["TestActivity"] = { "class": TestActivity, "single-instance": False, "custom-header": True }

App.run(sys.argv[1:])
