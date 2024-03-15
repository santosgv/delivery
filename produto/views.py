from django.contrib.messages import constants
from django.http import HttpResponse
import os
from django.shortcuts import render,redirect,get_object_or_404
from django.core.paginator import Paginator
from .models import Produto, Categoria, Opcoes, Adicional,Contato,Email
from django.contrib import messages
from django.db import transaction
from django.views.decorators.cache import cache_page
from django.core.cache import cache
import datetime
from django.db.models import Count
import logging
from django.conf import settings
from django.contrib import sitemaps
from .utils import email_html
import re
from django.contrib.auth.decorators import login_required

logger = logging.getLogger('Aplicacao')


def get_categorias_com_contagem():
    cached_categorias = cache.get('all_categorias_com_contagem')
    if cached_categorias is None:
        categorias = Categoria.objects.annotate(quantidade=Count('produto')).values('id', 'categoria', 'quantidade')
        cached_categorias = [{'id': cat['id'], 'categoria': cat['categoria'], 'quantidade': cat['quantidade']} for cat in categorias]
        cache.set('all_categorias_com_contagem', cached_categorias, timeout=1800)
    return cached_categorias

def home(request):
    categorias = get_categorias_com_contagem()
    if not request.session.get('carrinho'):
        request.session['carrinho'] = []
        request.session.save()
    produtos = Produto.objects.only('nome_produto','img','descricao','preco','descricao','ingredientes','adicionais').filter(ativo=True).all().order_by('-id')
    promos = Produto.objects.only('nome_produto','img','descricao','preco','descricao','ingredientes','adicionais').filter(ativo=True,promocao=True).all().order_by('-id')
    pagina = Paginator(produtos,25)
    pg_number = request.GET.get('page')
    paginas = pagina.get_page(pg_number)
    return render(request, 'home.html', {'produtos': paginas,
                                        'carrinho': len(request.session['carrinho']),
                                        'categorias': categorias,
                                        'promos':promos
                                        })

@cache_page(60 * 100)
def loja(request):
    categorias = get_categorias_com_contagem()
    if not request.session.get('carrinho'):
        request.session['carrinho'] = []
        request.session.save()
    return render(request, 'loja.html', {
                                        'carrinho': len(request.session['carrinho']),
                                        'categorias': categorias,
                                        })

def categorias(request, nome):
    categorias = get_categorias_com_contagem()
    if not request.session.get('carrinho'):
        request.session['carrinho'] = []
        request.session.save()
    categoria_nome = get_object_or_404(Categoria, categoria=nome)
    produtos =Produto.objects.only('nome_produto','img','descricao','preco','descricao','ingredientes','adicionais').filter(ativo=True,categoria=categoria_nome).all().order_by('-id')
    pagina = Paginator(produtos,25)
    pg_number = request.GET.get('page')
    paginas = pagina.get_page(pg_number)

    return render(request, 'home.html', {'produtos': paginas,
                                        'carrinho': len(request.session['carrinho']),
                                        'categorias': categorias,})

def produto(request, id):
    if not request.session.get('carrinho'):
        request.session['carrinho'] = []
        request.session.save()


    produto = Produto.objects.filter(id=id)[0]
    categorias = get_categorias_com_contagem()
    return render(request, 'produto.html', {'produto': produto,
                                            'carrinho': len(request.session['carrinho']),
                                            'categorias': categorias,
                                           })

@transaction.atomic
def add_carrinho(request):
    if not request.session.get('carrinho'):
        request.session['carrinho'] = []
        request.session.save()

    x = dict(request.POST)

    def removeLixo():
        adicionais = x.copy()
        adicionais.pop('id')
        adicionais.pop('csrfmiddlewaretoken')
        adicionais.pop('observacoes')
        adicionais.pop('quantidade')
        adicionais = list(adicionais.items())

        return adicionais

    adicionais = removeLixo()

    id = int(x['id'][0])
    preco_total = Produto.objects.filter(id=id)[0].preco
    adicionais_verifica = Adicional.objects.filter(produto=id)
    aprovado = True

    for i in adicionais_verifica:
        encontrou = False
        minimo = i.minimo
        maximo = i.maximo
        for j in adicionais:
            if i.nome == j[0]:
                encontrou = True
                if len(j[1]) < minimo or len(j[1]) > maximo:
                    aprovado = False
        if minimo > 0 and encontrou == False:
            aprovado = False

    if not aprovado:
        logger.warning(f'Confira a quantidade de adicionais selecionados'+str(datetime.datetime.now())+' horas!')
        messages.add_message(request, constants.ERROR, 'Confira a quantidade de adicionais selecionados')
        return redirect(f'/produto/{id}')

    for i, j in adicionais:
        for k in j:
            preco_total += Opcoes.objects.filter(id=int(k))[0].acrecimo

    def troca_id_por_nome_adicional(adicional):
        adicionais_com_nome = []
        for i in adicionais:
            opcoes = []
            for j in i[1]:
                op = Opcoes.objects.filter(id=int(j))[0].nome
                opcoes.append(op)
            adicionais_com_nome.append((i[0], opcoes))
        return adicionais_com_nome

    adicionais = troca_id_por_nome_adicional(adicionais)

    preco_total *= int(x['quantidade'][0])
    data = {'id_produto': int(x['id'][0]),
            'observacoes': x['observacoes'][0],
            'preco': preco_total,
            'adicionais': adicionais,
            'quantidade': x['quantidade'][0]}

    request.session['carrinho'].append(data)
    request.session.save()

    return redirect(f'/ver_carrinho')


