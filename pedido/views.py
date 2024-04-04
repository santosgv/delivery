
import json
from django.views.decorators.cache import cache_page
from django.shortcuts import redirect, render
from django.http import HttpResponse
from .models import Pedido, ItemPedido, CupomDesconto
from produto.views import get_status,get_all_produtos,get_categorias_com_contagem
from produto.models import Produto, Categoria,Bairro,Bairro
from django.contrib.messages import constants
from django.contrib import messages
from django.db import transaction
from django.core.cache import cache
from django.db.models import Count
import datetime
import logging

logger = logging.getLogger('Aplicacao')

def get_categorias_com_contagem():
    cached_categorias = cache.get('all_categorias_com_contagem')
    if cached_categorias is None:
        categorias = Categoria.objects.annotate(quantidade=Count('produto')).values('id', 'categoria', 'quantidade')
        cached_categorias = [{'id': cat['id'], 'categoria': cat['categoria'], 'quantidade': cat['quantidade']} for cat in categorias]
        cache.set('all_categorias_com_contagem', cached_categorias, timeout=1800)
    return cached_categorias

@transaction.atomic
def finalizar_pedido(request):
    status = get_status()
    if request.method == "GET":
        categorias = get_categorias_com_contagem()
        bairros = Bairro.objects.all()
        total = sum([float(i['preco']) for i in request.session['carrinho']])
        return render(request, 'finalizar_pedido.html', {'carrinho': len(request.session['carrinho']),
                                                         'categorias': categorias,
                                                         'total': total,
                                                         'bairros':bairros,
                                                         'status':status,
                                                         })
    else:
        if len(request.session['carrinho']) > 0:
            x = request.POST
            total = sum([float(i['preco']) for i in request.session['carrinho']])
            cupom = CupomDesconto.objects.filter(codigo=x['cupom'])
            cupom_salvar = None
            if len(cupom) > 0 and cupom[0].ativo:
                total = total - ((total * cupom[0].desconto) / 100)
                cupom[0].usos += 1
                cupom[0].save()
                cupom_salvar = cupom[0]

            carrinho = request.session.get('carrinho')
            listaCarrinho = []
            for i in carrinho:
                listaCarrinho.append({
                    'produto': Produto.objects.filter(id=i['id_produto'])[0],
                    'observacoes': i['observacoes'],
                    'preco': i['preco'],
                    'adicionais': i['adicionais'],
                    'quantidade': i['quantidade'],
                })

            lambda_func_troco = lambda x: int(x['troco_para']) - total if not x['troco_para'] == '' else ""
            lambda_func_pagamento = lambda x: 'Cartão' if x['meio_pagamento'] == '2' else 'Dinheiro'
            pedido = Pedido(usuario=x['nome'],
                            total=total,
                            troco=lambda_func_troco(x),
                            cupom=cupom_salvar,
                            pagamento=lambda_func_pagamento(x),
                            ponto_referencia=x['pt_referencia'],
                            cep=x['cep'],
                            rua=x['rua'],
                            numero=x['numero'],
                            bairro=Bairro.objects.get(id=x['bairro']),
                            telefone=x['telefone'],
                            )
            pedido.save()

            ItemPedido.objects.bulk_create(
                ItemPedido(
                    pedido=pedido,
                    produto=v['produto'],
                    quantidade=v['quantidade'],
                    preco=v['preco'],
                    descricao=v['observacoes'],
                    adicionais=str(v['adicionais'])
                ) for v in listaCarrinho

            )

            request.session['carrinho'].clear()
            request.session.save()
            return render(request, 'pedido_realizado.html')
        else:
            logger.warning(f'Escolha ao menos um produto antes de efetuar a compra!'+str(datetime.datetime.now())+' horas!')
            messages.add_message(request, constants.ERROR, 'Escolha ao menos um produto antes de efetuar a compra!')
            return redirect('/pedidofinalizar_pedido/')


@cache_page(60 * 100)
@transaction.atomic
def validaCupom(request):
    data = json.loads(request.body)
    codigo = data.get('cupom')
    cupom = CupomDesconto.objects.filter(codigo = codigo)
    if len(cupom) > 0 and cupom[0].ativo:
        desconto = cupom[0].desconto
        total = sum([float(i['preco']) for i in request.session['carrinho']])
        total_com_desconto = total - ((total*desconto)/100)
        data_json = json.dumps({'status': 0,
                                'desconto': desconto,
                                'total_com_desconto': str(total_com_desconto).replace('.', ',')

                                })
     
        return HttpResponse(data_json)
    else:
        logger.critical(f'erro ao validar o cupom'+str(datetime.datetime.now())+' horas!')
        return HttpResponse(json.dumps({'status': 1}))


@cache_page(60 * 100)
@transaction.atomic
def freteBairro(request):
    data = json.loads(request.body)
    id_bairro = data.get('bairro')
    if id_bairro !='0':
        bairro = Bairro.objects.get(id=id_bairro)
        data_json =json.dumps({'status': 0,
                                        'frete': bairro.Frete,
                                        })
        return HttpResponse(data_json)
    else:
        logger.critical(f'erro ao validar o bairro'+str(datetime.datetime.now())+' horas!')
        return HttpResponse(json.dumps({'status': 1}))

def novo(request):
    produtos = get_all_produtos()
    categorias = get_categorias_com_contagem()
    return render(request,'novo_html',{'produtos':produtos,
                                       'categorias': categorias,
                                       })