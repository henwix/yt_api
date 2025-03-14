from apps.channels.models import Channel
from django.contrib.auth import get_user_model


def run():
    username = "root"

    user = get_user_model()(
        username=username,
        email=username + "@gmail.com",
    )
    user.set_password("1234q1234q")
    user.save()
    Channel.objects.create(name=username, slug=username, user=user, country="Israel")

    print("done: " + username)
