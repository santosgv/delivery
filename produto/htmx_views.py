
from django.http import HttpResponse
from django.shortcuts import render
from pedido.models import CupomDesconto


def search(request):
    total = sum([float(i['preco']) for i in request.session['carrinho']])
    get_cupom = request.GET.get('cupom')
    cupoms = CupomDesconto.objects.filter(ativo=True,codigo=get_cupom)
    if len(cupoms) > 0 and cupoms[0].ativo:
        desconto = cupoms[0].desconto
        total = sum([float(i['preco']) for i in request.session['carrinho']])
        total_com_desconto = total - ((total*desconto)/100)
    return render(request,'particials/htmx_componenntes/cupom.html',{'cupoms':cupoms,
                                                                    'total': total,
                                                                    'total_com_desconto':total_com_desconto})
