from django.shortcuts import render, redirect
from .models import Source, UserIncome
from django.core.paginator import Paginator
from userpreferences.models import UserPreference
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse
import datetime
from django.http import JsonResponse  # Assurez-vous d'importer correctement votre modèle

# Create your views here.


def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        income = UserIncome.objects.filter(
            amount__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            date__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            description__icontains=search_str, owner=request.user) | UserIncome.objects.filter(
            source__icontains=search_str, owner=request.user) | UserIncome.objects.filter(
            nom__icontains=search_str, owner=request.user)
        data = income.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def index(request):
    categories = Source.objects.all()
    income = UserIncome.objects.filter(owner=request.user)
    paginator = Paginator(income, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context = {
        'income': income,
        'page_obj': page_obj,
        'currency': currency
    }
    return render(request, 'income/index.html', context)


@login_required(login_url='/authentication/login')
def add_income(request):
    sources = Source.objects.all()
    context = {
        'sources': sources,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'income/add_income.html', context)

    if request.method == 'POST':
        im = request.POST['im']
        nom = request.POST['nom']
        description = request.POST['description']
        age = request.POST['age']
        date = request.POST['income_date']
        source = request.POST['source']

        if not im:
            messages.error(request, 'IM is required')
            return render(request, 'income/add_income.html', context)

        
        if not description:
            messages.error(request, 'description is required')
            return render(request, 'income/add_income.html', context)
        
        if not nom:
            messages.error(request, 'Name is required')
            return render(request, 'income/add_income.html', context)

        if not age:
            messages.error(request, 'Age is required')
            return render(request, 'income/add_income.html', context)


        UserIncome.objects.create(owner=request.user, date=date,
                                  source=source, description=description, nom=nom, age=age, im=im)
        messages.success(request, 'Record saved successfully')

        return redirect('income')


@login_required(login_url='/authentication/login')
def income_edit(request, id):
    income = UserIncome.objects.get(pk=id)
    sources = Source.objects.all()
    context = {
        'income': income,
        'values': income,
        'sources': sources
    }
    if request.method == 'GET':
        return render(request, 'income/edit_income.html', context)
    if request.method == 'POST':
        description = request.POST['description']
        im = request.POST['im']
        nom = request.POST['nom']
        age = request.POST['age']
        date = request.POST['income_date']
        source = request.POST['source']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'income/edit_income.html', context)
        
        if not im:
            messages.error(request, 'IM is required')
            return render(request, 'income/edit_income.html', context)
        
        if not nom:
            messages.error(request, 'name is required')
            return render(request, 'income/edit_income.html', context)
        if not age:
            messages.error(request, 'age is required')
            return render(request, 'income/edit_income.html', context)
        
        #income.amount = amount
        income. date = date
        income.source = source
        income.description = description
        income.nom = nom
        income.im = im
        income.age = age

        income.save()
        messages.success(request, 'Record updated  successfully')

        return redirect('income')


def delete_income(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request, 'record removed')
    return redirect('income')

def income_source_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date-datetime.timedelta(days=30*6)
    income = UserIncome.objects.filter(owner=request.user,
                                      date__gte=six_months_ago, date__lte=todays_date)
    finalrep = {}

    def get_source(income):
        return income.source
    source_list = list(set(map(get_source, income)))

    def get_income_source_summary(source):
        age = 0
        filtered_by_source = income.filter(source=source)

        for item in filtered_by_source:
            age += item.age
        return age

    for x in income:
        for y in source_list:
            finalrep[y] = get_income_source_summary(y)

    return JsonResponse({'income_source_data': finalrep}, safe=False)



def statist_view(request):
    return render(request, 'income/statist.html')
