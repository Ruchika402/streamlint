
from django.contrib import admin

from .models import Review, ReviewSession

admin.site.register(ReviewSession)
admin.site.register(Review)