#!/usr/bin/python
# encoding: utf-8

from collections import Counter
from gist import create_workflow
from pprint import pprint as pp
import sys
import workflow
from workflow import Workflow, web
from workflow.background import run_in_background, is_running


def main(wf):
    arg = wf.args[0]
    wf.add_item(u"Set token", arg=arg, valid=True, icon="icons/token.png")
    wf.send_feedback()


if __name__ == '__main__':
    wf = create_workflow()
    sys.exit(wf.run(main))
