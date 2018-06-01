#!/usr/bin/python
# encoding: utf-8

import sys
import itertools
from workflow import Workflow, web
from github import Github
from pprint import pprint as pp
from gist import __version__
from datetime import datetime
from collections import Counter, OrderedDict

def main(wf):
    log = wf.logger
    log.info("Fetching Gists")
    # Fetch user token
    token = wf.get_password("GitHub-gist-alfred-token")
    gh = Github(login_or_token=token)
    gh_user = gh.get_user()
    gist_set = []
    user_gists = list(gh_user.get_gists())
    for n, gist in enumerate(user_gists):
        log.info(gist)
        gist_item = {}
        gist_item.update(gist.__dict__['_rawData'])
        gist_item['description'] = gist_item.get('description') or ""
        gist_item['public'] = gist.public
        gist_item['forked'] = len(gist.forks) > 0
        gist_item['starred'] = gist.is_starred()
        tag_list = list(set([x.replace("#","") for x in gist_item['description'].split(" ") if x.startswith("#")]))
        tag_list = list(filter(len, tag_list))
        gist_item['tags'] = tag_list
        # Join content of gist files together for searching
        gist_item['content'] = ' '.join([x.content for x in gist.files.values() if x.content])
        gist_set.append(gist_item)
        try:
            gist_item['language'] = gist_item['files'].values()[0]['language'].replace(" ", "-")
        except AttributeError:
            gist_item['language'] = ""

        wf.store_data('current_gist', n)
        wf.store_data('total_gists', len(user_gists))

    tags = itertools.chain.from_iterable([x['tags'] for x in gist_set])
    tag_counts = Counter(tags).most_common()
    tag_counts = OrderedDict(tag_counts)
    wf.store_data('tag_counts', tag_counts)
    language_counts = Counter([x['language'] for x in gist_set]).most_common()
    language_counts = OrderedDict(language_counts)
    wf.store_data('language_counts', language_counts)

    n_starred = len([x for x in gist_set if x['starred']])
    n_forked = len([len(x) > 0 for x in gist_set if x['forked']])
    n_public = len([x for x in gist_set if x['public']])
    n_private = len([x for x in gist_set if not x['public']])
    wf.store_data('n_starred', n_starred)
    wf.store_data('n_forked', n_forked)
    wf.store_data('n_public', n_public)
    wf.store_data('n_private', n_private)
    wf.store_data('gists', gist_set)

    # Last refresh
    wf.store_data('last_update', datetime.now())

    # Reset status
    wf.store_data('current_gist', None)
    wf.store_data('total_gists', None)

wf = Workflow()

if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
