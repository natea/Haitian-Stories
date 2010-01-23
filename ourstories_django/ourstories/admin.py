""" admin.py
Sets up Django's automatic admin interface for the OurStories application
"""

from ourstories_django.ourstories.models import Story, Category, Language, City, Country, Contributor, StoryFlag
from django.contrib import admin

admin.site.register((Story, Contributor, StoryFlag, Category, Language, City, Country))
