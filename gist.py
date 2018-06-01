#!/usr/bin/python
# encoding: utf-8

import sys
import workflow
import os
from workflow import Workflow, web
from collections import Counter
from workflow.background import run_in_background, is_running
from subprocess import Popen
from datetime import datetime

__version__ = '0.5'


def main(wf):
    arg = wf.args[0].split(" ")
    term = arg[0].strip()
    search = ' '.join(arg[1:])
    show_results = True

    try: 
        wf.get_password("GitHub-gist-alfred-token")
    except workflow.PasswordNotFound:
        wf.add_item("Set A GitHub Token with 'gg_set <token>'", icon="icons/error.png")
        wf.send_feedback()
        sys.exit()

    # Get last update
    last_update = wf.stored_data('last_update')
    if last_update:
        diff = (datetime.now() - last_update).seconds

        # Update daily
        if diff > 60*60*24:
            if not is_running(u"update_gists"):
                run_in_background('update_gists',['/usr/bin/python', wf.workflowfile('update_gists.py')])
                wf.add_item('Gist Update Triggered', icon="icons/download.png")

    # Initial Load
    if wf.stored_data('gists') is None:
        n = wf.stored_data('current_gist')
        total = wf.stored_data('total_gists')
        if n:
            status = 'Gists are being updated ({}/{}; {}%)'.format(n, total, int((n*1.0/total)*100))
        else:
            status = "Gists are being updated"
        wf.add_item(status, icon="icons/download.png")
        wf.send_feedback()
        if not is_running(u"update_gists"):
            run_in_background(u"update_gists",['/usr/bin/python', wf.workflowfile('update_gists.py')])
            # Exit for initial
        sys.exit()

    elif is_running(u"update_gists"):
        n = wf.stored_data('current_gist')
        total = wf.stored_data('total_gists')
        if n:
            status = 'Gists are being updated ({}/{}; {}%)'.format(n, total, int((n*1.0/total)*100))
        else:
            status = "Gists are being updated"
        wf.add_item(status, icon="icons/download.png")



    gists = wf.stored_data('gists')
    n_starred = wf.stored_data('n_starred')
    n_forked = wf.stored_data('n_forked')
    n_public = wf.stored_data('n_public')
    n_private = wf.stored_data('n_private')
    lang = "" # Multi-file gist language filtering

    tag_set = wf.stored_data('tag_counts')
    lang_set = wf.stored_data('language_counts')

    results = []
    if term == "":
        show_results = False
        # List Options
        wf.add_item(u"Create Gist", valid=True, arg='__new_gist', icon="icons/gist.png")
        wf.add_item(u"Starred (%s)" % n_starred, autocomplete = u"\u2605 ", icon="icons/star.png")
        wf.add_item(u"Forked (%s)" % n_forked, autocomplete = u"\u2442 ", icon="icons/forked.png") # Forked not presently supported.
        wf.add_item(u"Tags", autocomplete = "#", icon="icons/tag.png")
        wf.add_item(u"Language", autocomplete = "$", icon="icons/language.png")
        wf.add_item(u"Private (%s)" % n_private, autocomplete = "Private ", icon="icons/private.png")
        wf.add_item(u"Public (%s)" % n_public, autocomplete = "Public ", icon="icons/public.png")
        wf.add_item(u"Update (last update: {})".format(last_update.strftime("%Y-%m-%d %H:%M")), autocomplete = "Update", icon="icons/download.png")
    elif term == "Update":
        if not is_running(u"update_gists"):
            run_in_background('update_gists',['/usr/bin/python', wf.workflowfile('update_gists.py')])
            wf.add_item('Updating Gists', icon="icons/download.png")
            wf.send_feedback()
            sys.exit()
    elif term.startswith("#") and term.replace("#","") not in tag_set and len(search) == 0:
        show_results = False
        for tag, count in tag_set.items():
            if tag.lower().startswith(term.lower().replace("#","")):
                results.append(0) # Prevent no results found from being shown.
                wf.add_item("{tag} ({count})".format(**locals()), autocomplete = "#" + tag + " ", icon="icons/tag.png")
    elif term.replace("#","") in tag_set:
        # List Gist
        tag = term.split(" ")[0].replace("#","")
        results = [x for x in gists if tag in x["tags"]]
    elif term.startswith("$") and term.replace("$","") not in lang_set and len(search) == 0:
        show_results = False
        for lang, count in lang_set.items():
            if lang.lower().startswith(term.lower().replace("$","")):
                results.append(0) # Prevent no results found from being shown.
                wf.add_item("{lang} ({count})".format(**locals()),
                             autocomplete = "${} ".format(lang),
                             icon="icons/{}.png".format(lang.lower()))
    elif term.replace("$","") in lang_set:
        # List Gist
        language = term.split(" ")[0].replace("$","").lower()
        results = [x for x in gists if language == x["language"].lower()]
    elif term == "Public":
        # List Public
        results = [x for x in gists if x["public"] == True]
    elif term == "Private":
        # List Private
        results = [x for x in gists if x["public"] == False]
    elif term == u"\u2442" or term == "Forked":
        # List Forked
        results = [x for x in gists if x["forked"]]
    elif term == u"\u2605" or term == "Starred":
        # List Starred
        results = [x for x in gists if x["starred"] == True]
    else:
        # Perform search
        search = term + " " + search
        results = gists

    if show_results == True:
        if search != "":
            results = wf.filter(search, results, lambda x: x["description"] + ' '.join(x["tags"]) + ' '.join(x["files"].keys()))
        for gist in results:
            filename, f = gist['files'].items()[0]
            filename, extension = os.path.splitext(filename)
            extension = extension.strip(".")
            if lang == "" or f["language"] == lang:
                if len(gist['content']) > 10000:
                    gist['content'] = "Unfortunately, this gist is too long to copy; Use CMD to get URL"
                    wf.add_item(gist['description'],
                                filename + " | " + gist["content"].replace("\n", "")[0:100],
                                arg=gist["html_url"] + "@@@gist@@@" + gist["content"],
                                copytext=gist["url"],
                                valid = False,
                                icon="icons/error.png".format(extension.lower()))
                else:
                    wf.add_item(gist['description'],
                                filename + " | " + gist["content"].replace("\n", "")[0:100],
                                arg=gist["html_url"] + "@@@gist@@@" + gist["content"],
                                copytext=gist["url"],
                                valid = True,
                                icon="icons/{}.png".format(extension.lower()))
    if len(results) == 0 and term != "":
        wf.add_item("No Results Found", valid=True, icon="icons/error.png")
    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow(update_settings={
        'github_slug': 'danielecook/gist-alfred',
        'version': __version__,
        'frequency': 7
        })
    if wf.update_available:
        # Download new version and tell Alfred to install it
        wf.start_update()
    log = wf.logger
    sys.exit(wf.run(main))
