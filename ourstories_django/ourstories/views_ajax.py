""" views_ajax.py 
This module contains views that implement AJAX-style callbacks via JSON (used mostly by client-side Javascript sections of the site);
they are separated from the main views.py for clarity.
Also see views_flash.py for callbacks that exist specifically for use by the Flash applet.
"""

from decimal import Decimal
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from django.template import RequestContext

from ourstories.json import JsonResponse
from ourstories import models

def storiesOnMap(request):
    """ Retrieves stories that are visible on the map, given the parameters in the request,
    and returns a JSON list containing an dictionary/map for every story that should be updated.
    This is used by the embedded Google Map to create and display interactive story markers """
    requestDict = request.POST
    zoom = int(requestDict['zoom'])
    north = Decimal(requestDict['north'])
    south = Decimal(requestDict['south'])
    east = Decimal(requestDict['east'])
    west = Decimal(requestDict['west'])
    # The "old" parameter contains a commma-separated list of story ids that are already displayed by the browser
    currentlyDisplayedStoryIds = requestDict['old'].split(',')

    storiesToDisplay = models.Story.objects.filter(latitude__range=(south, north)).filter(longitude__range=(west, east)).order_by('-created')

    # Filter the amount of story markers to display based on the current zoom level
    if len(storiesToDisplay) >= (zoom-1)*5:
        storiesToDisplay = storiesToDisplay[(zoom-1)*5:zoom*5]

    response = []
    for story in storiesToDisplay:
        if str(story.id) not in currentlyDisplayedStoryIds:

            if story.contributor:
		contribName = story.contributor.name
            else: 
                contribName = None
            langName = story.language.name if story.language else None
            response.append({'id': story.id,
                             'title': story.title,
                             'summary': story.summary,
                             'link': story.link,
                             'has_flv':story.has_flv(),
                             'flv_id':story.flv_id(),
                             'media_type':story.media_type,
                             'imageRef': story.contributor.imageRef,
                             'contributor': contribName,
                             'language': langName,
                             'created': story.created.strftime('%d %B %Y'),
                             'lat': float(story.latitude),
                             'long': float(story.longitude)})
    return JsonResponse(response)



def cities_for_country(request, country_code):

    return HttpResponse("\n".join([ ("<option value='%s'>%s</option>" % (ci.id, ci.name)) for ci in models.City.objects.filter(country=country_code).order_by('name') ]))
