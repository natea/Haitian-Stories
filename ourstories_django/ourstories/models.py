from django.db import models
from django.core.urlresolvers import reverse
from hashlib import sha1 as hash_func
import time
from django.conf import settings
from django.utils.text import truncate_words
import re
from django.contrib.auth.models import User

from datetime import datetime

STORYTYPE_CHOICES = (
    ("video", "Video"),
    ("audio", "Audio"),
    ("text", "Text-only story"),
)

STORYTYPE_CHOICES_DICT = dict(STORYTYPE_CHOICES)

STORY_MODIFICATION_SIGNATURE_EXPIRY_INTERVAL = 60*60 # one hour # (in seconds)

class Story(models.Model):
    """ Represents an uploaded story """

    class Meta:
        verbose_name_plural = "Stories"
    
    MEDIA_NONE = ''    
    MEDIA_MP3 = 'mp3'
    MEDIA_FLV_VIDEO = 'flvv'
    MEDIA_FLV_AUDIO = 'flva'
    
    MEDIA_CHOICES = (
        (MEDIA_NONE, 'None'),
        (MEDIA_MP3, 'MP3'),
        (MEDIA_FLV_VIDEO, 'FLV Video'),
        (MEDIA_FLV_AUDIO, 'FLV Audio'),
    )
    
    # Meta information for this story
    title = models.CharField('Title of story', max_length=255, db_index=True, blank=True)
    
    storytype = models.CharField('Media Type', max_length=5, choices=STORYTYPE_CHOICES, db_index=True)

    summary = models.TextField('Summary of story')

    created = models.DateTimeField('Time created') # NOT auto_now_add; see save()
    categories = models.ManyToManyField('Category', related_name='stories', blank=True)

    is_published = models.BooleanField(default=False)
    
    # Content information for this story
    language = models.ForeignKey('Language', verbose_name='content language', related_name='stories', null=True, blank=True)
#    duration = models.IntegerField('Duration of story in seconds', default=None, blank=True, null=True) # null if text story
    link = models.URLField(null=True, blank=True, verify_exists=False) # link to the video
    # http://youtube.com/v/as943Fj
    # flv:123

    # Contributor information for this story
    contributor = models.ForeignKey('Contributor', related_name='stories', null=True, blank=True)
    
    # Location information for this story
    city = models.ForeignKey('City', related_name='stories', null=True, blank=True)
    country = models.ForeignKey('Country', related_name='stories', null=True, blank=True)

    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    # whether story has flva, flvv, mp3 or none
    # useful in templates to render flowplayer for flvv, for example
    # link field has flv:123 id
    media_type = models.CharField(max_length=50, blank=True, 
        default=MEDIA_NONE, choices=MEDIA_CHOICES)
    
    # flv:123 doesn't indicate whether flv is flvv or flva
    def has_flv(self):
        if self.link and re.search(r'^flv:\d+$', self.link):
            return True
        return False

    
    def flv_id(self):
        if self.has_flv():
            return int(self.link.split(':',1)[1]) # extract from flv:123
        else:
            return -1
    
    
    def __unicode__(self):
        if self.id is None:
            return '<Story: (unsaved; no ID) %s>' % self.make_title()
        return self.make_title()

    def get_modification_signature(self, expiry_delay=STORY_MODIFICATION_SIGNATURE_EXPIRY_INTERVAL):
        expiry_time = int(time.time()) + expiry_delay

        assert self.id, "Cannot generate signature for an unsaved story."

        plaintext = ':'.join([settings.SECRET_KEY,
                              str(expiry_time),
                              str(self.id)])
        return "%d,%s" % (expiry_time, hash_func(plaintext).hexdigest())


    def test_modification_signature(self, sig):
        """Tests a putative mod-signature for this object, retuning True iff
        it is valid."""
        
        parts = str(sig).split(",")

        if len(parts) != 2:
            return False

        expiry_time = parts[0]
        sigdigest = parts[1]

        if int(expiry_time) < time.time():
            return False
        
        plaintext = ':'.join([settings.SECRET_KEY,
                              str(expiry_time),
                              str(self.id)])
        
        return hash_func(plaintext).hexdigest() == sigdigest

    def make_title(self):
        """Get or generate a reasonable title for this story."""
        if self.title:
            return self.title

        elif self.summary:
            return truncate_words(self.summary, 6)

        else:
            return "%s story" % self.storytype_verbose()
        

    def storytype_verbose(self):
        return STORYTYPE_CHOICES_DICT.get(self.storytype)

    def get_absolute_url(self):
        return reverse("story-view", kwargs={"story_id":self.id})

    def save(self, force_insert=False, force_update=False):
        if not(self.latitude) and self.city:
            self.latitude = self.city.latitude
            self.longitude = self.city.longitude

        if not(self.latitude) and self.country:
            big_cities = self.country.cities.order_by("-population")[:1]

            if len(big_cities):
                self.latitude = big_cities[0].latitude
                self.longitude = big_cities[0].longitude

        if not self.created:
            self.created = datetime.now()


        super(Story, self).save(force_insert, force_update) # Call the "real" save() method.
        


