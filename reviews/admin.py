from django.contrib import admin
from .models import Game, Review, Recommendation, Discussion
# Register your models here.

class ReviewAdmin(admin.ModelAdmin):
    model = Review
    list_display = ('game', 'rating', 'user_name', 'comment', 'pub_date')
    list_filter = ['pub_date', 'user_name']
    search_fields = ['comment']


admin.site.register(Game)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Recommendation)
admin.site.register(Discussion)
