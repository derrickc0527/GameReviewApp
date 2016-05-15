from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.contrib.auth.models import User
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from reviews.forms import AuthenticateForm, UserCreateForm, MessageForm, ReviewForm
from reviews.models import Message, Review, Game
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import datetime


def index(request, auth_form=None, user_form=None):
    # User is logged in
    if request.user.is_authenticated():
        message_form = MessageForm()
        user = request.user
        messages_self = Message.objects.filter(user=user.id)
        messages_buddies = Message.objects.filter(user__userprofile__in=user.profile.follows.all)
        messages = messages_self | messages_buddies

        return render(request,
                      'buddies.html',
                      {'message_form': ribbit_form, 'user': user,
                       'messages': messages,
                       'next_url': '/', })
    else:
        # User is not logged in
        auth_form = auth_form or AuthenticateForm()
        user_form = user_form or UserCreateForm()

        return render(request,
                      'home.html',
                      {'auth_form': auth_form, 'user_form': user_form, })


def login_view(request):
    if request.method == 'POST':
        form = AuthenticateForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            # Success
            return redirect('/')
        else:
            # Failure
            return index(request, auth_form=form)
    return redirect('/')


def logout_view(request):
    logout(request)
    return redirect('/')


def signup(request):
    user_form = UserCreateForm(data=request.POST)
    if request.method == 'POST':
        if user_form.is_valid():
            username = user_form
            password = user_form
            user_form.save()
            user = authenticate(username=username, password=password)
            #login(request, user)
            return redirect('/')
        else:
            return index(request, user_form=user_form)
    return redirect('/')


@login_required
def public(request, message_form=None):
    message_form = message_form or MessageForm()
    messages = Message.objects.reverse()[:10]
    return render(request,
                  'public.html',
                  {'message_form': message_form, 'next_url': '/messages',
                   'messages': messages, 'username': request.user.username})


@login_required
def submit(request):
    if request.method == "POST":
        message_form = MessageForm(data=request.POST)
        next_url = request.POST.get("next_url", "/")
        if message_form.is_valid():
            message = message_form.save(commit=False)
            message.user = request.user
            message.save()
            return redirect(next_url)
        else:
            return public(request, message_form)
    return redirect('/')


def get_latest(user):
    try:
        return user.message_set.order_by('id').reverse()[0]
    except IndexError:
        return ""


@login_required
def users(request, username="", message_form=None):
    if username:
        # Show a profile
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404
        messages = Message.objects.filter(user=user.id)
        if username == request.user.username or request.user.profile.follows.filter(user__username=username):
            # Self Profile
            return render(request, 'user.html', {'user': user, 'messages': messages, })
        return render(request, 'user.html', {'user': user, 'messages': messages, 'follow': True, })
    users = User.objects.all().annotate(message_count=Count('message'))
    messages = map(get_latest, users)
    obj = zip(users, ribbits)
    message_form = message_form or MessageForm()
    return render(request,
                  'profiles.html',
                  {'obj': obj, 'next_url': '/users/',
                   'message_form': message_form,
                   'username': request.user.username, })

@login_required
def follow(request):
    if request.method == "POST":
        follow_id = request.POST.get('follow', False)
        if follow_id:
            try:
                user = User.objects.get(id=follow_id)
                request.user.profile.follows.add(user.profile)
            except ObjectDoesNotExist:
                return redirect('/users/')
    return redirect('/users/')


def review_list(request):
    latest_review_list = Review.objects.order_by('-pub_date')[:9]
    context = {'latest_review_list':latest_review_list}
    return render(request, 'review_list.html', context)


def review_detail(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    return render(request, 'review_detail.html', {'review': review})


def game_list(request):
    game_list = Game.objects.order_by('-name')
    query = request.GET.get("keyword")
    if query:
        game_list = game_list.filter(name__icontains=query)
    context = {'game_list':game_list}
    return render(request, 'game_list.html', context)


def game_detail(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    form = ReviewForm()
    return render(request, 'game_detail.html', {'game': game, 'form': form})

@login_required
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
        return HttpResponseRedirect(reverse('game_detail', args=(game.id,)))

    return render(request, 'game_detail.html', {'game': game, 'form': form})

def user_review_list(request, username=None):
    if not username:
        username = request.user.username
    latest_review_list = Review.objects.filter(user_name=username).order_by('-pub_date')
    context = {'latest_review_list':latest_review_list, 'username':username}
    return render(request, 'user_review_list.html', context)
