from django.shortcuts import render, redirect
from vote.models import Competition, Participate, COMPETITION_TYPE
from django.http import Http404
from .forms import CompetitionForm, ParticipateForm
from django.utils import timezone


def competition_list(request):
    competitions = Competition.objects.all()
    return render(request, "vote/competition.html", {'competitions': competitions,
                                                     'COMPETITION_TYPE': dict(COMPETITION_TYPE)})


def competition_add(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = CompetitionForm(request.POST)
            if form.is_valid():
                competition = form.save(commit=False)
                competition.status = 1
                competition.publish_date = timezone.now()
                competition.save()
                return redirect('competitions')
        else:
            form = CompetitionForm()
            return render(request, "vote/competition_add.html", {'form': form})
    else:
        return render(request, "vote/log_in.html")


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
                participate.competition_p = competition
                participate.status = 1
                participate.publish_date = timezone.now()
                participate.save()
                return redirect('competitions')
        else:
            form = ParticipateForm()
            return render(request, "vote/participate_add.html", {'form': form, 'competition': competition})
    else:
        return render(request, "vote/log_in.html")


def participates_in_competition(request):
    competition = request.GET.get('competition', None)
    try:
        competition = Competition.objects.get(title=competition)
    except Competition.DoesNotExist:
        raise Http404
    try:
        if competition.expiry_date > timezone.now() < competition.Survey_date and competition.status == 2:
            add_member = True
        else:
            add_member = False
        if competition.expiry_date > timezone.now() > competition.Survey_date and competition.status == 2:
            vote_open = True
        else:
            vote_open = False
    except TypeError:
        add_member = vote_open = False

    participates = competition.participates_competition.all()
    return render(request, "vote/participate.html", {'participates': participates, 'add_member': add_member,
                                                     'competition': competition, 'vote_open': vote_open})

