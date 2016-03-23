from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from .models import Review, Game
from .forms import ReviewForm
import datetime

def review_list(request):
    latest_review_list = Review.objects.order_by('-pub_date')[:9]
    context = {'latest_review_list':latest_review_list}
    return render(request, 'review_list.html', context)


def review_detail(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    return render(request, 'review_detail.html', {'review': review})


def game_list(request):
    game_list = Game.objects.order_by('-name')
    context = {'game_list':game_list}
    return render(request, 'game_list.html', context)


def game_detail(request, wine_id):
    game = get_object_or_404(Game, pk=game_id)
    form = ReviewForm()
    return render(request, 'game_detail.html', {'game': game, 'form': form})

def add_review(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    form = ReviewForm(request.POST)
    if form.is_valid():
        rating = form.cleaned_data['rating']
        comment = form.cleaned_data['comment']
        user_name = request.user.username
        review = Review()
        review.game = game
        review.user_name = user_name
        review.rating = rating
        review.comment = comment
        review.pub_date = datetime.datetime.now()
        review.save()
        """Always return an HttpResponseRedirect after successfully dealing
        with POST data. This prevents data from being posted twice if a
        user hits the Back button."""
        return HttpResponseRedirect(reverse('reviews:game_detail', args=(game.id,)))

    return render(request, 'game_detail.html', {'game': game, 'form': form})
