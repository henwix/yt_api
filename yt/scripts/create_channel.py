from apps.channels.models import Channel
from django.contrib.auth import get_user_model
from django.db import transaction


def run():
    username = 'henwixx'

    with transaction.atomic():
        user = get_user_model()(
            username=username,
            email=username + '@gmail.com',
        )
        user.set_password('1234q1234q')
        user.save()
        Channel.objects.create(name=username, slug=username, user=user, country='Israel')
        transaction.on_commit(lambda: print('done: ' + username))
