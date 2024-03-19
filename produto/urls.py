from django.urls import path
from . import views,htmx_views
from django.urls import path
from django.contrib.sitemaps.views import sitemap
from produto.views import robots,Sitemap

app_name = 'Core'

sitemaps = {
    'sitemap': Sitemap,
}

urlpatterns = [
    path("", views.home, name="home"),
    path("loja/", views.loja, name="loja"),
    path("contact/", views.contact, name='contact'),
    path("formulario/", views.formulario, name='formulario'),
    path('unsubscriber/<int:id>',views.unsubscriber, name='unsubscriber'),
    path("categoria/<str:nome>", views.categorias, name='categoria'),
    path("produto/<int:id>", views.produto, name='produto'),
    path("add_carrinho", views.add_carrinho, name='add_carrinho'),
    path("ver_carrinho", views.ver_carrinho, name='ver_carrinho'),
    path("remover_carrinho/<int:id>", views.remover_carrinho, name='remover_carrinho'),
    path('enviar_emeil/',views.enviar_emeil, name='enviar_emeil'),
    path('robots.txt',robots),
    path('sitemap.xml',sitemap, {'sitemaps': sitemaps}),
]

htmx_patterns =[
    path('search/',htmx_views.search, name='search'),
   # path('status/',htmx_views.status, name='status'),
]

urlpatterns += htmx_patterns
