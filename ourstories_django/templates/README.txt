Django templates for the OurStories platform
============================================

Every displayable page in this site has a corresponding template, with
more-or-less the same name as its access URL.

All page templates inherit from a base template (called "base.html",
surprisingly).

In other words, to re-skin the site, most changes would have to be made
to "base.html" only; as long as the Django "insert blocks" are retained in
base.html, most things should work fine with a new look.
 