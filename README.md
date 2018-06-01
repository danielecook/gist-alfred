# gist-alfred

### [Download](https://github.com/danielecook/gist-alfred/releases/latest)

An alfred workflow for accessing gists as snippets. Features:

* Hot-key for creating new gist <kbd>CMD</kbd>+<kbd>SHIFT</kbd>+<kbd>G</kbd>
* Full Search
* Adds tagging and allows filtering by tag
* Allows filtering and search by programming language.
* Filter by starred, public, and private gists. 
* Stores gists locally to speed up access. Reload as needed.

__Setup__

Type `gg_set` and enter a [personal access token](https://github.com/blog/1509-personal-api-tokens) from github. The workflow takes some time to load new snippets because of the way the gist API is set up.

__Implements tags using #__

![Filter by tag](img/filter_tag.png)

__Gists can be filtered by Language__

![Filter by Language](img/filter_lang.png)

__Search Gists__

![Search](img/search.png)

__Filter by starred__

![Starred](img/filter_starred.png)
