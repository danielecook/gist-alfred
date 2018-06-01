#!/usr/bin/python
# encoding: utf-8

import sys
import workflow
from workflow import Workflow, web
from collections import Counter
from pprint import pprint as pp
from workflow.background import run_in_background, is_running


def main(wf):

    arg = wf.args[0]

    wf.add_item(u"Set Token", arg=arg, valid=True, icon="icons/token.png")

    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow()
    log = wf.logger
    sys.exit(wf.run(main))
