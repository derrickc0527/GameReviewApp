"""GameReviewApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^$', 'reviews.views.index'),
    url(r'^login$', 'reviews.views.login_view'),
    url(r'^logout$', 'reviews.views.logout_view'),
    url(r'^signup$', 'reviews.views.signup'),
    url(r'^ribbits$', 'reviews.views.public'),
    url(r'^submit$', 'reviews.views.submit'),
    url(r'^users/$', 'reviews.views.users'),
    url(r'^users/(?P<username>\w{0,30})/$', 'reviews.views.users', name='user'),
    url(r'^follow$', 'reviews.views.follow'),
    #url(r'^reviews$', 'ribbit_app.reviews.follow'),
    #review
    url(r'^review/(?P<review_id>[0-9]+)/$', 'reviews.views.review_detail', name='review_detail'),
    url(r'^game$', 'reviews.views.game_list', name='game_list'),
    url(r'^game/(?P<game_id>[0-9]+)/$', 'reviews.views.game_detail', name='game_detail'),
    url(r'^game/(?P<game_id>[0-9]+)/add_review/$', 'reviews.views.add_review', name='add_review'),
    url(r'^review/user/(?P<user>\w+)/$', 'reviews.views.user_review_list', name='user_review_list'),
    url(r'^review/user/$', 'reviews.views.user_review_list', name='user_review_list'),
    url(r'^game/recommend/(?P<game_id>\d+)/$', 'reviews.views.recommendation', name='recommendtion'),
    url(r'^game/opendiscussion/(?P<game_id>\d+)/$', 'reviews.views.open_discussion', name='open_discussion'),
    url(r'^game/discussions/(?P<game_id>\d+)/', 'reviews.views.discussions', name='discussions'),
    url(r'^discussion/(?P<discussion_id>\d+)', 'reviews.views.discussion_detail', name='discussion_detail'),
    url(r'^discussion/add_comment/(?P<discussion_id>\d+)', 'reviews.views.add_comment', name='add_comment'),
    url(r'^user_discussions_list/$', 'reviews.views.user_discussions_list', name='user_discussions_list'),
    # url(r'^ribbit/', include('ribbit.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/', admin.site.urls),

]
