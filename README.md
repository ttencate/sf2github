sf2github README
================

`sf2github` is a Python program
that reads an XML export from a SourceForge project
and pushes this data to GitHub via its REST API.

The script is currently very incomplete and barely tested.
If it works for you, great; if not, fix it up and send me a pull request!
Currently, only migration of tracker issues is partly implemented,
and there's little error handling.

Also note that the GitHub API is quite slow,
taking about 5 seconds per request on my machine and internet connection.
Migration of a large project will take a while.

Issue migration
---------------

What works (for me):

* SF tracker issues become GitHub tracker issues.
* Comments on SF become comments in GitHub.
* Groups and categories on SF both become labels on GitHub.
* Issues with a status that is exactly the text "Closed" or "Deleted"
  will be closed on GitHub.
* Items from trackers with the default names
  "Bug", "Feature Request", "Patch" and "Tech Support"
  will receive default prefixes in their title (see the code).
  For trackers with other names, the user will be prompted.

Limitations:

* All issues and comments will be owned by the project's owner on GitHub,
  but mention the SF username of the original submitter.
* Creation times will be the date of the import,
  not the creation time from SourceForge. (However, most recently updated
  tracker items will be the most recently added ones after the import:
  I.e., the ordering is preserved)

Code migration
--------------

This script doesn't help you to migrate code from SF's Subversion to GitHub.
However, I found the following page helpful in doing that:
http://help.github.com/svn-importing/

Usage
-----

sf2github depends on the [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/),
the [requests](http://docs.python-requests.org/en/latest/) and the 're' modules.
If you don't have them, install them first.

From SourceForge, you need to export the tracker data in XML.
Read [here](https://sourceforge.net/apps/trac/sourceforge/wiki/XML export) for instructions.

Run the `issues.py` script and it will print further instructions.
Basically, if your SF XML export is in `foo.xml`,
your GitHub username is `john`
and your repository is `bar`:

    ./issues.py foo.xml john/bar

License
-------

This software is in the public domain.
I accept no responsibility for any damage resulting from it.
Use at your own risk.
