""" picasa.py
This module contains Google Picasa-related functions; it relies on
Google's "gdata-client-python" project's "gdata" module, which
is available here: http://code.google.com/p/gdata-python-client/

A local copy of the gdata module is included in the top-level dir of the project for convenience;
this may safely be removed if gdata is installed to the system.

The details of the Picasa account to use are set in django's top-level settings.py.
"""

import mimetypes

import gdata.photos.service

from django.conf import settings
from settings import PICASA_USERNAME, PICASA_PASSWORD 

def uploadImage(imgFilename, title, summary=''):
    """ Uploads the image with the specified filename (should be absolute) to Picasa,
    using the account settings in the Django settings.py file
    
    @return: the resulting URL of the image on Picasa
    @rtype: str
    """
    gdClient = gdata.photos.service.PhotosService()
    gdClient.ClientLogin(PICASA_USERNAME, PICASA_PASSWORD)
    albumUrl = '/data/feed/api/user/%s/album/%s' % ('default', 'OurStories')
    entry = gdClient.InsertPhotoSimple(albumUrl, title=title, summary=summary, filename_or_handle=imgFilename, content_type=mimetypes.guess_type(imgFilename)[0])
    r = str(entry.content.src)
    k = r[r.rfind('/'):]
    r = r.replace(k,'/s800'+k)
    return r

def deleteImage(imageUri):
    """ Attempts to delete the image with the specified URI """
    gdClient = gdata.photos.service.PhotosService()
    gdClient.ClientLogin(PICASA_USERNAME, PICASA_PASSWORD)
    try:
        gdClient.Delete(imageUri)
    except Exception:
        pass
