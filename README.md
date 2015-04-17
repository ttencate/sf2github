sf2github README
================

sf2github is a Python program
that reads a JSON export from a SourceForge project
and pushes this data to GitHub via its REST API.

The preferred entry point is `sf2gh`.

The script is currently somewhat incomplete and barely tested.
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

Two Factor Authentication
-------------------------

If you are using two factor authentication you will not be able to use
your password and you'll get errors from the GitHub API about needing a
OTP. The easiest way to handle this is to go to your profile and under
Applications you will find Personal access tokens. There you can generate a
new token that you will use for a password here. Once you're done with the
import you should delete the token to reduce the chances that someone can
get into your account.

Code migration
--------------

This script doesn't help you to migrate code from SF's Subversion to GitHub.
However, I found the following page helpful in doing that:
http://help.github.com/svn-importing/

Usage
-----

From SourceForge, you need to export the tracker data. This is done through
the Export function of the admin interface.

For more details on usage, run `sf2gh -h` and it will print
further instructions.
Basically, if your SF export is in `bugs.json`, your GitHub username is `john`
and your repository is `bar`:

    ./sf2gh bugs.json john/bar


*Manual installation*

The `sf2gh` command uses `python2.7` and wraps execution in a virtual
environment installed using `virtualenv` and `pip`. If that doesn't work for
you, try installing dependencies in `requirements.txt` and then running
`./sf2ghJSON.py` directly.




License
-------

This software is in the public domain.
I accept no responsibility for any damage resulting from it.
Use at your own risk.
