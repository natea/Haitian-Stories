from django.core.management.base import BaseCommand

from storyfeed.models import Feed, FeedItem

class Command(BaseCommand):
    def handle(self, *args_dummy, **kwargs_dummy):
        print "Updating OurStories feeds..."

        feedcounter = 0

        for feed in Feed.objects.filter(is_active=True):
            feedcounter += 1
            print " - feed %s... " % str(feed.id)

            was_updated = feed.update()

            print " - feed %s " % str(feed.id),
            if was_updated:
                print "updated OK."
            else:
                print "already up to date."

        print "Found and attempted update of %d feed(s)." % feedcounter
