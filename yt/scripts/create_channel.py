


from apps.channels.models import Channel
from django.contrib.auth import get_user_model

def run():

    user = get_user_model()(
        username='henwix',
        email='123@gmail.com',
    )
    user.set_password('1234q1234q')
    user.save()
    Channel.objects.create(
        name='henwix',
        slug='henwix',
        user=user,
        country='Israel'
    )

    print('done')