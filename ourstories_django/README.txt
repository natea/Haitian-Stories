Setting up an Ubuntu Karmic server
==================================

apt-get update
apt-get install apache2 libapache2-mod-python python2.6-dev imagemagick mencoder ffmpeg

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

Load geodata
------------

Import the countries and cities. You'll still need to manually add the languages and categories.

    $ cd haitianstories/geodata
    $ gunzip countryInfo.txt.gz
    $ gunzip cities15000.txt.gz
    $ ./manage.py load_geodata ../geodata/countryInfo.txt ../geodata/cities15000.txt
    
Youtube configuration
---------------------

Go into settings.py and change the following settings::

    YOUTUBE_EMAIL = 'someuser@somedomain.com'
    YOUTUBE_PASSWORD = 'somepassword'
    YOUTUBE_SOURCE = 'yourappid'
    YOUTUBE_CLIENT_ID = '' # not used anymore
    YOUTUBE_DEVELOPER_KEY = 'yourdeveloperkey'

Picasa configuration
--------------------

Picasa is used for the thumb
Go into settings.py and change the following settings::

    PICASA_USERNAME = 'someuser@somedomain.com'
    PICASA_PASSWORD = 'somepassword'

Set up the streaming from Red5
------------------------------

Once Red5 is set up, go into the static dir and make a symlink to the Red5 streams dir::

    $ cd /var/local/haitianstories/ourstories_django/static
    $ ln -s /opt/red5/webapps/oflaDemo/streams/ flv
    
Configure the URLs for the SWF player
-------------------------------------

Edit the file /var/local/haitianstories/ourstories_django/static/swf/ourstories_config.xml::

    <?xml version="1.0" encoding="utf-8"?>
    <ourstories_config>

        <red5_nc_url>rtmp:/oflaDemo</red5_nc_url>
        <amf_nc_url>http://haitianstories.org/gateway/</amf_nc_url>
        <flv_url>http://haitianstories.org/static/flv/</flv_url>
        <story_url>http://haitianstories.org/story/</story_url>
        <story_record_url>haitianstories.org/story/record/</story_record_url>
        <max_record_sec>180</max_record_sec>
        <debug>0</debug>
        
    </ourstories_config>
    
