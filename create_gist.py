#!/usr/bin/python
# encoding: utf-8

from gist import create_workflow, get_github_token
from github import Github, GithubObject
from github.InputFileContent import InputFileContent
import os
import os.path
from pprint import pprint as pp
import pyperclip
import sys
from update_gists import create_gist_item
from workflow import Workflow, web


def read_file(path):
    with open(path, 'r') as f:
        return f.read()


def main(wf):
    log = wf.logger

    # Process command-line arguments.
    public = int(os.environ['GIST_PUBLIC']) == 1
    files = wf.args[0].split(u"\t") if wf.args[0] else None

    # Fetch user token.
    gh = Github(login_or_token=get_github_token(wf))
    gh_user = gh.get_user()

    # Create new gist for user.
    log.info("Creating new gist...")
    if files:
        log.info("Creating gist from files: %s." % ", ".join("`%s`" % f for f in files))
        files = { os.path.basename(f): InputFileContent(read_file(f)) for f in files }
    else:
        log.info("Creating gist from clipboard.")
        files = { "paste": InputFileContent(pyperclip.paste()) }
    gist = gh_user.create_gist(public, files, GithubObject.NotSet)
    log.info(gist)
    print(gist.html_url)

    # Update cache of gists.
    gist_set = wf.stored_data('gists')
    n_starred = wf.stored_data('n_starred')
    n_forked = wf.stored_data('n_forked')
    n_public = wf.stored_data('n_public')
    n_private = wf.stored_data('n_private')
    tag_counts = wf.stored_data('tag_counts')
    language_counts = wf.stored_data('language_counts')
    
    gist_item = create_gist_item(gist)
    gist_set.append(gist_item)
    n_starred += 1 if gist_item['starred'] else 0
    n_forked += 1 if gist_item['forked'] else 0
    n_public += 1 if gist_item['public'] else 0
    n_private += 1 if not gist_item['public'] else 0
    for tag in gist_item['tags']:
        tag_counts[tag] += 1
    if gist_item['language']:
        language_counts[gist_item['language']] += 1

    wf.store_data('gists', gist_set)
    wf.store_data('n_starred', n_starred)
    wf.store_data('n_forked', n_forked)
    wf.store_data('n_public', n_public)
    wf.store_data('n_private', n_private)
    wf.store_data('tag_counts', tag_counts)
    wf.store_data('language_counts', language_counts)


if __name__ == '__main__':
    wf = create_workflow()
    sys.exit(wf.run(main))
