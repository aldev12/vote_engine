from mezzanine.pages.page_processors import processor_for
from django.http import HttpResponseRedirect
from .models import Competition
from .forms import CompetitionForm


@processor_for(Competition)
def competition_add(request):
    form = CompetitionForm()
    if request.method == "POST":
        form = CompetitionForm(request.POST)
        if form.is_valid():
            # Form processing goes here.
            redirect = request.path + "?submitted=true"
            return HttpResponseRedirect(redirect)
    return {"form": form}
