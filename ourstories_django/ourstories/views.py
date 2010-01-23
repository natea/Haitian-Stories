""" views.py
Main django views - all of the view handler functions in this module are used to serve up
actual HTML pages to the user; no ajax-like callbacks are defined here; see views_ajax.py
and views_flash.py for those
"""

from decimal import Decimal
import urllib2, datetime

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from django.template import RequestContext
from django.core.urlresolvers import reverse

from django.contrib.auth.decorators import permission_required

from ourstories import models, forms, youtube
from django.conf import settings
from flv.models import Flv


def index(request):
    """ Renders the home page """

    # Get the 10 most recent stories
    latestStories = models.Story.objects.filter(is_published=True).order_by('-created')[:10]
    detailStories = latestStories[:5]

    citiesWithStories = models.City.objects.distinct().filter(stories__isnull=False)
    countriesWithStories = models.Country.objects.distinct().filter(stories__isnull=False)
    languages = models.Language.objects.all()
    languagesWithStories = models.Language.objects.distinct().filter(stories__isnull=False)
    categories = models.Category.objects.all()

    initLat = -25.43
    initLong = 28.17

    for s in detailStories:
        if s.latitude and s.longitude:
            initLat = s.latitude
            initLong = s.longitude
            break

    return render_to_response('index.html', 
                              {'menuHomeActive': True,
                               'latestStories': latestStories,
                               'detailStories': detailStories,
                               'citiesWithStories': citiesWithStories,
                               'countriesWithStories': countriesWithStories,
                               'languagesWithStories': languagesWithStories,
                               'languages': languages,
                               'storyCount' : models.Story.objects.filter(is_published=True).count(),
                               'categories': categories,
                               'initLat': initLat,
                               'initLong': initLong
                               },
                              RequestContext(request))

def story_view(request, story_id):
    """ Renders a detail page for the story with the specified ID """
    story = get_object_or_404(models.Story, id=story_id)

    if not(story.is_published):

        if not request.user.has_perm("ourstories.can_review_flags"):
            return render_to_response('story_unavailable.html',
                                      { 'story': story },
                                      RequestContext(request))

    if story.contributor:
        otherStories = story.contributor.stories.order_by('-created')[:20] # limit to last 20 stories
        if len(otherStories) <= 1:
            otherStories = None
    else:
        otherStories = None

    return render_to_response('story.html', 
                              {'story': story,
                               'otherStories': otherStories},
                              RequestContext(request))

def story_record(request):
    """Record video or audio to be posted with a story."""
    errors = []
    
    return render_to_response('story_record.html',
                              {'menuAdd2Active': True,
                               #'story': story,
                               'errors': errors,
                              },
                              RequestContext(request))
    
def story_record_form(request, flv_id, mod_sig):
    """After recording, handle form."""
    errors = []
    
    if not forms.check_signed_value(flv_id, mod_sig):
        if settings.DEBUG:
            print "mod_sig fail"
        raise Http404
    
    storytype = "video" # set this later based on flv model
    
    return story_add_form(request, "recvideo", _link="flv:%s" % flv_id,
        _storytype=storytype,)
    
    
    
def story_upload(request):
    """Upload a video file to be posted with a story."""
    errors = []

    if "status" in request.REQUEST:
        # user has been sent back here from youtube with something like:
        #     ?status=200&id=Su4ArLGM8l8
        
        yt_status = request.REQUEST.get("status")
        yt_id = request.REQUEST.get("id")

        if yt_id and yt_status == "200":
            return story_add_form(request, "upload", 
                                  _link="http://www.youtube.com/v/%s&hl=en&fs=1" % yt_id,
                                  _storytype="video")
            
#             story.storytype = "video"
#             story.link = "http://www.youtube.com/v/%s&hl=en&fs=1" % yt_id
#             story.is_published = True
#             story.save()
#             return HttpResponseRedirect(story.get_absolute_url())

        else:
            errors.append("There was an error processing your uploaded file.  The status code is %s.  Please try again." % str(yt_status))


    youtube_upload_url, youtube_upload_token = youtube.getBrowserUploadInfo()

    return render_to_response('story_upload.html', 
                              {'menuAdd2Active': True,
                               #'story': story,
                               'errors': errors,
                               'youtube_upload_url': youtube_upload_url,
                               'youtube_upload_token': youtube_upload_token,
                               },
                              RequestContext(request))
    

