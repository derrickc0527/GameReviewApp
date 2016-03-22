from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.review_list, name='review_list'),
    url(r'^review/(?P<review_id>[0-9]+)/$', views.review_detail, name='review_detail'),
    url(r'^game$', views.game_list, name='game_list'),
    url(r'^game/(?P<wine_id>[0-9]+)/$', views.game_detail, name='game_detail'),
    url(r'^game/(?P<wine_id>[0-9]+)/add_review/$', views.add_review, name='add_review'),


]
