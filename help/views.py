from django.shortcuts import render

def account_help(request):
    return render(request, "accounts_help.html")

def company_help(request):
    return render(request, "company_help.html")

def task_help(request):
    return render(request, "task_help.html")