""" admin.py
Sets up Django's automatic admin interface for the storyfeed application
"""

from storyfeed.models import Feed, FeedItem
from django.contrib import admin


class FeedAdmin(admin.ModelAdmin):
    list_display = ("feed_url", "id", "is_active", "feed_format", "last_updated")
admin.site.register(Feed, FeedAdmin)

class FeedItemAdmin(admin.ModelAdmin):
    list_display = ("feed_item_id", "feed", "created")
admin.site.register(FeedItem, FeedItemAdmin)

