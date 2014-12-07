from django.shortcuts import render

# Create your views here.

def eventStatus(request, event):
    return render(request, 'status', {'eventname':event})

def eventCSS(request, event):
    return render(request, "css/{}".format(event.lower()))


def eventLogo(request, event):
    return
