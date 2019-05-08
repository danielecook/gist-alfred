#!/usr/bin/python
# encoding: utf-8

from collections import Counter, OrderedDict
from datetime import datetime
from gist import create_workflow, get_github_token
from github import Github
import itertools
from pprint import pprint as pp
import sys
from workflow import Workflow, web


def create_gist_item(gist):
    gist_item = {}
    gist_item.update(gist.__dict__['_rawData'])
    gist_item['description'] = gist_item.get('description') or ""
    gist_item['public'] = gist.public
    gist_item['forked'] = len(gist.forks) > 0
    gist_item['starred'] = gist.is_starred()
    tag_list = set([x.replace("#","") for x in gist_item['description'].split(" ") if x.startswith("#")])
    tag_list = filter(len, tag_list)
    gist_item['tags'] = list(tag_list)
    # Join contents of gist files together for full-text searching.
    gist_item['content'] = '\n'.join([x.content for x in gist.files.values() if x.content])
    try:
        gist_item['language'] = gist_item['files'].values()[0]['language'].replace(" ", "-")
    except AttributeError:
        gist_item['language'] = ""

    return gist_item


def main(wf):
    log = wf.logger

    # Fetch user token.
    gh = Github(login_or_token=get_github_token(wf))
    gh_user = gh.get_user()

    # Fetch all gists for user.
    log.info("Fetching gists...")
    gist_set = []
    user_gists = list(gh_user.get_gists())
    for n, gist in enumerate(user_gists):
        log.info(gist)
        gist_item = create_gist_item(gist)
        gist_set.append(gist_item)

        wf.store_data('current_gist', n)
        wf.store_data('total_gists', len(user_gists))

    # Update cache of gists.
    n_starred = len([x for x in gist_set if x['starred']])
    n_forked = len([len(x) > 0 for x in gist_set if x['forked']])
    n_public = len([x for x in gist_set if x['public']])
    n_private = len([x for x in gist_set if not x['public']])

    tags = itertools.chain.from_iterable([x['tags'] for x in gist_set])
    tag_counts = Counter(tags).most_common()
    tag_counts = OrderedDict(tag_counts)
    language_counts = Counter([x['language'] for x in gist_set if x['language']]).most_common()
    language_counts = OrderedDict(language_counts)

    wf.store_data('gists', gist_set)
    wf.store_data('n_starred', n_starred)
    wf.store_data('n_forked', n_forked)
    wf.store_data('n_public', n_public)
    wf.store_data('n_private', n_private)
    wf.store_data('tag_counts', tag_counts)
    wf.store_data('language_counts', language_counts)

    # Set last update date/time.
    wf.store_data('last_update', datetime.now())

    # Reset update status.
    wf.store_data('current_gist', None)
    wf.store_data('total_gists', None)


if __name__ == '__main__':
    wf = create_workflow()
    sys.exit(wf.run(main))