def search(request):
    """ Renders input/results page for search operations """
    form = forms.SearchForm(request.GET)
    if form.is_bound and form.is_valid(): # All validation rules pass
        # Process the data in form.cleaned_data
        query = form.cleaned_data['q']
        filterStorytype = form.cleaned_data['storytype']
        filterCategory = form.cleaned_data['category']
        filterLanguage = form.cleaned_data['language']
        filterCountry = form.cleaned_data['country']
        filterGender = form.cleaned_data['gender']
    else:
        form = forms.SearchForm()
        query = request.GET.get('q', '')
        filterStorytype = ''
        filterCategory = ''
        filterLanguage = ''
        filterCountry = ''
        filterGender = ''
        
    qsetList = []
    # Set up the search query
    if query:
        # text search on story tite & contributor name
        qsetList.append( Q(title__icontains=query) | Q(contributor__name__icontains=query) )
    if filterStorytype:
        qsetList.append( Q(storytype=filterStorytype) )
    if filterCategory:
        qsetList.append( Q(categories__name=filterCategory) )
    if filterLanguage:
        qsetList.append( Q(language__name=filterLanguage) )
    if filterCountry:
        qsetList.append( Q(country__name=filterCountry) )
    if filterGender:
        qsetList.append( Q(contributor__gender=filterGender) )
    
    # Perform the search (if required)
    if len(qsetList) > 0:
        allResults = models.Story.objects.filter(is_published=True).filter(*qsetList).distinct() # unpack this list as arguments
        performedSearch = True
    else:
        allResults = []
        performedSearch = False
    
    paginator = Paginator(allResults, 15) # Show a maximum of 15 stories per page
    
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        results = paginator.page(page)
    except (EmptyPage, InvalidPage):
        results = paginator.page(paginator.num_pages)

    # This is used to store the request paramters for the pagination links (bit ugly, but works well)
    paginatorQueryBase = 'q=%s&category=%s&language=%s&country=%s&gender=%s' % (urllib2.quote(query), urllib2.quote(filterCategory), urllib2.quote(filterLanguage), urllib2.quote(filterCountry), urllib2.quote(filterGender))
    
    return render_to_response('search.html', {'menuSearchActive': True,
                                              'results': results,
                                              'query': query,
                                              'form': form,
                                              'performedSearch': performedSearch,
                                              'paginatorQueryBase': paginatorQueryBase})

def listStoriesForLanguage(request, languageName):
    allResults = models.Story.objects.filter(is_published=True).filter(language__name=languageName).distinct()
    return _renderStoriesList(request, allResults, 'language', languageName)
        
def listStoriesForCategory(request, categoryName):
    allResults = models.Story.objects.filter(is_published=True).filter(categories__name=categoryName).distinct()
    return _renderStoriesList(request, allResults, 'category', categoryName)
    
def listStoriesForContributor(request, contributorId):
    try:
        contributor = models.Contributor.objects.get(id=contributorId)
    except models.Contributor.DoesNotExist:
        raise Http404
    else:
        allResults = models.Story.objects.filter(is_published=True).filter(contributor__id=contributorId).distinct()
        return _renderStoriesList(request, allResults, 'contributor', contributor.name)

def _renderStoriesList(request, allResults, listName, listFilterName):
    """ Private function that takes care of rendering & pagination for the list* family of functions, above """
    paginator = Paginator(allResults, 25) # Show a maximum of 25 stories per page
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    # If page request (9999) is out of range, deliver last page of results.
    try:
        results = paginator.page(page)
    except (EmptyPage, InvalidPage):
        results = paginator.page(paginator.num_pages)
    return render_to_response('list.html', {'listName': listName,
                                            'listFilterName': listFilterName,
                                            'results': results})

def about(request):
    """ Renders the "about" page """
    return render_to_response('about.html', {'menuAboutActive': True})


def story_add(request):
    return render_to_response("story_add.html",
                              {'menuAdd2Active': True},
                              RequestContext(request))

def story_add_form(request, postingtype, _link=None, _storytype=None):
    """ Show a form for adding a story.  If _link or _storytype are passed
    in (i.e. this view function is called directly, rather than reached via
    urls.py), they will be used to initialize a form that will create a
    story using those values for its link and storytype fields.  These
    values will be included in the form, but also cryptographically signed
    so that they cannot be forged by a malicious client.
    
    postingtype may be recvideo, upload, or text.
    recvideo is record video and/or audio, depending on options in the Flash recorder swf.
    """

    if postingtype not in ("text", "upload", "recvideo"):
        return HttpResponseRedirect(reverse("story-add"))

    if postingtype == "text":
        _storytype = "text"


    if request.method == "POST":
        form = forms.StoryForm(data=request.POST)
        if form.is_valid():
            story = form.save()
            
            # flv media_type was sent back to django amf at the completion
            # of recording.  now that the story form is done saved created,
            # set the value on the story
            if story.has_flv():
                flv = Flv.objects.get(id=story.flv_id())
                story.media_type = flv.media_type
                if flv.media_type == "flva":
                    story.storytype = "audio"
                if flv.media_type == "flvv":
                    story.storytype = "video"
                story.save()
            
            return HttpResponseRedirect(story.get_absolute_url())

    else: # GET

        if (_link and _storytype) or _storytype=="text":
            form = forms.StoryForm(_link=_link, _storytype=_storytype, )

        else:
            # NOT GOOD ... there should never be a get without a _link or
            # _storytype passed in, except for text stories.
            return HttpResponseRedirect(reverse("story-add"))
        
        
    return render_to_response('story_add_form.html', 
                              {'menuAdd2Active': True,
                               'postingtype': postingtype,
                               'form': form,
                              },
                              RequestContext(request))


