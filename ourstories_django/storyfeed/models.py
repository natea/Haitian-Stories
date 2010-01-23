from django.db import models

from storyfeed.feedhandlers import PraekeltSMSHandler, PraekeltIVRHandler, DropioRssIVRHandler

from datetime import datetime,timedelta
from django.conf import settings

# min. how long after last_updated should we update a feed?
FEED_UPDATE_INTERVAL = timedelta(0, settings.FEED_UPDATE_INTERVAL) # days, seconds, ...

FEED_FORMATS_AND_HANDLERS = (

    dict(code='pk_sms',
         desc="Prakelet SMS XML format (txt)",
         handler=PraekeltSMSHandler),

    dict(code='pk_ivr',
         desc="Prakelet IVR XML format (wmv)",
         handler=PraekeltIVRHandler),

    dict(code='dr_rss',
         desc="Drop.io RSS Test Feed (mp3)",
         handler=DropioRssIVRHandler),

)

FEED_HANDLERS_BY_CODE = dict([(x["code"], x["handler"]) for x in FEED_FORMATS_AND_HANDLERS ])

class Feed(models.Model):
    feed_url = models.CharField('Feed URL', unique=True, max_length=1000)
    feed_format = models.CharField(max_length=6, choices=[
            (x["code"], x["desc"]) for x in FEED_FORMATS_AND_HANDLERS ])
    created = models.DateTimeField('Time created', auto_now_add=True)
    is_active = models.BooleanField(default=True)

    most_recent_id = models.CharField(max_length=255, blank=True) # freeform max ID/timestamp/whatever
    last_updated = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return u"[Feed #%s: %s]" % (unicode(getattr(self, "id", None)),
                                    self.feed_url)

    def update(self, force=False):
        """Update this feed, if necessary.
        Returns True if feed was updated, False if no update was needed,
        or raises an Exception if something went wrong."""

        if self.last_updated and not(force):
            age = datetime.now() - self.last_updated
            if age < FEED_UPDATE_INTERVAL:
                return False # nothing to do

        Handler = FEED_HANDLERS_BY_CODE.get(self.feed_format)

        if not Handler:
            raise RuntimeError("No known FeedHandler for feed format %s" % self.feed_format)

        h = Handler(self)
        return h.update()


class FeedItem(models.Model):
    feed = models.ForeignKey(Feed)
    created = models.DateTimeField('Time created', auto_now_add=True)
    story = models.ForeignKey('ourstories.Story', null=True, blank=True)
    feed_item_id = models.CharField(max_length=255, unique=True) # freeform permalink/UUID/whatever uniquely identifies this story


### FOR TEST DATA, run:
# ./manage.py loaddata storyfeed/fixtures/test_data.yaml
