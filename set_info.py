#!/usr/bin/python
# encoding: utf-8

import sys
from workflow import Workflow, web
from collections import Counter
from workflow.background import run_in_background, is_running


wf = Workflow()
arg = wf.args[0]
if len(arg) > 0:
    token = arg
    wf.save_password('GitHub-gist-alfred-token', token)
    wf.send_feedback()