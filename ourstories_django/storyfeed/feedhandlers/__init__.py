"""
XML Feed handlers for OurStories.

Each format of feed has its own handler class.  They use the
storyfeed.models.Feed and FeedItem model classes, as well as
ourstories.models.Story.

"""

import urllib
from xml.dom import minidom
from datetime import datetime
import time
try:
	import email.utils as emailutils
except:
	import email26.utils as emailutils

from ourstories.models import Story, Country, Contributor


def parse_time(timereceived):
    try:
        return datetime.strptime(timereceived,
                                 "%Y%m%d%H%M%S")
    except ValueError:
        return datetime.now()


def get_country(countryname):
    try:
        countryObj = Country.objects.get(name=countryname)
    except Country.DoesNotExist:
        countryObj=None

    return countryObj


def get_or_create_contrib(msisdn):

    if not msisdn:
        return None

    try:
        c = Contributor.objects.get(msisdn=msisdn)
        return c

    except Contributor.DoesNotExist:
        if msisdn == "test":
            contrib_name = "Test Contributor"
        else:
            contrib_name = "%s..." % (str(msisdn)[:3],)

        c = Contributor(name=contrib_name,
                        msisdn=msisdn)
        c.save()
        return c


class XMLFeedHandlerBase(object):
    def __init__(self, feed):
        self.feed = feed

    def update(self):
        print "LOG: Called update on %s" % str(self)

        data = urllib.urlopen(self.feed.feed_url).read().lstrip()
        fetchtime = datetime.now()

        doc = minidom.parseString(data)

        result = self._process_xmldoc(doc)

        if result: # updated successfully
            self.feed.last_updated = fetchtime
            self.feed.save()

        return result # true indicates actually updated; false means no update needed

    def _process_xmldoc(self, doc):
        raise RuntimeError("You're supposed to override _process_xmldoc in subclasses!")



class PraekeltSMSHandler(XMLFeedHandlerBase):
    def _process_xmldoc(self, doc):
        from storyfeed.models import FeedItem

        for smselt in doc.getElementsByTagName("sms"):
            uniqueid = None
            msisdn = None
            message = None
            country = None
            timereceived = None

            for child in ( elt for elt in smselt.childNodes if elt.nodeType == minidom.Node.ELEMENT_NODE):
                nodename = child.nodeName
                innerText = None
                if child.firstChild:
                    innerText = child.firstChild.data.strip()

                if nodename == u'uniqueid':
                    uniqueid = innerText
                elif nodename == u'msisdn':
                    msisdn = innerText
                elif nodename == u'message':
                    message = innerText
                elif nodename == u'country':
                    country = innerText
                elif nodename == u'timereceived':
                    timereceived = innerText

            if uniqueid and msisdn and message and country and timereceived:
                print "GOOD === SMS ======================="
                print uniqueid
                print msisdn
                print repr(message)
                print country
                print timereceived
                print "===================================="

                fi,created = FeedItem.objects.get_or_create(
                    feed=self.feed,
                    feed_item_id="sms:%s" % uniqueid)

                if created:
                    # new entry -- save the story
                    ##import pdb;pdb.set_trace()
                    s = Story(title="",
                              storytype="text",
                              is_published=True,
                              summary=message,
                              contributor=get_or_create_contrib(msisdn),
                              country=get_country(country),
                              created=parse_time(timereceived))
                    s.save()
                    fi.story = s
                    fi.save()

                    print "Created FeedItem %r" % fi

            else:
                print "WARNING: Skipping malformed SMS feed entry: %s" % smselt.toxml()

        return True # indicates successful update



class PraekeltIVRHandler(XMLFeedHandlerBase):
    def _process_xmldoc(self, doc):
        from storyfeed.models import FeedItem

        for smselt in doc.getElementsByTagName("sms"):
            uniqueid = None
            wav_uri = None
            mp3_uri = None
            country = None
            timereceived = None
            msisdn = None # not currently in feed but may appear in future

            for child in ( elt for elt in smselt.childNodes if elt.nodeType == minidom.Node.ELEMENT_NODE):
                nodename = child.nodeName
                innerText = None
                if child.firstChild:
                    innerText = child.firstChild.data.strip()

                if nodename == u'uniqueid':
                    uniqueid = innerText
                elif nodename == u'msisdn':
                    msisdn = innerText
                elif nodename == u'wav':
                    wav_uri = innerText
                elif nodename == u'mp3':
                    mp3_uri = innerText
                elif nodename == u'country':
                    country = innerText
                elif nodename == u'timereceived':
                    timereceived = innerText

            message_uri = mp3_uri or wav_uri

            if uniqueid and message_uri and country and timereceived:
                print "GOOD === IVR ======================="
                print uniqueid
                print repr(msisdn)
                print message_uri
                print country
                print timereceived
                print "===================================="

                fi,created = FeedItem.objects.get_or_create(
                    feed=self.feed,
                    feed_item_id="ivr:%s" % uniqueid)

                if created:
                    # new entry -- save the story
                    s = Story(title="",
                              storytype="audio",
                              media_type=Story.MEDIA_MP3,
                              is_published=True,
                              link=message_uri,
                              contributor=get_or_create_contrib(msisdn),
                              country=get_country(country),
                              created=parse_time(timereceived))
                    s.save()
                    fi.story = s
                    fi.save()

                    print "Created FeedItem %r" % fi

            else:
                print "WARNING: Skipping malformed IVR feed entry: %s" % smselt.toxml()

        return True # indicates successful update


class DropioRssIVRHandler(XMLFeedHandlerBase):
    def _process_xmldoc(self, doc):
        from storyfeed.models import FeedItem

        for rssitem in doc.getElementsByTagName("item"):
            guid = None
            title = None
            enclosure = None
            pubDate = None

            for child in ( elt for elt in rssitem.childNodes if elt.nodeType == minidom.Node.ELEMENT_NODE):
                nodename = child.nodeName
                innerText = None
                if child.firstChild:
                    innerText = child.firstChild.data.strip()

                if nodename == u'guid':
                    guid = innerText
                elif nodename == u'title':
                    title = innerText
                elif nodename == u'pubDate':
                    pubDate = innerText
                elif nodename == u'enclosure':
                    enclosure = child

            if enclosure.getAttribute("type") != "audio/mpeg":
                # only watch for audio/mpeg enclosures!
                continue

            enclosure_url = enclosure.getAttribute("url")

            if guid and title and pubDate and enclosure_url:
                print "GOOD === Drop.io IVR================"
                print guid
                print title
                print repr(enclosure)
                print pubDate
                print "===================================="

                pubdt = datetime.fromtimestamp(emailutils.mktime_tz(emailutils.parsedate_tz(pubDate)))

                fi,created = FeedItem.objects.get_or_create(
                    feed=self.feed,
                    feed_item_id="rss:%s" % guid)

                if created:
                    # new entry -- save the story
                    s = Story(title=title,
                              storytype="audio",
                              media_type=Story.MEDIA_MP3,
                              is_published=True,
                              link=enclosure_url,
                              contributor=get_or_create_contrib("test"),
                              country=get_country("United States"),
                              created=pubdt)
                    s.save()
                    fi.story = s
                    fi.save()

                    print "Created FeedItem %r" % fi

            else:
                print "WARNING: Skipping malformed Drop.io IVR feed entry: %s" % rssitem.toxml()

        return True # indicates successful update
        
