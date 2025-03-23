from apps.channels.models import Channel, SubscriptionItem


def run():
    admin = Channel.objects.filter(slug='admin').first()
    channels = Channel.objects.exclude(slug='admin')

    subs = []
    for i in channels:
        subs.append(SubscriptionItem(subscriber=i, subscribed_to=admin))

    SubscriptionItem.objects.bulk_create(subs)

    print('done')
