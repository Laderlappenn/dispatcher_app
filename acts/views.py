from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .models import Act
from .forms import ActForm

@login_required
def acts(request):
    if request.user.type == 'DISPATCHER':
        queryset = Act.objects.select_related('user').all()
    else:
        queryset = Act.objects.select_related('user').filter(user_id=request.user.id) # request.session.get('_auth_user_id')
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'acts/act_list.html', {'page_obj': page_obj})


@login_required
def create_act(request):
    if request.method == 'GET':
        form = ActForm()
        return render(request, 'acts/create_act.html', {'form': form})

    elif request.method == 'POST':
        form = ActForm(request.POST, request.FILES)
        if form.is_valid():
            user = request.user.id
            form.instance.user_id = user
            form.save()
            return HttpResponseRedirect('http://127.0.0.1:8000/acts/create')
        else:
            return render(request, 'acts/create_post.html', {'form': form})

@login_required
def act(request, pkey):
    queryset = get_object_or_404(Act, pk=pkey)
    if request.user.type == 'DISPATCHER' or request.user.id == queryset.user_id:
        return render(request, 'acts/act.html', {'act': queryset})
    else:
        return render(request, 'no_access.html')


def act_search(request):
    if request.user.type == 'DISPATCHER':
        if request.method == 'POST':
            # any orm injections?
            search = request.POST['search']
            acts = Act.objects.all()
            queryset = [act for act in acts if (
                        (search.lower() in act.title.lower())
                        or
                        (search.lower() in act.adress.lower())
                        or
                        (search.lower() in act.text.lower()))
                        ]
            return render(request,'acts/details/act-search.html', {'status': queryset})

def return_act(request, actid):
    if request.user.is_staff == 1:
        Act.objects.filter(id=actid).update(act_processing='Заявка возвращена')

        return render(request, 'dispatcher/details/return-detail.html')

def accept_act(request, actid):
    if request.user.is_staff == 1:
        Act.objects.filter(id=actid).update(act_processing='Заявки принята')
        return render(request, 'dispatcher/details/accept-detail.html')

def set_date(request, actid):
    if request.user.is_staff == 1:
        if request.method == 'GET':
            queryset = Act.objects.filter(id=actid).values_list('do_until', flat=True).first()

            form = ActSetDateForm()#instance=queryset
            return render(request, 'dispatcher/forms/date-form.html', {'form': form,'act':actid, 'date':queryset})
        if request.method == 'PUT':
            # optimize query
            queryset = get_object_or_404(Act, id=actid)
            data = QueryDict(request.body).dict()
            form = ActSetDateForm(data, instance=queryset)
            if form.is_valid():
                form.save()

        return render(request, 'dispatcher/details/accept-detail.html')