#!/usr/bin/python
# encoding: utf-8

import sys
from workflow import Workflow, web


def get_gist():
    username = wf.stored_data("Username")
    token = wf.get_password("Token")
    headers = { 'X-Github-Username': username,
                    'Content-Type': 'application/json',
                    'Authorization': 'token %s' % token}

    # Get Starred Gists
    starred_gists = []
    p = 1
    while True:
        r = web.post(url="https://api.github.com/gists/starred?page={p}".format(p=p),headers=headers).json()
        if not r:
            break
        starred_gists.extend(r)
        p += 1

    starred_ids = list(set([x['id'] for x in starred_gists]))

    gists = []
    p = 1
    while True:
        url = "https://api.github.com/users/{u}/gists?page={p}&per_page=100".format(u=username,p=p)
        print(url)
        r = web.post(url=url,headers=headers).json()
        if not r:
            break
        gists.extend(r)
        p += 1

    gist_ids = [x["id"] for x in gists]
    all_gists = list(set(starred_ids + gist_ids))

    # Load gists:
    gists = [web.post(url="https://api.github.com/gists/" + i,headers=headers).json() for i in all_gists]
    # Check if starred
    for gist in gists:
        if gist["id"] in starred_ids:
            gist["starred"] = True
        else:
            gist["starred"] = False

    return gists


def main(wf):
    log = wf.logger
    gists = get_gist()
    n_starred = len([x for x in gists if x['starred']])
    n_forked = len([x for x in gists if x['forks']])
    n_public = len([x for x in gists if x['public']])
    n_private = len([x for x in gists if not x['public']])
    wf.store_data('n_starred', n_starred)
    wf.store_data('n_forked', n_forked)
    wf.store_data('n_public', n_public)
    wf.store_data('n_private', n_private)
    wf.store_data('gists', gists)

wf = Workflow()

if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
