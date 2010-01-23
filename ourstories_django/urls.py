from django.conf.urls.defaults import *

#FNA: used for relative paths for static files during development - should not be used in production!
import sys

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.conf import settings

urlpatterns = patterns('',
    
    # pyamf gateway, flash remoting
    # http://pyamf.org/wiki/DjangoHowto
    (r'^gateway/', 'ourstories_django.gateway.gateway.mainGateway'),

    # to hurry update of all drop.io test feeds
    (r'^hurry/', 'ourstories_django.storyfeed.views.hurry'),
    
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),
    (r'^comments/', include('django.contrib.comments.urls')),

    # Serve the OurStories URLs on root; change this to "^stories/" or whatever to use app prefix (see commented line)
    (r'', include('ourstories_django.ourstories.urls')),
    #(r'^stories/', include('ourstories_django.ourstories.urls')),

    #FNA: Included the following to allow the django development server to serve static files;
    # replace this with something safer on a production deployment (also remove import sys statment)
#    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': sys.path[0]+'/static'}),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT }),

)
