def main():
    Faker.seed(0)
    fake = Faker()
    start_date = date(2024, 1, 1)
    end_date = date(2024, 12, 31)
  #  for _ in range(3):
  #      categoria = Categoria.objects.create(
  #          categoria=fake.name()
  #      )
  #      print(f'Categoria criada {categoria.categoria}')
#

    for _ in range(random.randint(5, 8)):
       produto = Produto.objects.create(
           nome_produto=fake.name(),
           img="post_img/produto1.jpg",
           categoria=Categoria.objects.get(id=2),
           preco=random.randint(1, 50),
           descricao=fake.sentence(nb_words=20),
           ingredientes=fake.sentence(nb_words=15),
           promocao=False
       )
       print(f'Produto criada {produto.nome_produto}')
    
    # for _ in range(random.randint(1,60)):
    #     # Criar o pedido
    #     novo_pedido = Pedido.objects.create(
    #         usuario=fake.name(),
    #         data=fake.date_between(start_date=start_date, end_date=end_date),
    #         total=random.randint(1, 100),
    #         troco=random.randint(1, 100),
    #         pagamento=random.randint(1, 100),
    #         cep=random.randint(1, 8),
    #         rua=fake.sentence(nb_words=15),
    #         numero=random.randint(1, 100),
    #         bairro=Bairro.objects.get(id=3),
    #         telefone=random.randint(1, 30),
    #         entregue=False
    #     )
    #     pedido_id = novo_pedido.id  # Armazenar o ID do pedido

    #     for _ in range(random.randint(1,60)):
    #         # Criar o item do pedido usando o ID do pedido criado anteriormente
    #         item_pedido = ItemPedido.objects.create(
    #             pedido_id=pedido_id,  # Usar o ID do pedido
    #             produto=Produto.objects.get(id=random.randint(1, 53)),
    #             quantidade=random.randint(1, 10),
    #             preco=random.randint(1, 100),
    #             descricao=fake.sentence(nb_words=15),
    #             adicionais=fake.sentence(nb_words=15)
    #         )
    #         print(f'Item pedido criado {item_pedido.id}')

    #     print(f'Pedido {novo_pedido.id} Criado')

if __name__ == '__main__':
    import os
    import random
    from django.core.wsgi import get_wsgi_application

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imersaoPython.settings')
    application = get_wsgi_application()
    from faker import Faker
    import random
    from datetime import date
    from produto.models import Produto,Categoria,Bairro
    from pedido.models import Pedido,ItemPedido

    main()