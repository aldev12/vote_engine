from django.shortcuts import render, redirect
from vote.models import Competition, Participate, Vote
from django.http import Http404
from .forms import CompetitionForm, ParticipateForm
from django.utils import timezone
from django.db import IntegrityError
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django import forms
from .forms import UserRegistrationForm


def competition_list(request):
    competitions = Competition.objects.all()
    return render(request, "vote/competition.html", {'competitions': competitions})


@login_required
def competition_add(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = CompetitionForm(request.POST)
            if form.is_valid():
                competition = form.save(commit=False)
                competition.status = 1
                competition.publish_date = timezone.now()
                competition.creator = request.user
                try:
                    competition.create_competition()
                except IntegrityError:
                    form.add_error('title', 'Конкурс с таким именем уже существует')
                    return render(request, "vote/competition_add.html", {'form': form})
                return redirect('competitions')
        else:
            form = CompetitionForm()
            return render(request, "vote/competition_add.html", {'form': form})
    else:
        return render(request, "vote/registration/login.html")


def about_participate(request):
    participate = request.GET.get('participate', None)
    try:
        participate = Participate.objects.get(title=participate)
    except Participate.DoesNotExist:
        raise Http404
    competition = participate.competition_id
    return render(request, "vote/about_participate.html", {'participate': participate, 'competition': competition})


@login_required
def participate_add(request):
    competition = request.GET.get('competition', None)
    try:
        competition = Competition.objects.get(title=competition)
    except Competition.DoesNotExist:
        raise Http404

    if request.user.is_authenticated:
        if request.method == "POST":
            form = ParticipateForm(request.POST, request.FILES)
            if form.is_valid():
                participate = form.save(commit=False)
                participate.competition_id = competition
                participate.status = 1
                participate.publish_date = timezone.now()
                participate.creator = request.user
                try:
                    participate.create_participate()
                except IntegrityError:
                    form.add_error('title', 'Заявка на участие с таким именем уже существует')
                    return render(request, "vote/participate_add.html", {'form': form})
                return redirect('competitions')
        else:
            form = ParticipateForm()
            return render(request, "vote/participate_add.html", {'form': form, 'competition': competition})
    else:
        return render(request, "vote/log_in.html")


def participates_in_competition(request):
    message = None
    competition = request.GET.get('competition', None)
    if request.user.is_authenticated:
        participate = request.GET.get('vote', None)
        if participate:
            vote = Vote()
            vote.user = request.user
            try:
                vote.participate = Participate.objects.get(title=participate)
            except Participate.DoesNotExist:
                raise 404
            try:
                vote.save()
            except IntegrityError:
                message = 'Вы уже голосовали за %s' % participate
    try:
        competition = Competition.objects.get(title=competition)
    except Competition.DoesNotExist:
        raise Http404
    try:
        if competition.expiry_date > timezone.now() < competition.survey_date and competition.status == 2:
            add_member = True
        else:
            add_member = False
        if competition.expiry_date > timezone.now() > competition.survey_date and competition.status == 2:
            vote_open = True
        else:
            vote_open = False
    except TypeError:
        add_member = vote_open = False

    participates = competition.competition_participates.all()
    return render(request, "vote/participate.html", {'participates': participates, 'add_member': add_member,
                                                     'competition': competition, 'vote_open': vote_open,
                                                     'message': message})


def log_in(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
    return redirect('competitions')


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user_obj = form.cleaned_data
            username = user_obj['username']
            email = user_obj['email']
            password = user_obj['password']
            if not (User.objects.filter(
                    username=username).exists() or User.objects.filter(
                    email=email).exists()):
                User.objects.create_user(username, email, password)
                user = authenticate(username=username, password=password)
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                raise forms.ValidationError(
                    'Кажется, пользователь стаким именем или почтой уже существует!')
    else:
        form = UserRegistrationForm()

    return render(request, 'vote/registration/register.html', {'form': form})
