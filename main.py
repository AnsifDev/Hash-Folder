#!/bin/python3

import sys
from src.py.Application import Application

def main():
    """The application's entry point."""
    app = Application()
    return app.run(sys.argv)

main()
