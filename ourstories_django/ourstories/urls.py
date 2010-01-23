from django.conf.urls.defaults import *
import django.views.generic.list_detail

from ourstories.models import Story

info_dict = {
    'queryset': Story.objects.all(),
}

urlpatterns = patterns('ourstories_django.ourstories',
    # Web page URLs
    (r'^$', 'views.index'),
    
    url(r'^story/(?P<story_id>\d+)/$', 'views.story_view', name="story-view"),
    url(r'^story/feed/(?P<feed_type>sms|ivr)/(?P<feeditem_id>\d+)/$', 'views.story_view_by_feeditem_id', name="story-view-by-feeditem-id"),

    # after story id created, upload a file or record a video
    url(r'^story/upload/$', 'views.story_upload', name="story-upload"),
    url(r'^story/record/$', 'views.story_record', name="story-record"),
    url(r'^story/record/(?P<flv_id>\d+)/(?P<mod_sig>[A-Za-z0-9,]+)/$', 
        'views.story_record_form', name="story-record-form"),
    

    url(r'^story/(?P<story_id>\d+)/link_flv/(?P<mod_sig>[A-Za-z0-9,]+)/$', 
        'views.story_link_flv', name="story-link-flv"),
    url(r'^story/(?P<story_id>\d+)/flag/$', 'views.story_flag', name="story-flag"),

    url(r'^add/$', 'views.story_add', name="story-add"),
    url(r'^add/(?P<postingtype>\w+)/$', 'views.story_add_form', name="story-add-form"),
    (r'^search/$', 'views.search'),
    (r'^language/(?P<languageName>\w+)/$', 'views.listStoriesForLanguage'),
    (r'^category/(?P<categoryName>\w+)/$', 'views.listStoriesForCategory'),
    (r'^contributor/(?P<contributorId>\d+)/$', 'views.listStoriesForContributor'),
    (r'^about/$', 'views.about'),

    url(r'^flags/$', 'views.flag_dashboard', name="flag-dashboard"),
    url(r'^flags/(?P<story_id>\d+)/deflag/$', 'views.flag_story_deflag', name="flag-story-deflag"),
    url(r'^flags/(?P<story_id>\d+)/unpublish/$', 'views.flag_story_unpublish', name="flag-story-unpublish"),
    url(r'^flags/(?P<story_id>\d+)/republish/$', 'views.flag_story_republish', name="flag-story-republish"),
    url(r'^flags/unpublished/$', 'views.flag_unpublished', name="flag-unpublished"),
    
    # Flash applet URLs
    (r'^add/config/languages/(?P<languageName>\w+)/$', 'views_flash.getLanguage'),
    (r'^add/config/languages/$', 'views_flash.listLanguages'),
    (r'^add/config/countries/$', 'views_flash.getCountriesXml'),
    (r'^add/upload/snapshot/$', 'views_flash.uploadSnapshot'),
    (r'^add/upload/image/$', 'views_flash.uploadImageFile'),
    (r'^add/upload/story/$', 'views_flash.uploadStoryXml'),
    (r'^add/image/(?P<imgFilename>.*)/$', 'views_flash.getUploadedImage'), # this is used to retrieve uploaded image files for use in the flash applet 
    
    # JavaScript ajax URLs
    (r'^show/$', 'views_ajax.storiesOnMap'),
    (r'^cities/(?P<country_code>[^/]+)/$', 'views_ajax.cities_for_country'),
)
