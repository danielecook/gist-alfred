#!/usr/bin/python
# encoding: utf-8

import sys
from workflow import Workflow, web

__version__ = '0.2'


def get_gist():
    username = wf.stored_data("Username")
    token = wf.get_password("Token")
    headers = { 'X-Github-Username': username,
                    'Content-Type': 'application/json',
                    'Authorization': 'token %s' % token}

    # Get Starred Gists
    starred = web.post(url="https://api.github.com/gists/starred?per_page=100000",headers=headers).json()
    starred_ids = [x["id"] for x in starred]

    gists = web.post(url="https://api.github.com/users/{u}/gists?per_page=100000".format(u=username),headers=headers).json()
    gist_ids = [x["id"] for x in gists]
    all_gists = list(set(starred_ids + gist_ids))
    # Load gists:
    gists = [web.post(url="https://api.github.com/gists/" + i,headers=headers).json() for i in all_gists]
    #for i in gists:
    #    print i 
    # Check if starred
    for gist in gists:
        if gist["id"] in starred_ids:
            gist["starred"] = True
        else:
            gist["starred"] = False
        #if gist["id"] in forked_ids:
        #    gist["forked"] = True
        #else:
        #    gist["forked"] = False

    return gists


def main(wf):
    gists = get_gist()
    wf.store_data('gists', gists)

wf = Workflow()

if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
