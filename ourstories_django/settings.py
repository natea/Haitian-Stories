# Django settings for ourstories_django project.

#FNA: sys imported for development dir structure; see "FNA"-tagged comments, below
import sys,os

# add lib directory
ROOT_PATH = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(ROOT_PATH,'lib'))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# Google Picasa account information for use by the OurStories system
PICASA_USERNAME = ''
PICASA_PASSWORD = ''

# Youtube account information for use by the OurStories system 
YOUTUBE_EMAIL = '' 
YOUTUBE_PASSWORD = ''
#YOUTUBE_SOURCE = ''
#YOUTUBE_CLIENT_ID = ''
YOUTUBE_DEVELOPER_KEY = ''

# Google Maps API KEY
# old key, for ourstories.mepemepe.com I think:
# key for http://ourstories-staging.jazkarta.com/ :
GOOGLE_MAPS_API_KEY = ""

#### Settings for the video encoder module (ourstories/video.py) ###
VIDEO_IMAGEMAGICK_CONVERT_BIN = 'convert' # path to the ImageMagick "convert" executable binary
VIDEO_FFMPEG_BIN = 'ffmpeg' # path to the "ffmpeg" executable
VIDEO_MENCODER_BIN = 'mencoder' # path to the "mencoder" executable
#### end of video encoding-related settings

# Red5 Flash Media Server settings
RED5_UPLOAD_PATH = '/home/francois/bin/red5-0.7/webapps/LiveStreams/streams/MPlayer-1.0rc2/' # local directory where the red5 server stores recorded stories; this has to end with a /
 
ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = ROOT_PATH+'/ourstories_db'             # Or path to database file if using sqlite3.
DATABASE_USER = 'unicef'             # Not used with sqlite3.
DATABASE_PASSWORD = 'unicef'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(ROOT_PATH,'static')

# FLV_ROOT is a symlink to RED5_STREAMS_ROOT
# django knows the FLV_ROOT
# red5 knows the RED5_STREAMS_ROOT
FLV_ROOT = os.path.join(MEDIA_ROOT,'flv')
RED5_STREAMS_ROOT = '/opt/red5/webapps/oflaDemo/streams'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ca1j@@h!bccz6u^@13i()&lg%sg1mv6%+0%9a5p15jgk-h==(y'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'ourstories_django.urls'

# FNA: Using sys.path[0] here to get a Turbogears-style relative template dir for development;
# change this to something absolute on production deployment
TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(ROOT_PATH,'templates'),
)


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.comments',
    'django.contrib.admin',
    'django_evolution',
    'flv',
    'ourstories',
    'storyfeed',
)



TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.request",
    'django.core.context_processors.auth',
    'ourstories.context_processors.api_keys',
)



# when updating stories from (Praekelt etc) feeds, how long to wait from most recent feed poll?
FEED_UPDATE_INTERVAL = 60*5 # seconds

# don't bother loading cities with populations less than...
MINIMUM_POPULATION_CITY_TO_LOAD = 80000


# login / django auth is used for admins (and flagging) only.
LOGIN_URL = "/admin/"

# import any local settings overrides if available
try:
    from local_settings import *
except ImportError:
    pass
