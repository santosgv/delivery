
from django.http import HttpResponse
from django.shortcuts import render
from .models import Produto

def search(request):
    word = request.GET.get('search-input')
    pesquisas = Produto.objects.filter(ativo=True,nome_produto=word)
    return render(request,'particials/htmx_componenntes/search.html',{'produtos':pesquisas})
