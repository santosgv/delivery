
from django.shortcuts import render
from produto.models import Unidade
from django.contrib import messages
from django.contrib.messages import constants


def search(request):
    return render(request,'particials/htmx_componenntes/aviso.html')


