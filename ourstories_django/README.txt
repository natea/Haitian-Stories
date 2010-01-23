ourstories_django
=================

This is a Django (http://www.djangoproject.org) project. It can be started by
running the manage.py script:

$./manage.py runserver

Applications
------------
This project has one main django app, located in the "ourstories" directory.
Dependencies for this application are Google's "gdata" and "atom" packages;
local copies of these are included on the PYTHONPATH (this directory) for
convenience - they may be safely removed if these are installed to the system.

Templates
---------
Templates for this django project are found in the "templates" directory.

Static content
--------------
All static content (images, javascript, css, flash, etc) are located in the
"static" directory.

Requirements
------------
- Django 1.0
- python-simplejson >= 1.9.1 (if using Python 2.5 or lower; Python 2.6's 
                              included "json" module should work fine as a
                              drop-in replacement)

Other misc utilities
--------------------
The "utils" directory in this directory contains some Python utilities used
during development; they have no use at run-time.
