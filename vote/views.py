from .forms import CompetitionForm, ParticipateForm, UserRegistrationForm, ProfileForm
from django.contrib.auth.forms import PasswordChangeForm
from django import forms
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.utils import timezone
from django.db import IntegrityError
from django.db.models import Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from vote.models import Competition, Participate, Vote, Profile
from hitcount.views import HitCountDetailView
from hitcount.models import HitCount
from hitcount.views import HitCountMixin

CONTENT_COUNT_IN_PAGE = 5

PARTICIPATE_VIEW = {
    1: 'vote/participate/photo.html',
    2: 'vote/participate/liter.html',
    3: 'vote/participate/video.html',
    4: 'vote/participate/audio.html'
}


class PostCountHitDetailView(HitCountDetailView):
    model = Competition
    count_hit = True


def competition_list(request):
    competitions_list = Competition.objects.filter(status=2). \
        annotate(count_vote=Count('competition_participates__participate_votes')). \
        annotate(count_participate=Count('competition_participates', distinct=True)) # .\
        # values('Participate_name', 'title', 'status', 'count_participate', 'count_vote')
    paginator = Paginator(competitions_list, CONTENT_COUNT_IN_PAGE)
    page = request.GET.get('page')
    try:
        competitions = paginator.page(page)
    except PageNotAnInteger:
        competitions = paginator.page(1)
    except EmptyPage:
        competitions = page.page(paginator.num_pages)
    return render(request, "vote/competitions.html", {'competitions': competitions})


@login_required
def competition_add(request):
    if request.method == "POST":
        form = CompetitionForm(request.POST)
        if form.is_valid():
            competition = form.save(commit=False)
            competition.status = 0
            competition.publish_date = timezone.now()
            competition.creator = request.user
            competition.save()
            messages.add_message(request, messages.SUCCESS,
                                 'Конкурс %s создан, ожидайте проверки администратором' % competition.title)
            return redirect('competitions')
    else:
        form = CompetitionForm()
    return render(request, "vote/competition_add.html", {'form': form})


@login_required
def competition_edit(request):
    competition_id = request.GET.get('competition_id', 0)
    competition = get_object_or_404(Competition, id=competition_id)
    if request.user != competition.creator:
        raise Http404
    if request.method == "POST":
        form = CompetitionForm(request.POST)
        if form.is_valid():
            competition = form.save(commit=False)
            competition.status = 0
            competition.publish_date = timezone.now()
            competition.creator = request.user
            if Competition.objects.filter(id=competition_id).exclude(status=2).update(
                    title=competition.title,
                    comp_type=competition.comp_type,
                    rules=competition.rules,
                    short_description=competition.short_description,
                    expiry_date=competition.expiry_date,
                    survey_date=competition.survey_date,
                    status=competition.status,
                    publish_date=competition.publish_date):
                messages.add_message(request, messages.SUCCESS,
                                     'Конкурс %s изменен, ожидайте проверки администратором' % competition.title)
            return redirect('profile_vote')
    else:
        competition = get_object_or_404(Competition, id=competition_id)
        form = CompetitionForm(instance=competition)
    return render(request, "vote/competition_edit.html", {'form': form})


