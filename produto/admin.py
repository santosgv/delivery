from django.contrib import admin
from .models import Categoria, Produto, Adicional, Opcoes,Contato,Email,Unidade



@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('icone', 'nome_produto', 'categoria', 'preco', 'ativo')
    list_editable = ('preco','ativo')


admin.site.register(Categoria)
admin.site.register(Adicional)
admin.site.register(Opcoes)
admin.site.register(Unidade)

admin.site.register(Email)

@admin.action(description="Marcar como Lido")
def action_read_messenger(modeladmin,request,queryset):
    for mensagem in queryset:
        mensagem.Lido = True
        mensagem.save()

@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ('Nome','Email','Telefone','Mensagem','Lido')
    readonly_fields=('Nome','Email','Telefone','Mensagem')
    list_filter = ('Lido',)
    actions = [action_read_messenger,]