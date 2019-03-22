#!/usr/bin/python
# encoding: utf-8

from gist import create_workflow, set_github_token
from workflow import Workflow, web
from workflow.background import run_in_background, is_running


def main(wf):
    if len(arg) > 0:
        token = wf.args[0]
        set_github_token(wf, token)


if __name__ == '__main__':
    wf = create_workflow()
    sys.exit(wf.run(main))