class Category(models.Model):
    """ Represents a story category (aka tag) """
    class Meta:
        verbose_name_plural = "Categories"

    name = models.CharField(max_length=40, primary_key=True)
    def __unicode__(self):
        return '<Category: %s>' % self.name



class Contributor(models.Model):
    """ Represents a user that contributes (i.e. uploads) a story """
    name = models.CharField(max_length=255, db_index=True)
    msisdn = models.CharField(max_length=25, unique=True, editable=False, null=True, blank=True, verbose_name="Praekelt-supplied user identifier / phone number; currently used only to group multiple SMSes from a single person.")
    email = models.EmailField(null=True, blank=True)
    age = models.SmallIntegerField(null=True, blank=True, db_index=True)
    gender = models.CharField(max_length=1, choices=(('M', 'Male'), ('F', 'Female')))
    #image = models.ImageField(null=True, blank=True, upload_to=contributorImageFilename) #FNA: We use Picasa for storing images; no use in declaring an ImageField
    imageRef = models.URLField(default='/static/images/no_photo.jpg')
    
    def __unicode__(self):
        if self.id == None:
            return '<Contributor: (unsaved; no ID) %s>' % self.name
        return '<Contributor: (%d) %s>' % (self.id, self.name)



# These functions are defined here because they need to be accessible at compile-time by the Language class
def flashLocalizationFilename(instance, filename):
    """ Called by the Language.flashLocalization FileField to determine the upload_to path """
    return 'localizations/flash/%s.xml' % instance.name

def djangoLocalizationFilename(instance, filename):
    """ Called by the Language.flashLocalization FileField to determine the upload_to path """
    return 'localizations/flash/%s.xml' % instance.name

class Language(models.Model):
    """ Represents a language; stories are associated with these
    
    They are also used for localization of the Flash app and site.
    """     
    name = models.CharField(max_length=155)
    flashLocalization = models.FileField('Flash applet localization file (.xml)', upload_to=flashLocalizationFilename, blank=True)
    djangoLocalization = models.FileField('Django site localization file (.po)', upload_to=djangoLocalizationFilename, blank=True)
    
    def __unicode__(self):
        return '<Language: %s>' % self.name


class City(models.Model):
    """ Represents a city; stories are associated with these, and may use lat/long information
    from the closest city if the story lacks its own unique values """
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Cities"
        
    name = models.CharField(max_length=155, db_index=True)
    country = models.ForeignKey('Country', related_name='cities')
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    population = models.IntegerField(null=True)
    
    def __unicode__(self):
        if self.id == None:
            return '[City: (unsaved; no ID) %s]' % self.name
        return '[City: (%d) %s]' % (self.id, self.name)


class Country(models.Model):
    """ Represents a country; stories and cities are associated with these """
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Countries"

    isocode = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=40)
    continent = models.CharField(max_length=2)
    
    def __unicode__(self):
        return '<Country: %s>' % self.name



class StoryFlag(models.Model):
    """A flag placed by any user on a story, indicating that the story
    requires administrative review."""

    class Meta:
        ordering = ['-created']
        permissions = (
            ("can_review_flags", "Can review flags"),
            )

    story = models.ForeignKey('Story')
    
    # null until reviewed
    reviewed_by = models.ForeignKey(User, blank=True, null=True)
    
    created = models.DateTimeField('Time created', auto_now_add=True)
    modified = models.DateTimeField('Time modified', auto_now=True)

    flagger_ip = models.IPAddressField('Flag Creator IP Address')

    
    def __unicode__(self):
        rev = ("reviewed by %s" % self.reviewed_by.username) if self.reviewed_by else "UNREVIEWED"

        return "[%s] flag on %s from %s" % (
            rev,
            self.story.make_title(),
            self.flagger_ip)
    


    @classmethod
    def create(cls, story, request, commit=True):
        """Create a new flag on the given story, as initiated in the given request."""
        f = cls(story=story,
                flagger_ip=request.META.get("REMOTE_ADDR"))
        
        if commit:
            f.save()

        return f

