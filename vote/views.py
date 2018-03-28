from .forms import CompetitionForm, ParticipateForm, SignupForm, UserForm
from .forms import ProfileForm, LiteralParticipateForm, VideoParticipateForm
from django.contrib.auth.forms import PasswordChangeForm
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.utils import timezone
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from vote.models import Competition, Participate, Vote, Profile, LITERAL, VIDEO
from hitcount.views import HitCountDetailView
from hitcount.models import HitCount
from hitcount.views import HitCountMixin
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage

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
    """Все конкурсы в статусе 'опубликован'"""
    competitions = Competition.objects.filter(
        status=2
    ).annotate(
        count_vote=Count('competition_participates__participate_votes')
    ). annotate(
        count_participate=Count('competition_participates', distinct=True)
    )
    return render(request, "vote/competitions.html", {'competitions': competitions})


@login_required
def competition_add(request):
    """Создание конкурса"""
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
    """Редактирование конкурса"""
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
            update = Competition.objects.filter(id=competition_id).exclude(status=2).update(
                title=competition.title,
                comp_type=competition.comp_type,
                rules=competition.rules,
                short_description=competition.short_description,
                expiry_date=competition.expiry_date,
                survey_date=competition.survey_date,
                status=competition.status,
                publish_date=competition.publish_date)
            if update:
                messages.add_message(request, messages.SUCCESS,
                                     'Конкурс %s изменен, ожидайте проверки администратором' % competition.title)
            else:
                messages.add_message(request, messages.SUCCESS,
                                     'При изменении конкурса %s произошла ошибка' % competition.title)
            return redirect('profile_vote')
    else:
        competition = get_object_or_404(Competition, id=competition_id)
        form = CompetitionForm(instance=competition)
    return render(request, "vote/competition_edit.html", {'form': form})


@login_required
def competition_delete(request, competition_id):
    """Удаление конкурса, если у него статус - не опубликован"""
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
    """Удаление заявки на конкурс, если у нее статус - не опубликована"""
    participate = get_object_or_404(Participate, id=participate_id)
    if request.user in {participate.competition_id.creator, participate.creator} and participate.status != 2:
        participate.delete()
        messages.add_message(request, messages.SUCCESS,
                             'Заявка %s на конкурс %s удалена'
                             % (participate.title, participate.competition_id.title))
    else:
        messages.add_message(request, messages.WARNING,
                             'Нет прав на удаление, либо заявка %s уже опубликована'
                             % participate.title)
    return redirect('profile_vote')


def about_competition(request, competition_id):
    """Информация о конкурсе"""
    competition = get_object_or_404(Competition, id=competition_id)
    return render(request, "vote/about_competition.html", {'competition': competition})


def about_participate(request, participate_id):
    """Информация о заявке"""
    participate = get_object_or_404(Participate, id=participate_id)

    add_member = vote_open = False

    if participate.competition_id.status == 2:
        exp_date = participate.competition_id.expiry_date
        surv_date = participate.competition_id.survey_date

        if exp_date and surv_date:
            if timezone.now() < surv_date < exp_date:
                add_member = True

            if surv_date < timezone.now() < exp_date:
                vote_open = True

    return render(request, PARTICIPATE_VIEW[participate.competition_id.comp_type],
                  {'participate': participate, 'competition': participate.competition_id,
                   'add_member': add_member, 'vote_open': vote_open})


@login_required
def participate_add(request):
    """Создать заявку на участие в конкурсе"""
    competition_id = request.GET.get('competition_id', 0)
    competition = get_object_or_404(Competition, id=competition_id)

    if competition.comp_type == LITERAL:
        CustomForm = LiteralParticipateForm
    elif competition.comp_type == VIDEO:
        CustomForm = VideoParticipateForm
    else:
        CustomForm = ParticipateForm

    if request.method == "POST":
        form = CustomForm(request.POST, request.FILES)
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
        form = CustomForm()
    return render(request, "vote/participate_add.html", {'form': form, 'competition': competition})


