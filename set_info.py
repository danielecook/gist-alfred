#!/usr/bin/python
# encoding: utf-8

import sys
from workflow import Workflow, web
from collections import Counter
from workflow.background import run_in_background, is_running


wf = Workflow()



arg = wf.args[0]
#arg = wf.args[0]


if arg.startswith("Username:"):
    username = arg.split(":")[1]
    wf.store_data("Username", username)
    arg = "Saved " + arg
elif arg.startswith("Token:"):
    token = arg.split(":")[1]
    wf.save_password('Token',token)

wf.send_feedback()


