""" youtube.py
This module contains Google Youtube interface functions; it relies on
Google's "gdata-client-python" project's "gdata" module, which
is available here: http://code.google.com/p/gdata-python-client/

A local copy of the gdata module is included in the top-level dir of the project for convenience;
this may safely be removed if gdata is installed to the system.

@note: no video encoding/creation functions are defined here, only youtube-integration mechanims
       for video creation functions, see video.py

The details of the Youtube account to use are set in django's top-level settings.py.
"""

import gdata.youtube.service
import gdata.media
import gdata.geo

from socket import error as SocketError

from django.conf import settings

from settings import YOUTUBE_EMAIL, YOUTUBE_PASSWORD, YOUTUBE_SOURCE, YOUTUBE_DEVELOPER_KEY, YOUTUBE_CLIENT_ID

def uploadVideo(videoFilename, title, description='', keywords=[], geoLatLongTuple=None):
    """ Uploads the video clip with the specified filename (should be absolute) to Youtube,
    using the account settings in the Django settings.py file
    
    @param geoLatLongTuple: An optional tuple containing the latitude and longitude of where the video was recorded
                            Format: (<float>lat, <float>long)
                            Example: (-25.43, 28.17)
    @type geoLatLongTuple: tuple
    
    @return: the resulting URL of the video clip on Youtube
    @rtype: str
    """
    # Login to youtube
    client = gdata.youtube.service.YouTubeService(email=YOUTUBE_EMAIL,
                                                  password=YOUTUBE_PASSWORD,
                                                  source=YOUTUBE_SOURCE,
                                                  client_id=YOUTUBE_CLIENT_ID,
                                                  developer_key=YOUTUBE_DEVELOPER_KEY)
    client.ProgrammaticLogin()
    
    # Prepare a media group object to hold our video's meta-data
    mediaGroup = gdata.media.Group(title=gdata.media.Title(text=title),
                                   description=gdata.media.Description(description_type='plain', text=description),
                                   keywords=gdata.media.Keywords(text=','.join(keywords)),
                                   # See the scheme URL below for information on the allowed categories ("Nonprofit" may also be a good fit, but I felt "People" is a little bit more descriptive) 
                                   category=gdata.media.Category(text='People',
                                                                 scheme='http://gdata.youtube.com/schemas/2007/categories.cat',
                                                                 label='People'),
                                   player=None)
    
    
    if geoLatLongTuple != None:
        # Prepare a geo.where object to hold the geographical location of where the video was recorded
        where = gdata.geo.Where()
        where.set_location(geoLatLongTuple)
        # create the gdata.youtube.YouTubeVideoEntry to be uploaded
        videoEntry = gdata.youtube.YouTubeVideoEntry(media=mediaGroup, geo=where)
    else:
        # create the gdata.youtube.YouTubeVideoEntry without geo-position information
        videoEntry = gdata.youtube.YouTubeVideoEntry(media=mediaGroup, geo=where)
    
    # Upload the video...
    try:
        entry = client.InsertVideoEntry(videoEntry, videoFilename, content_type='video/avi')
    except SocketError:
        #FNA: This sometimes happens - perhaps it's just my questionable net connection... anyhow, a single retry solves it
        entry = client.InsertVideoEntry(videoEntry, videoFilename, content_type='video/avi')
        
    # ...and extract the link to its new URL
    l = '%s' % (entry.id)
    ID = l.split('/')
    link = "http://www.youtube.com/v/"+ID[-2][0:len(ID[-2])-1]
    return link




def getBrowserUploadInfo(story=None):
    """Prepare to upload a video to youtube via the end-user's browser.
    Youtube will redirect with the following parameters, for example:
    ?status=200&id=Su4ArLGM8l8"""

    keywords = ["OurStories"]


    if story:
        vid_title = story.title
        vid_description = story.summary
        try:
            vid_lat = float(story.latitude)
            vid_long = float(story.longitude)
        except (ValueError, TypeError):
            vid_lat = None
            vid_long = None
    else:
        vid_title = "OurStories uploaded video"
        vid_description = "This video has been uploaded to OurStories, a UNICEF project."
        vid_lat = None
        vid_long = None

    # Login to youtube
    client = gdata.youtube.service.YouTubeService(email=YOUTUBE_EMAIL,
                                                  password=YOUTUBE_PASSWORD,
                                                  source=YOUTUBE_SOURCE,
                                                  client_id=YOUTUBE_CLIENT_ID,
                                                  developer_key=YOUTUBE_DEVELOPER_KEY)
    client.ProgrammaticLogin()
    
    # Prepare a media group object to hold our video's meta-data
    mediaGroup = gdata.media.Group(title=gdata.media.Title(text=vid_title),
                                   description=gdata.media.Description(description_type='plain', text=vid_description),
                                   keywords=gdata.media.Keywords(text=','.join(keywords)),
                                   # See the scheme URL below for information on the allowed categories ("Nonprofit" may also be a good fit, but I felt "People" is a little bit more descriptive) 
                                   category=gdata.media.Category(text='People',
                                                                 scheme='http://gdata.youtube.com/schemas/2007/categories.cat',
                                                                 label='People'),
                                   player=None)
    
    # Prepare a geo.where object to hold the geographical location of where the video was recorded
    if vid_lat and vid_long:
        where = gdata.geo.Where()
        where.set_location((vid_lat, vid_long))
        # create the gdata.youtube.YouTubeVideoEntry to be uploaded
        videoEntry = gdata.youtube.YouTubeVideoEntry(media=mediaGroup, geo=where)
    else:
        videoEntry = gdata.youtube.YouTubeVideoEntry(media=mediaGroup)

    (url, token) = client.GetFormUploadToken(videoEntry)

    return (url, token)

