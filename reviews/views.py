from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.contrib.auth.models import User
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from reviews.forms import AuthenticateForm, UserCreateForm, MessageForm, ReviewForm
from reviews.models import Message, Review, Game, Recommendation, Discussion, DiscussionComment
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
                      {'message_form': message_form, 'user': user,
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
    obj = zip(users, messages)
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


"""
This method allow user to recommend a game to the followers. THe requirement is
the user1 MUST follow user2 and the user2 MUST follow the user1 to sent the recommendation
"""
def recommendation(request, game_id):
    user = request.user
    game = get_object_or_404(Game, pk=game_id)
    #get the list of the followers
    network = user.profile.followed_by.all
    if 'user' in request.GET:
        recommended_to = get_object_or_404(User, username = request.GET.get('user'))
        recommend = Recommendation.objects.update_or_create(game = game,
                                                            recommended_to = recommended_to,
                                                            recommended_by = request.user)
        return render(request, 'recommend_success.html', {'game': game, 'user': recommended_to})
    return render(request, 'recommend.html', {'game': game, 'networks': networks})


"""
Open a discussion to selected follower list. The follower invited will see the discussion in game discussion list
"""
def open_discussion(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    user = request.user
    networks = user.profile.followed_by.all()
    if 'question' in request.GET and 'invited' in request.GET:
        discussion = Discussion(game=game)
        discussion.user = request.user
        discussion.question = request.GET['question']
        discussion.save()
        # get the invited list
        invited = request.GET.getlist('invited')
        # iterate through the invited list and add the user's to discussion's invited_user
        for i in invited:
            u = get_object_or_404(User, username=i)
            discussion.invited_user.add(u)
        return HttpResponse('discussion created successfully')
    return render(request, 'opendiscussion.html', {'networks': networks, 'game': game})

"""
If a user is invited in a games discussions he will see the list
"""
def discussions(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    u = request.user
    discussions = u.invited.filter(game=game)
    return render(request, 'discussions_list.html', {'game': game, 'discussions': discussions})

"""
The invited user can comment on the game discussion if the discussion is not closed
if the logged in user is creator of discussion he will see a link to close the discussion.
and the invited user will not see the comment box
"""
def discussion_detail(request, discussion_id):
    discussion = get_object_or_404(Discussion, pk=discussion_id)
    if 'close' in request.GET:
        close = request.GET['close']
        if close == str(1):
            discussion.closed = True
            discussion.save()
    day = date.today() - timedelta(7)
    if day == discussion.creation_date:
        discussion.closed = True
        discussion.save()
    comments = DiscussionComment.objects.filter(discussion=discussion)
    form = DiscussionCommentForm()
    return render(request, 'discussion_detail.html', {'discussion': discussion, 'comments': comments, 'form': form})

def add_comment(request, discussion_id):
    discussion = get_object_or_404(Discussion, pk=discussion_id)
    form = DiscussionCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.discussion = discussion
        comment.user = request.user
        comment.save()
        return HttpResponseRedirect(reverse('discussion_detail', args=(discussion.id,)))

    return render(request, 'discussion_detail.html', {'discussion': discussion, 'form': form})


def user_discussions_list(request):
    discussions = Discussion.objects.filter(user=request.user)
    return render(request, 'user_discussions_list.html', {'discussions': discussions})
