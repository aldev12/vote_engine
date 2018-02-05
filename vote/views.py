from django.shortcuts import render
from vote.models import Competition, Participate
from django.http import Http404


def competition_list(request):
    competitions = Competition.objects.all()
    return render(request, "vote/competition.html", {'competitions': competitions})


def competition_add(request):
    if request.user.is_authenticated:
        return render(request, "vote/competition_add.html")
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

