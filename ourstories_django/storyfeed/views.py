# storyfeed.views

from django.http import HttpResponse, Http404, HttpResponseRedirect

from storyfeed.models import Feed

def hurry(request):
    testfeeds = Feed.objects.filter(feed_format="dr_rss")

    updated_count = 0

    for f in testfeeds:
        f.update(force=True)
        updated_count += 1

    return HttpResponse("OK, forced update of %d feed(s)." % updated_count)
