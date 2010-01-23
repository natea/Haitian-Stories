from ourstories_django.flv.models import Flv
from django.conf import settings
from ourstories_django.ourstories.models import Story
from ourstories_django.ourstories.forms import sign_value, check_signed_value

def ping(request):
    '''Pings PyAMF gateway service.'''

    if settings.DEBUG:
        print 'ping pong'    
    
    return 'pong'


def get_id(request):
    '''Creates a new Flv and returns its id.  Intended for Flash Flv recorder.'''
    
    flv = Flv() # default status is STATUS_PENDING
    flv.save()
    
    if settings.DEBUG:
        print 'get_id flv_id:%s' % flv.id    

    return flv.id


def get_id_sig(request):
    '''Creates a new Flv and returns its id, along with the sig for recording
    first then submitting form.  Intended for Flash Flv recorder.'''
    
    flv = Flv() # default status is STATUS_PENDING
    flv.save() # need to get id
    
    sig = sign_value(flv.id)
    flv.sig = sig
    flv.save()
    
    if settings.DEBUG:
        print 'get_id_sig flv_id:%s sig:%s' % (flv.id, sig)    

    return {'id':flv.id, 'sig':sig}
    

def set_status(request, flv_id, status):
    '''Sets the recording status of an Flv'''
    
    if settings.DEBUG:
        print 'set_status flv_id:%s status:%s' % (flv_id, status)
        
    if status in Flv.STATUS_TYPES:
        try:
            flv = Flv.objects.get(id=flv_id)
            flv.status = status
            flv.save()
            return True
        except:
            return False
    else:
        return False
    

def set_status_type(request, flv_id, status, media_type):
    '''Sets the recording status and media type of an Flv'''
    
    if settings.DEBUG:
        print 'set_status flv_id:%s status:%s media_type:%s' % (flv_id, status, media_type)
        
    if status in Flv.STATUS_TYPES:
        try:
            flv = Flv.objects.get(id=flv_id)
            flv.status = status
            flv.media_type = media_type
            flv.save()
            return True
        except:
            return False
    else:
        return False
    

def link_flv_to_story(request, flv_id, story_id, media_type):
    '''Links an Flv to a Story, saves media_type from Flash/Flex recorder'''
    
    if settings.DEBUG:
        print 'link_flv_to_story flv_id:%s story_id:%s media_type:%s' % (
            flv_id, story_id, media_type)
        
    try:
        story = Story.objects.get(id=story_id)
        story.link = 'flv:%s' % flv_id
        story.media_type = media_type
        
        if media_type == 'flvv':
            story.storytype = 'video'
        if media_type == 'flva':
            story.storytype = 'audio'
        

        story.is_published = True

        story.save()
        return True
    except:
        return False
    

def dtrace(request, message):
    '''Traces message, DEBUG only'''

    if settings.DEBUG:
        print 'dtrace: %s' % message
    return True
    
    
    
