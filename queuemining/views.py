from django.shortcuts import render
import random

from django.http import HttpResponse
from . import forms
from.models import Document
from django.template import loader


def importLogs(request):
    random.seed(10)
    if request.method == 'POST':
        form = forms.DocumentForm(request.POST,request.FILES)

        if form.is_valid():
            name = form.cleaned_data['document']
            print(str(name))

            save = form.save()
            id = save.pk
            print(id)
            context = {'form' : form}
        else:
            form = forms.DocumentForm()
            text = "This fileformat is not supported. Please use a CSV or XES file."
            context = {'form' : form, 'text' : text}



    else:
        form = forms.DocumentForm()
        context = {'form' : form}

    template = loader.get_template('main.html')
    return HttpResponse(template.render(context, request))