@login_required
def competition_delete(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    if competition.creator == request.user and competition.status != 2:
        competition.delete()
        messages.add_message(request, messages.SUCCESS, 'Конкурс %s удален' % competition.title)
    else:
        messages.add_message(request, messages.WARNING, 'Нет прав на удаление, либо конкурс %s уже опубликован'
                             % competition.title)
    return redirect('profile_vote')


@login_required
def participate_delete(request, participate_id):
    participate = get_object_or_404(Participate, id=participate_id)
    if request.user in {participate.competition_id.creator, participate.creator} and participate.status != 2:
            participate.delete()
            messages.add_message(request, messages.SUCCESS, 'Заявка %s на конкурс %s удалена'
                                 % (participate.title, participate.competition_id.title))
    else:
        messages.add_message(request, messages.WARNING, 'Нет прав на удаление, либо заявка %s уже опубликована'
                             % participate.title)
    return redirect('profile_vote')


def about_competition(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    return render(request, "vote/about_competition.html", {'competition': competition})


def about_participate(request, participate_id):
    participate = get_object_or_404(Participate, id=participate_id)
    return render(request, PARTICIPATE_VIEW[participate.competition_id.comp_type],
                  {'participate': participate, 'competition': participate.competition_id})


@login_required
def participate_add(request):
    competition_id = request.GET.get('competition_id', 0)
    competition = get_object_or_404(Competition, id=competition_id)
    if request.method == "POST":
        form = ParticipateForm(request.POST, request.FILES)
        if form.is_valid():
            participate = form.save(commit=False)
            participate.competition_id = competition
            participate.parent = competition
            participate.status = 0
            participate.publish_date = timezone.now()
            participate.creator = request.user
            participate.save()
            messages.add_message(request, messages.SUCCESS,
                                 'Заявка %s создана, ожидайте проверки администратором' % competition.title)
            return redirect('competitions')
    else:
        form = ParticipateForm()
    if competition.comp_type == 2:
        form.fields['content'].widget = forms.HiddenInput()
    return render(request, "vote/participate_add.html", {'form': form, 'competition': competition})


@login_required
def participate_edit(request):
    participate_id = request.GET.get('participate_id', 0)
    participate = get_object_or_404(Participate, id=participate_id)
    competition = get_object_or_404(Competition, id=participate.competition_id_id)
    if request.user not in [participate.creator, competition.creator]:
        raise Http404
    if request.method == "POST":
        form = ParticipateForm(request.POST, request.FILES)
        if form.is_valid():
            participate = form.save(commit=False)
            participate.competition_id = competition
            participate.parent = competition
            participate.status = 0
            participate.publish_date = timezone.now()
            participate.creator = request.user
            if Participate.objects.filter(id=participate_id).exclude(status=2).update(
                    title=participate.title,
                    comment=participate.comment,
                    content=participate.content,
                    status=participate.status,
                    publish_date=participate.publish_date):
                messages.add_message(request, messages.SUCCESS,
                                     'Заявка %s изменена, ожидайте проверки администратором' % competition.title)
            return redirect('profile_vote')
    else:
        participate = get_object_or_404(Participate, id=participate_id)
        form = ParticipateForm(instance=participate)
    return render(request, "vote/participate_edit.html", {'form': form, 'competition': competition})


@login_required
def vote(request, participate_id):
    if request.is_ajax():
        participate = get_object_or_404(Participate, id=participate_id)
        try:
            Vote.objects.create(user=request.user,
                                participate=participate)
        except IntegrityError:
            message = 'Вы уже голосовали за %s' % participate.title
        else:
            message = 'Вы проголосовали за %s' % participate.title
        return HttpResponse(message)


def participates_in_competition(request):
    competition_id = request.GET.get('competition_id', 0)
    competition = get_object_or_404(Competition, id=competition_id)
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

    participates_list = competition.competition_participates.filter(status=2).all()
    paginator = Paginator(participates_list, CONTENT_COUNT_IN_PAGE)
    page = request.GET.get('page')
    try:
        participates = paginator.page(page)
    except PageNotAnInteger:
        participates = paginator.page(1)
    except EmptyPage:
        participates = page.page(paginator.num_pages)

    hit_count = HitCount.objects.get_for_object(competition)
    HitCountMixin.hit_count(request, hit_count)

    competition_form = CompetitionForm(instance=competition)
    return render(request, "vote/participates.html", {'participates': participates, 'add_member': add_member,
                                                      'competition': competition,
                                                      'competition_form': competition_form, 'vote_open': vote_open})


@login_required
def participate_manage(request):
    competition_id = request.GET.get('competition_id', 0)
    competition = get_object_or_404(Competition, id=competition_id)
    if competition.creator != request.user:
        raise Http404
    participates_list = competition.competition_participates.all()

    paginator = Paginator(participates_list, CONTENT_COUNT_IN_PAGE)
    page = request.GET.get('page')
    try:
        participates = paginator.page(page)
    except PageNotAnInteger:
        participates = paginator.page(1)
    except EmptyPage:
        participates = page.page(paginator.num_pages)

    hit_count = HitCount.objects.get_for_object(competition)
    HitCountMixin.hit_count(request, hit_count)
    return render(request, "vote/participate_manage.html", {'participates': participates, 'competition': competition})


@login_required
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
            messages.add_message(request, messages.SUCCESS, 'Изменения успешно сохранены')
    form = ProfileForm(instance=Profile.objects.get(user=request.user))
    competitions = Competition.objects.filter(creator=request.user).all()
    participates = Participate.objects.filter(creator=request.user).all()
    return render(request, "accounts/profile.html", {'form': form, 'participates': participates,
                                                     'competitions': competitions})


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


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Важно!
            messages.success(request, 'Ваш пароль успешно обновлен!')
            return redirect('change_password')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибку!')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})

