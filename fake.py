def main():
    Faker.seed(0)
    fake = Faker()

    #for _ in range(3):
    #    categoria = Categoria.objects.create(
    #        categoria=fake.name()
    #    )
    #    print(f'Categoria criada {categoria.categoria}')


    for _ in range(30):
        produto = Produto.objects.create(
            nome_produto=fake.name(),
            img="post_img/produto2.jpg",
            categoria=Categoria.objects.get(id=4),
            preco=random.randint(1, 100),
            descricao=fake.sentence(nb_words=20),
            ingredientes=fake.sentence(nb_words=15),
            promocao=True
        )
        print(f'Produto criada {produto.nome_produto}')

if __name__ == '__main__':
    import os
    import random
    from django.core.wsgi import get_wsgi_application

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imersaoPython.settings')
    application = get_wsgi_application()
    from faker import Faker
    import random
    from produto.models import Produto,Categoria

    main()