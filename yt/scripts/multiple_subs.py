
import random
from apps.channels.models import Channel, SubscriptionItem
from django.contrib.auth import get_user_model



def run():
    henwix = Channel.objects.filter(slug='henwix').first()
    # number = random.randint(1, 45)
    channels = Channel.objects.exclude(slug='henwix')
    
    subs = []
    for i in channels:
        subs.append(SubscriptionItem(subscriber=i, subscribed_to=henwix))

    SubscriptionItem.objects.bulk_create(subs)


    print('done')