@login_required
def participate_edit(request):
    """Редактрировать завяку"""
    participate_id = request.GET.get('participate_id', 0)
    participate = get_object_or_404(Participate, id=participate_id)
    competition = get_object_or_404(Competition, id=participate.competition_id_id)

    if competition.comp_type == LITERAL:
        CustomForm = LiteralParticipateForm
    elif competition.comp_type == VIDEO:
        CustomForm = VideoParticipateForm
    else:
        CustomForm = ParticipateForm

    if request.user not in [participate.creator, competition.creator]:
        raise Http404
    if request.method == "POST":
        form = CustomForm(request.POST, request.FILES)
        if form.is_valid():
            participate = form.save(commit=False)
            participate.competition_id = competition
            participate.parent = competition
            participate.status = 0
            participate.publish_date = timezone.now()
            participate.creator = request.user
            update = Participate.objects.filter(id=participate_id).exclude(status=2).update(
                title=participate.title,
                comment=participate.comment,
                content=participate.content,
                status=participate.status,
                publish_date=participate.publish_date)
            if update:
                messages.add_message(request, messages.SUCCESS,
                                     'Заявка %s изменена, ожидайте проверки администратором' % competition.title)
            return redirect('profile')
    else:
        participate = get_object_or_404(Participate, id=participate_id)
        form = CustomForm(instance=participate)
    return render(request, "vote/participate_edit.html", {'form': form, 'competition': competition})


@login_required
def vote(request, participate_id):
    """Отдать голос за участника, если еще не голосовал"""
    if request.is_ajax():
        participate = get_object_or_404(Participate, id=participate_id)
        try:
            Vote.objects.create(user=request.user,
                                participate=participate)
        except IntegrityError:
            message = 'DONE'
        else:
            message = 'OK'
        return HttpResponse(message)


def participates_in_competition(request):
    """Все опубликованные заявки на участие в конкурсе,
    с id конкурса равным competition_id"""
    competition_id = request.GET.get('competition_id', 0)
    competition = get_object_or_404(Competition, id=competition_id)

    add_member = vote_open = False

    if competition.status == 2:
        exp_date = competition.expiry_date
        surv_date = competition.survey_date

        if exp_date and surv_date:
            if exp_date > timezone.now() < surv_date:
                add_member = True

            if exp_date > timezone.now() > surv_date:
                vote_open = True

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
    context = {'participates': participates, 'add_member': add_member,
               'competition': competition, 'competition_form': competition_form,
               'vote_open': vote_open}
    return render(request, "vote/participates.html", context)


@login_required
def participate_manage(request):
    """Все заявки в конкурсе, созданном текущим пользователем"""
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
@transaction.atomic
def profile(request):
    if request.method == "POST":
        user_form = UserForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = request.user

            user_temp = user_form.save(commit=False)
            profile_temp = profile_form.save(commit=False)

            user.first_name = user_temp.first_name
            user.last_name = user_temp.last_name
            user.email = user_temp.email

            user.profile.location = profile_temp.location
            user.profile.phone = profile_temp.phone
            user.profile.birth_date = profile_temp.birth_date
            user.save()

            messages.add_message(request, messages.SUCCESS,
                                 'Изменения успешно сохранены')
            return redirect('profile')
        else:
            messages.add_message(request, messages.WARNING,
                                 'Проверьте корректность данных!')
            return redirect('profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
        competitions = Competition.objects.filter(creator=request.user).all()
        participates = Participate.objects.filter(creator=request.user).all()
        context = {'user_form': user_form, 'profile_form': profile_form,
               'participates': participates, 'competitions': competitions}
    return render(request, "accounts/profile.html", context)


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Активация аккаунта на сайте Конкурсы'
            message = render_to_string('registration/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            messages.add_message(request, messages.SUCCESS,
                                'На Ваш email отправлено письмо! '
                                'Перейдите по ссылке и Ваш аккаунт активируется.')
            return redirect("/")
    else:
        form = SignupForm()
    return render(request, 'vote/registration/signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.add_message(request, messages.SUCCESS,
                             'Аккаунт активирован! Теперь Вы можете войти.')
        redirect("/")
    else:
        messages.add_message(request, messages.WARNING,
                             'Ваша ссылка активации недействительна!')
        redirect("/")


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Важно!
            messages.success(request, 'Ваш пароль успешно обновлен!')
            return redirect('change_password')
        else:
            pass
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})

