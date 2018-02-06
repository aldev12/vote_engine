from django.shortcuts import render, redirect
from vote.models import Competition, Participate
from django.http import Http404
from .forms import CompetitionForm
from django.utils import timezone


def competition_list(request):
    competitions = Competition.objects.all()
    return render(request, "vote/competition.html", {'competitions': competitions})


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


def participates_in_competition(request):
    competition = request.GET.get('competition', None)
    try:
        competition = Competition.objects.get(title=competition)
    except Competition.DoesNotExist:
        raise Http404
    participates = competition.participates_competition.all()
    return render(request, "vote/participate.html", {'participates': participates})

