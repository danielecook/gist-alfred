#!/usr/bin/python
# encoding: utf-8

import sys
from workflow import Workflow, web
from collections import Counter
from pprint import pprint as pp
from workflow.background import run_in_background, is_running

__version__ = '0.2'


def main(wf):
    if wf.args != []:
        arg = wf.args[0].split(" ")
    else:
        arg = ["#VCF","l"]
    term = arg[0].strip()
    search = ' '.join(arg[1:])
    show_results = True
    if wf.stored_data('gists') == None:
        run_in_background('update',['/usr/bin/python', wf.workflowfile('update_gists.py')])
    # Add a notification if the script is running
    if is_running('update'):
        username = wf.stored_data("Username")
        if username is None:
            wf.add_item("Set your github username with gg_set", icon="icons/info.png")
        try: 
            wf.get_password("Token")
        except:
            wf.add_item("Set your github-token with gg_set", icon="icons/info.png")
        wf.add_item('Downloading Latests Gists. This may take a bit.', icon="icons/download.png")
        wf.send_feedback()
        sys.exit()

    gists = wf.stored_data('gists')
    lang = "" # Multi-file gist language filtering

    tag_set = []
    lang_set = []
    for gist in gists:
        # fails if no description. to fix:
        if not gist["description"]:
            gist["description"]=''
        tags = list(set([x.replace("#","") for x in gist["description"].split(" ") if x.startswith("#")]))
        gist["tags"] = tags
        tag_set.extend(tags)
        lang_files = [str(x["language"]) for x in gist["files"].values()]
        gist["langs"] = lang_files
        lang_set.extend(lang_files)

    results = []

    if term == "":
        show_results = False
        # List Options
        wf.add_item("Starred", autocomplete = u"\u2605 ", icon="icons/star.png")
        # wf.add_item("Forked", autocomplete = u"\u2442", icon="icons/forked.png") # Forked not presently supported.
        wf.add_item("Tags", autocomplete = "#", icon="icons/tag.png")
        wf.add_item("Language", autocomplete = "$", icon="icons/language.png")
        wf.add_item("Private", autocomplete = "Private ", icon="icons/private.png")
        wf.add_item("Public", autocomplete = "Public ", icon="icons/public.png")
        wf.add_item("Reload", autocomplete = "Reload", icon="icons/download.png")
    elif term == "Reload":
        run_in_background('update',['/usr/bin/python', wf.workflowfile('update_gists.py')])
        wf.add_item('Downloading Latests Gists. This may take a bit.', icon="icons/download.png")
        wf.send_feedback()
        sys.exit()
    elif term.startswith("#") and term.replace("#","") not in tag_set and len(search) == 0:
        show_results = False
        tag_set = Counter(tag_set)
        tag_search = tag_set.items()
        tag_search = sorted(tag_search, key=lambda x: x[0].lower())
        for tag, count in tag_search:
            if tag.lower().startswith(term.lower().replace("#","")):
                results.append(0) # Prevent no results found from being shown.
                wf.add_item("{tag} ({count})".format(**locals()), autocomplete = "#" + tag + " ", icon="icons/tag.png")
    elif term.replace("#","") in tag_set:
        # List Gist
        tag = term.split(" ")[0].replace("#","")
        results = [x for x in gists if tag in x["tags"]]
    elif term.startswith("$") and term.replace("$","") not in lang_set and len(search) == 0:
        show_results = False
        lang_set = Counter(lang_set)
        lang_search = lang_set.items()
        lang_search = sorted(lang_search, key=lambda x: x[0].lower())
        for lang, count in lang_search:
            if lang.lower().startswith(term.lower().replace("$","")):
                results.append(0) # Prevent no results found from being shown.
                wf.add_item("{lang} ({count})".format(**locals()), autocomplete = "$" + lang + " ", icon="icons/{lang}.png".format(lang=lang))
    elif term.replace("$","") in lang_set:
        # List Gist
        lang = term.split(" ")[0].replace("$","")
        results = [x for x in gists if lang in x["langs"]]
    elif term == "Public":
        # List Public
        results = [x for x in gists if x["public"] == True]
    elif term == "Private":
        # List Private
        results = [x for x in gists if x["public"] == False]
    #elif term == u"\u2442" or term == "Forked":
    #    # List Private
    #    results = [x for x in gists if x["forked"] == True]
    elif term == u"\u2605" or term == "Starred":
        # List Private
        results = [x for x in gists if x["starred"] == True]
    else:
        # Perform search
        search = term + " " + search
        results = gists

    if show_results == True:
        if search != "":
            results = wf.filter(search, results, lambda x: x["description"] + ' '.join(x["tags"]) + ' '.join(x["files"].keys()))
        for gist in results:
            for filename, f in gist["files"].items():
                if lang == "" or f["language"] == lang:
                    wf.add_item(gist["description"],
                    filename + " | " + f["content"].replace("\n"," "),
                    arg=f["content"], 
                    copytext=gist["url"],
                    valid = True,
                    icon="icons/" + str(f["language"]) + ".png")
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
