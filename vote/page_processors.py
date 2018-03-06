from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from mezzanine.pages.page_processors import processor_for
from django.http import HttpResponseRedirect
from mezzanine.utils.views import render

from .models import Participate, Competition
from .forms import CompetitionForm


@processor_for('competition')
def participate_add(request):
    form = CompetitionForm()
    if request.method == "POST":
        form = CompetitionForm(request.POST)
        if form.is_valid():
            # Form processing goes here.
            redirect = request.path + "?submitted=true"
            return HttpResponseRedirect(redirect)
    return {"form": form}


@processor_for('/')
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
