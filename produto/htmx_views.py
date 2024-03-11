
from django.http import HttpResponse
from django.shortcuts import render
from pedido.models import CupomDesconto


def search(request):
    return render(request,'particials/htmx_componenntes/aviso.html')
