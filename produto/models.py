from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe

class Categoria(models.Model):
    categoria = models.CharField(max_length=200)

    def __str__(self):
        return self.categoria
    
class Bairro(models.Model):
    Nome = models.CharField(max_length=100)
    Frete = models.FloatField()

    def __str__(self):
        return self.Nome

class Opcoes(models.Model):
    nome = models.CharField(max_length=100)
    acrecimo = models.FloatField(default=0)
    ativo = models.BooleanField(default=True)
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name_plural = "Opçôes"

class Adicional(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    maximo = models.IntegerField()
    minimo = models.IntegerField()
    opcoes = models.ManyToManyField(Opcoes)
    ativo = models.BooleanField(default=True)
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name_plural = "Adicionais"

class Produto(models.Model):
    nome_produto = models.CharField(max_length=100)
    img = models.ImageField(upload_to='post_img')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    preco = models.FloatField()
    descricao = models.TextField()
    ingredientes = models.CharField(max_length=2000)
    adicionais = models.ManyToManyField(Adicional, blank=True)
    promocao=models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)
    data_upload = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('Core:produto', args=[str(self.id)]) 

    @mark_safe
    def icone(self):
        return f'<img width="30px" src="{self.img.url}">'


    def __str__(self):
        return self.nome_produto
    
class Contato(models.Model):
    Nome = models.CharField(max_length=100,null=True, blank=True)
    Email = models.EmailField()
    Telefone = models.IntegerField()
    Mensagem = models.TextField(max_length=500)
    Lido = models.BooleanField(default=False)
    
    def __str__(self):
        return self.Nome
    
    class Meta:
        verbose_name_plural = "Contatos"

class Email(models.Model):
    email = models.EmailField()
    ativo = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.email
    
    class Meta:
        verbose_name_plural = "Newsletter"

class Unidade(models.Model):
    nome = models.CharField(max_length=100,null=True, blank=True)
    horario_de = models.TimeField(auto_now=False, auto_now_add=False)
    horario_ate = models.TimeField(auto_now=False, auto_now_add=False)
    ativo = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.nome
    class Meta:
        verbose_name_plural = "Horarios"