def ver_carrinho(request):
    categorias = Categoria.objects.all()
    dados_motrar = []
    for i in request.session['carrinho']:
        prod = Produto.objects.filter(id=i['id_produto'])
        dados_motrar.append(
            {'imagem': prod[0].img.url,
             'nome': prod[0].nome_produto,
             'quantidade': i['quantidade'],
             'observacoes': i['observacoes'],
             'preco': i['preco'],
             'id': i['id_produto']
             }
        )
    total = sum([float(i['preco']) for i in request.session['carrinho']])

    return render(request, 'carrinho.html', {'dados': dados_motrar,
                                             'total': total,
                                             'carrinho': len(request.session['carrinho']),
                                             'categorias': categorias
                                             })

def remover_carrinho(request, id):
    request.session['carrinho'].pop(id)
    request.session.save()
    return redirect('/ver_carrinho')


@cache_page(60 * 100)
@transaction.atomic
def contact(request):
    categorias = get_categorias_com_contagem()
    if not request.session.get('carrinho'):
        request.session['carrinho'] = []
        request.session.save()
        
    if request.method == "GET":
        categorias = get_categorias_com_contagem()
        status = request.GET.get('status')
        return render(request,'contact.html',{'status':status,'categorias':categorias,
                                              'carrinho': len(request.session['carrinho']),
                                              })
    else:
        NOME = request.POST.get('name')
        EMAIL = request.POST.get('email')
        TELEFONE = request.POST.get('phone')
        MENSAGEM = request.POST.get('message')
        
        new_contato= Contato(
            Nome=NOME,
            Email=EMAIL,
            Telefone=TELEFONE,
            Mensagem=MENSAGEM
        )
        new_contato.save()
        messages.add_message(request, constants.SUCCESS, 'Enviado com sucesso')
        return redirect("contact")

@transaction.atomic   
def formulario(request):
    if request.method =="POST":
        email = request.POST.get('email')
       
        if len(email) == 0:
            logger.warning(f'insira um email valido'+str(datetime.datetime.now())+' horas!')
            messages.add_message(request, constants.WARNING, 'insira um email valido')
            return redirect("/")
        valida = Email.objects.filter(email=email)
        if valida.exists():
            messages.add_message(request, constants.ERROR, 'Email Ja cadastrado')
            logger.info(f'Email Ja cadastrado {email} '+str(datetime.datetime.now())+' horas!')
            return redirect("/")
        Email.objects.create(
            email=email
        )
        messages.add_message(request, constants.SUCCESS, 'Cadastrado com sucesso')
        return redirect("/")
    
@transaction.atomic
def unsubscriber(request,id):
    email = Email.objects.get(id=id)
    email.ativo =False
    email.save()
    logger.info(f'Cancelado sua Inscriçao {email} '+str(datetime.datetime.now())+' horas!')
    return HttpResponse('Cancelado sua Inscriçao')


@login_required(login_url='/admin/login/?next=/admin/') 
def enviar_emeil(request):
    try:
        path_template = os.path.join(settings.BASE_DIR, 'produto/templates/emails/email.html')
        base_url = request.build_absolute_uri('/')
        emails = Email.objects.filter(ativo=True).all()
        produtos = Produto.objects.only('id','nome_produto','descricao','img').filter(promocao=True,ativo=True).all().order_by('-id')[:15]

        for email in emails:
            email_html(path_template, 'Novos Produtos em Promoçao', [email,],produtos=produtos,email=email,base_url=base_url)
            messages.add_message(request, constants.SUCCESS, 'Emails enviados com sucesso')
            return redirect("/")
        
    except Exception as msg:
        messages.add_message(request, constants.ERROR, f'Nao foi possivel enviar os Emails consulte o arquivo de Log')
        logger.critical(f'{msg} '+str(datetime.datetime.now())+' horas!')
        return redirect("/")


@cache_page(60 * 100)
def robots(request):
    if not settings.DEBUG:
        path = os.path.join(settings.STATIC_ROOT,'robots.txt')
        with open(path,'r') as arq:
            return HttpResponse(arq, content_type='text/plain')
    else:
        path = os.path.join(settings.BASE_DIR,'templates/static/robots.txt')
        with open(path,'r') as arq:
            return HttpResponse(arq, content_type='text/plain')


class Sitemap(sitemaps.Sitemap):
    i18n = True
    changefreq ='monthly'
    priority = 0.7

    def items(self):
        return Produto.objects.filter(ativo=True).all()    

    def lastmod(self, obj):
        return obj.data_upload