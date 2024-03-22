from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from pedido.models import Pedido
import pywhatkit as kit

@receiver(post_save, sender=Pedido)
def notification_created(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'public_room',
            {
                "type": "send_notification",
                "message": 'pedido N° ' + str(instance.id)
            }
        )
        #phone_number = f"+55{instance.telefone}"
        message = f" Ola {instance} Recebemos seu pedido de N°{instance.id} no total de R$ {instance.total}"
        print(message)
        #kit.sendwhatmsg_instantly(phone_number, message)
