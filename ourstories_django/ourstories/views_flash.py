""" views_flash.py 
This module contains views that implement AJAX-style callbacks exclusively for use by the "add story" Flash applet;
they are separated from the main views.py and views_ajax.py for clarity (since the user should never need to call
these views directly).
"""
import os

# Code for testing purposes
if __name__ == '__main__':
    import sys
    sys.path.insert(0, '../..')
    sys.path.insert(0, '..')
    os.environ['DJANGO_SETTINGS_MODULE'] = 'ourstories_django.settings'
# end test code - more below

import datetime
import tempfile
import mimetypes
from xml.dom import minidom

from django.http import HttpResponse, Http404, HttpResponseBadRequest
from django.core.files import File

from ourstories_django.settings import MEDIA_ROOT
from ourstories import models, picasa, video, youtube, storyxml


def listLanguages(request):
    """ Called by the Flash applet to receive a list supported languages
    This is returned in XML format (since it started out as a statically-served XML file)
    """
    # Get all languages that have Flash localizations...
    languages = models.Language.objects.exclude(flashLocalization='')
    # ...and create the XML doc
    xmlDoc = minidom.Document()
    docElement = xmlDoc.createElement('Languages')
    for language in languages:
        element = xmlDoc.createElement('Lang')
        element.appendChild(xmlDoc.createTextNode(language.name))
        docElement.appendChild(element)
    xmlDoc.appendChild(docElement)
    return HttpResponse(xmlDoc.toxml('UTF-8'), mimetype='text/xml')

def getLanguage(request, languageName):
    """ Called by the Flash applet to receive the translation XML doc for the specified language;
    typically this is called after a call to listLanguages()
    """
    try:
        language = models.Language.objects.get(name=languageName)
    except models.Language.DoesNotExist:
        raise Http404
    else:
        f = open(MEDIA_ROOT+language.flashLocalization.url, 'r')
        xmlText = f.read()
        f.close
        return HttpResponse(xmlText, mimetype='text/xml')
    
def getCountriesXml(request):
    """ Called by the Flash applet to receive a list of countries and the cities in them
    This is returned in XML format (since it started out as a statically-served XML file; "countries.xml")
    -- note: see the "create_country_city_db.py" script in the top-level "utils" directory in order to re-create the static countries.xml file
    """
    countries = models.Country.objects.all()
    xmlDoc = minidom.Document()
    docElement = xmlDoc.createElement('countries')
    for country in countries:
        countryElement = xmlDoc.createElement('country')
        countryElement.setAttribute('name', country.name)
        for city in country.cities.all():
            cityElement = xmlDoc.createElement('city')
            cityElement.appendChild(xmlDoc.createTextNode(city.name))
            cityElement.setAttribute('lat', str(city.latitude))
            cityElement.setAttribute('long', str(city.longitude))
            countryElement.appendChild(cityElement)
        docElement.appendChild(countryElement)
    xmlDoc.appendChild(docElement)
    return HttpResponse(xmlDoc.toxml('UTF-8'), mimetype='text/xml')

def uploadSnapshot(request):
    """ Called by the Flash applet to upload a photo of the contributor when adding a story """
    #TODO: actually save the image
    tempFilename = tempfile.mkstemp(prefix='_upload_', suffix='.jpg')[1]
    f = open(tempFilename, 'w')
    f.write(request.raw_post_data)
    f.close()
    return HttpResponse(tempFilename)

def uploadImageFile(request):
    """ Called by the Flash applet to upload a pre-existing image to be used as the contributor's photo
    This is separate from uploadSnapshot because of the differences in POST format between the two requests """
    photo = request.FILES['Filedata'] # photo is a django UploadedFile object
    tempFilename = tempfile.mkstemp(prefix='_upload_', suffix=photo.name[-5:])[1]
    f = open(tempFilename, 'w')
    f.write(photo.read())
    f.close()
    return HttpResponse(tempFilename)

def getUploadedImage(request, imgFilename):
    """ Called by the Flash applet to retrieve an uploaded image file (called after "uploadImageFile", above) """
    if '_upload_' in imgFilename:
        try:
            f = open(imgFilename, 'rb')
            imgData = f.read()
            f.close()
        except IOError:
            raise Http404
        else:
            response = HttpResponse(imgData, mimetype=mimetypes.guess_type(imgFilename)[0])
            response['Content-Disposition'] = 'attachment; filename=%s' % imgFilename
            return response
    else:
        return HttpResponseBadRequest('Invalid query')

def uploadStoryXml(request):
    """ Called by the Flash applet to upload the details about a newly-contributed story as an XML document;
    this is the final step in the Flash-based story upload process """
    print 'in method'
    if request.method == 'POST':
        storyXml = storyxml.StoryXml(minidom.parseString(request.raw_post_data))
        # Get story language
        language = models.Language.objects.get(name=storyXml.language)
        # Get story city
        city = models.City.objects.get(name=storyXml.city, country__name=storyXml.country)
        # Create a video from the uploaded story
        storyVideoFile = video.createVideo(storyXml.imageFilename, storyXml.audioFilename, storyXml.duration)
        # Save the contributor's image on Picasa...
        imageRef = picasa.uploadImage(storyXml.imageFilename, title=storyXml.contributorName, summary='OurStories contributor photo')
        # ...and upload the video to youtube
        videoRef = youtube.uploadVideo(videoFilename=storyVideoFile, title=storyXml.title, description=storyXml.summary, keywords=storyXml.categories, geoLatLongTuple=(float(city.latitude), float(city.longitude)))
        # Set up contributor (or reuse existing one if found)
        #TODO: perhaps make this more like a standard "user login"-type thing; currently done this way because of legacy flash app code
        try:
            contributor = models.Contributor.objects.get(email=storyXml.contributorEmail, name=storyXml.contributorName)
        except models.Contributor.DoesNotExist:
            # not found - create a new user entry
            contributor = models.Contributor(name=storyXml.contributorName,
                                             email=storyXml.contributorEmail,
                                             age=storyXml.contributorAge,
                                             gender=storyXml.contributorGender,
                                             imageRef=imageRef)
        else:
            # update the contributor's details, if necessary
            picasa.deleteImage(contributor.imageRef) # remove the contributor's current image
            contributor.age = storyXml.contributorAge
            contributor.gender = storyXml.contributorGender
            contributor.imageRef = imageRef
        
        contributor.save()
           
        # Create and set up story entry in db
        story = models.Story(title=storyXml.title,
                             summary=storyXml.summary,
                             contributor=contributor,
                             language=language,
                             # geoposition values are saved separate from the origin city/country as well, so that stories may be added to any lat/long in future (and not be locked to city coordinates in our db)
                             city=city,
                             country=city.country,
                             latitude=city.latitude,
                             longitude=city.longitude,
                             link=videoRef,
                             duration=storyXml.duration)
        story.save()
        # Cycle through the sstory's categories, and add category entries as necessary
        for categoryName in storyXml.categories:
            try:
                category = models.Category.objects.get(name=categoryName)
            except models.Category.DoesNotExist:
                # create new category if it does not exist
                category = models.Category(name=categoryName)
                category.save()
            story.categories.add(category)
        story.save()
        return HttpResponse(1)
    else:
        return HttpResponseBadRequest('Stories must be uploaded using POST requests')

# code for testing
if __name__ == '__main__':
    print 'testing story upload'
    f = open('/tmp/xmldump.xml')
    x = f.read()
    f.close()
    class fakeReq(object):
        def __init__(self, r):
            self.raw_post_data = r
            self.method = 'POST'
            
    r = fakeReq(x)
    uploadStoryXml(r)
# end test code
