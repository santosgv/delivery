from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'Pedido'

urlpatterns = [
    path("finalizar_pedido/", views.finalizar_pedido, name='finalizar_pedido'),
    path("validaCupom/", views.validaCupom, name='validaCupom'),
    path("freteBairro/", views.freteBairro, name='freteBairro'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)