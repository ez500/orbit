from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def settings(request):
    context = dict()
    context['title'] = "Settings"

    # TODO SETUP HYPERLINK TO PROFILE EDIT
    return render(request, "settings/index.html", context)
