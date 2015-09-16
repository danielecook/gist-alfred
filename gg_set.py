#!/usr/bin/python
# encoding: utf-8

import sys
from workflow import Workflow, web
from collections import Counter
from pprint import pprint as pp
from workflow.background import run_in_background, is_running

__version__ = '0.2'


def main(wf):
    arg = wf.args[0]

    if arg.startswith("Username:"):
        wf.add_item("Set Username", autocomplete= "username:", arg=arg, valid = True, icon="icons/star.png")

    elif arg.startswith("Token:"):
        wf.add_item("Set Token", autocomplete= "username:", arg=arg, valid = True, icon="icons/star.png")
    else:
        wf.add_item("Set Username", autocomplete= "Username:", icon="icons/star.png")
        wf.add_item("Set Token", autocomplete= "Token:", icon="icons/tag.png")

    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow()
    log = wf.logger
    sys.exit(wf.run(main))
