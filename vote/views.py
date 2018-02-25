from .forms import CompetitionForm, ParticipateForm, UserRegistrationForm, ProfileForm
from django import forms
from django.http import Http404, HttpResponseRedirect
from django.utils import timezone
from django.db import IntegrityError
from django.db.models import Count
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from vote.models import Competition, Participate, Vote, Profile
from hitcount.views import HitCountDetailView
from hitcount.models import HitCount
from hitcount.views import HitCountMixin


class PostCountHitDetailView(HitCountDetailView):
    model = Competition
    count_hit = True


def competition_list(request):
    competitions_list = Competition.objects. \
        annotate(count_vote=Count('competition_participates__participate_votes')). \
        annotate(count_participate=Count('competition_participates', distinct=True)) # .\
        # values('hit_count', 'title', 'status', 'count_participate', 'count_vote')
    paginator = Paginator(competitions_list, 5)

    page = request.GET.get('page')
    try:
        competitions = paginator.page(page)
    except PageNotAnInteger:
        competitions = paginator.page(1)
    except EmptyPage:
        competitions = page.page(paginator.num_pages)
    return render(request, "vote/competition.html", {'competitions': competitions})


@login_required(login_url="vote/registration/login.html")
def competition_add(request):
    competition_id = request.GET.get('competition_id', None)
    if request.method == "POST":
        form = CompetitionForm(request.POST)
        if form.is_valid():
            competition = form.save(commit=False)
            competition.status = 0
            competition.publish_date = timezone.now()
            competition.creator = request.user
            if competition_id:
                try:
                    competition_edit = Competition.objects.get(id=competition_id)
                    if competition_edit.creator != request.user or competition_edit.status == 2:
                        raise Http404
                    competition_edit.title = competition.title
                    competition_edit.comp_type = competition.comp_type
                    competition_edit.rules = competition.rules
                    competition_edit.short_description = competition.short_description
                    competition_edit.expiry_date = competition.expiry_date
                    competition_edit.survey_date = competition.survey_date
                    competition_edit.status = competition.status
                    competition_edit.publish_date = competition.publish_date
                    competition_edit.save()
                    messages.add_message(request, messages.INFO,
                                         'Конкурс %s изменен, ожидайте проверки администратором' % competition.title)
                    return redirect('profile_vote')
                except Competition.DoesNotExist:
                    Http404
            else:
                competition.save()
                messages.add_message(request, messages.INFO,
                                     'Конкурс %s создан, ожидайте проверки администратором' % competition.title)
                return redirect('competitions')
    if competition_id:
        try:
            competition = Competition.objects.get(id=competition_id)
        except Competition.DoesNotExist:
            Http404
        form = CompetitionForm(instance=competition)
    else:
        form = CompetitionForm()
    return render(request, "vote/competition_add.html", {'form': form})


def about_participate(request):
    participate = request.GET.get('participate', None)
    try:
        participate = Participate.objects.get(title=participate)
    except Participate.DoesNotExist:
        raise Http404
    competition = participate.competition_id
    return render(request, "vote/about_participate.html", {'participate': participate, 'competition': competition})


@login_required(login_url="vote/registration/login.html")
def participate_add(request):
    participate_id = request.GET.get('participate_id', None)
    competition_id = request.GET.get('competition_id', None)
    try:
        competition = Competition.objects.get(id=competition_id)
    except Competition.DoesNotExist:
        raise Http404

    if request.user.is_authenticated:
        if request.method == "POST":
            form = ParticipateForm(request.POST, request.FILES)
            if form.is_valid():
                participate = form.save(commit=False)
                participate.competition_id = competition
                participate.parent = competition
                participate.status = 0
                participate.publish_date = timezone.now()
                participate.creator = request.user
                if participate_id:
                    try:
                        participate_edit = Participate.objects.get(id=participate_id)
                        if participate_edit.creator != request.user or participate_edit.status == 2:
                            raise Http404
                        participate_edit.title = participate.title
                        participate_edit.comment = participate.comment
                        participate_edit.content = participate.content
                        participate_edit.status = participate.status
                        participate_edit.publish_date = participate.publish_date
                        participate_edit.save()
                        messages.add_message(request, messages.INFO,
                                             'Заявка %s изменена, ожидайте проверки администратором' % competition.title)
                        return redirect('profile_vote')
                    except Competition.DoesNotExist:
                        Http404
                else:
                    participate.save()
                    messages.add_message(request, messages.INFO,
                                         'Заявка %s создана, ожидайте проверки администратором' % competition.title)
                    return redirect('competitions')
        else:

            if participate_id:
                try:
                    participate = Participate.objects.get(id=participate_id)
                except Participate.DoesNotExist:
                    Http404
                form = ParticipateForm(instance=participate)
            else:
                form = ParticipateForm()
            return render(request, "vote/participate_add.html", {'form': form, 'competition': competition})
    else:
        return render(request, "vote/registration/login.html")


def participates_in_competition(request):
    competition_id = request.GET.get('competition_id', None)
    if request.user.is_authenticated:
        participate = request.GET.get('vote', None)
        if participate:
            vote = Vote()
            vote.user = request.user
            try:
                vote.participate = Participate.objects.get(id=participate)
            except Participate.DoesNotExist:
                raise 404
            try:
                vote.save()
            except IntegrityError:
                messages.add_message(request, messages.INFO, 'Вы уже голосовали за %s' % vote.participate.title)
    try:
        competition = Competition.objects.get(id=competition_id)
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

    participates_list = competition.competition_participates.all()
    paginator = Paginator(participates_list, 5)
    page = request.GET.get('page')
    try:
        participates = paginator.page(page)
    except PageNotAnInteger:
        participates = paginator.page(1)
    except EmptyPage:
        participates = page.page(paginator.num_pages)

    hit_count = HitCount.objects.get_for_object(competition)
    hit_count_response = HitCountMixin.hit_count(request, hit_count)
    return render(request, "vote/participate.html", {'participates': participates, 'add_member': add_member,
                                                     'competition': competition, 'vote_open': vote_open})


@login_required(login_url="vote/registration/login.html")
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = Profile.objects.get(user=request.user)
            profile_temp = form.save(commit=False)
            profile.location = profile_temp.location
            profile.phone = profile_temp.phone
            profile.birth_date = profile_temp.birth_date
            profile.save()
            messages.add_message(request, messages.INFO, 'Изменения успешно сохранены')
            return render(request, 'accounts/profile.html',
                          {'form': form})
    else:
        form = ProfileForm(instance=Profile.objects.get(user=request.user))
    competitions = Competition.objects.filter(creator=request.user).all()
    participates = Participate.objects.filter(creator=request.user).all()
    return render(request, "accounts/profile.html", {'form': form,
                                                     'competitions': competitions,
                                                     'participates': participates})


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
