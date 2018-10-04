from django.shortcuts import render

from website.models import Bluetooth


def index(request):
    entries = Bluetooth.objects.all()[:5]
    return render(request, 'index.html', {'entries': entries})