#     FormClass = None
#     form = None

#     if postingtype in ("text", "upload", "recvideo"):
#         FormClass = forms.StoryForm

#     if FormClass:
#         if request.method == "POST":
#             form = FormClass(request.POST)
#             if form.is_valid():
                
#                 story = form.save()

#                 nextstep = ""

#                 if postingtype == "upload":
#                     nextstep = "upload/%s/" % story.get_modification_signature()
#                 if postingtype == "recvideo":
#                     nextstep = "link_flv/%s/" % story.get_modification_signature()

#                 if postingtype == "text":
#                     story.is_published = True
#                     story.save()

#                 return HttpResponseRedirect("/story/%d/%s" % (story.id, nextstep))

#         else: # GET
#             form = FormClass()

#     return render_to_response('story_add_form.html', 
#                               {'menuAdd2Active': True,
#                                'postingtype': postingtype,
#                                'form': form,
#                                },
#                               RequestContext(request))



def story_link_flv(request, story_id, mod_sig):
    # verify story id
    story = get_object_or_404(models.Story, pk=story_id)
    # verify mod sig
    if not story.test_modification_signature(mod_sig):
        raise Http404
    
    errors = []
    
    # TODO need to pass story_id into flash
    return render_to_response('story_linkflv.html', 
                              {'story': story,
                               'errors': errors,
                               },
                              RequestContext(request))
    





def story_flag(request, story_id):
    """Asks for confirmation to flag this story, or creates a story flag if confirmed."""

    story = get_object_or_404(models.Story, pk=story_id)

    if request.method == "POST":
        models.StoryFlag.create(story, request)
        return render_to_response("flag/story_flag_done.html",
                                  {"story":story},
                                  RequestContext(request))

    else:
        return render_to_response("flag/story_flag_confirm.html",
                                  {"story":story},
                                  RequestContext(request))

@permission_required("ourstories.can_review_flags")
def flag_dashboard(request):

    flags = models.StoryFlag.objects.filter(reviewed_by__isnull=True)

    story_by_id = {}

    for f in flags:
        s = story_by_id.setdefault(f.story_id, f.story)
        f.story = s
        if not hasattr(s, "flags"):
            s.flags = []
        s.flags.append(f)

    stories = story_by_id.values()
    stories.sort(key=lambda s: len(s.flags), reverse=True)

    return render_to_response("flag/dashboard.html", {
            "flag_count": len(flags),
            "flagged_stories": stories,
            "subnav_section": "flag_dashboard",
            },
                              RequestContext(request))
                              
#    return HttpResponse("User %s can review: %r" % (str(request.user), can_review))

@permission_required("ourstories.can_review_flags")
def flag_story_deflag(request, story_id):
    models.StoryFlag.objects.filter(story=story_id, 
                                    reviewed_by__isnull=True
                                    ).update(reviewed_by=request.user,
                                             modified=datetime.datetime.now())

    return HttpResponseRedirect(reverse("flag-dashboard"))
    

@permission_required("ourstories.can_review_flags")
def flag_story_unpublish(request, story_id):
    story = get_object_or_404(models.Story, pk=story_id)
    models.StoryFlag.objects.filter(story=story_id, 
                                    reviewed_by__isnull=True
                                    ).update(reviewed_by=request.user,
                                             modified=datetime.datetime.now())
    story.is_published = False
    story.save()

    return HttpResponseRedirect(reverse("flag-dashboard"))

@permission_required("ourstories.can_review_flags")
def flag_unpublished(request):
    
    stories = models.Story.objects.filter(is_published=False)

    return render_to_response("flag/unpublished.html", {
            "stories": stories,
            "subnav_section": "unpublished",
            },
                              RequestContext(request))

@permission_required("ourstories.can_review_flags")
def flag_story_republish(request, story_id):
    story = get_object_or_404(models.Story, pk=story_id)
    if not(story.is_published):
        story.is_published = True
        story.save()

    return HttpResponseRedirect(reverse("story-view", kwargs={"story_id": story.id}))


def story_view_by_feeditem_id(request, feed_type, feeditem_id):

    from storyfeed.models import FeedItem

    feeditem = get_object_or_404(FeedItem, feed_item_id="%s:%d" % (
            feed_type, int(feeditem_id)))
    
    return HttpResponseRedirect(reverse("story-view", kwargs={"story_id": feeditem.story_id }))
