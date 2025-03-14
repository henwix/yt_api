import random

from apps.channels.models import Channel
from django.contrib.auth import get_user_model

random_names = [
    "Emma Johnson",
    "Liam Smith",
    "Olivia Brown",
    "Noah Davis",
    "Ava Miller",
    "William Wilson",
    "Sophia Moore",
    "James Taylor",
    "Isabella Anderson",
    "Logan Thomas",
    "Mia Jackson",
    "Benjamin White",
    "Charlotte Harris",
    "Mason Martin",
    "Amelia Thompson",
    "Elijah Garcia",
    "Harper Martinez",
    "Oliver Robinson",
    "Evelyn Clark",
    "Jacob Rodriguez",
    "Abigail Lewis",
    "Michael Lee",
    "Emily Walker",
    "Daniel Hall",
    "Elizabeth Allen",
    "Henry Young",
    "Sofia Hernandez",
    "Alexander King",
    "Ella Wright",
    "Sebastian Lopez",
    "Grace Hill",
    "Jack Scott",
    "Chloe Green",
    "Owen Adams",
    "Victoria Baker",
    "Samuel Gonzalez",
    "Riley Nelson",
    "Matthew Carter",
    "Aria Mitchell",
    "Joseph Perez",
    "Lily Roberts",
    "David Turner",
    "Zoe Phillips",
    "Carter Campbell",
    "Hannah Parker",
    "Wyatt Evans",
    "Addison Edwards",
    "Jayden Collins",
    "Layla Stewart",
    "Luke Sanchez",
]


def run():
    users = []
    channels = []
    for i in range(46):
        username = random.choice(random_names)
        random_names.remove(username)

        user = get_user_model()(
            username=username.replace(" ", ""),
            email=username + "@gmail.com",
        )
        user.set_password("1234q1234q")
        users.append(user)

        c = Channel(name=username, slug=username, user=user, country="Israel")

        channels.append(c)

    get_user_model().objects.bulk_create(users)
    Channel.objects.bulk_create(channels)
    print(f"done: users - {len(users)}")
