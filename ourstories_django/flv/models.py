from django.db import models
import datetime
from django.conf import settings
import os

class FlvManager(models.Manager):

    def recorded(self):
        return self.filter(status=Flv.STATUS_RECORDED)
    def fail(self):
        return self.filter(status=Flv.STATUS_FAIL)
    def pending(self):
        return self.filter(status=Flv.STATUS_PENDING)
    

class Flv(models.Model):
    
    STATUS_RECORDED = 1
    STATUS_FAIL = 0
    STATUS_PENDING = 2
    
    STATUS_TYPES = (STATUS_RECORDED, STATUS_FAIL, STATUS_PENDING,)
    STATUS_CHOICES = (
        (STATUS_RECORDED, 'Recorded'), 
        (STATUS_FAIL, 'Fail'),
        (STATUS_PENDING, 'Pending'),
    )

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
        
    status = models.SmallIntegerField(default=STATUS_PENDING, 
        choices=STATUS_CHOICES)
    media_type = models.CharField(blank=True, max_length=50, default=MEDIA_NONE, 
        choices=MEDIA_CHOICES)
    
    sig = models.CharField(blank=True, max_length=500)
    
    created = models.DateTimeField(editable=False)
    updated = models.DateTimeField(editable=False)
    
    # TODO filepath not currently used, necessary?
    filepath = models.FilePathField(path=os.path.join(settings.MEDIA_ROOT,'flv'), 
        match='^\d+.flv$', recursive=True, null=True, blank=True, editable=False)
    
    objects = FlvManager()
    
    def __unicode__(self):
        if not self.id:
            return '<Flv: (unsaved; no ID)>'
        return '<Flv: %s>' % self.id
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.datetime.now()
        self.updated = datetime.datetime.now()
        super(Flv, self).save(*args, **kwargs)  
      
