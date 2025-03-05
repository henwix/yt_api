import random
import string
from apps.videos.models import Video
from apps.channels.models import Channel

video_urls = [
    "https://www.youtube.com/watch?v=3JZ_D3ELwOQ",
    "https://www.youtube.com/watch?v=2vjPBrBU-TM",
    "https://www.youtube.com/watch?v=9bZkp7q19f0",
    "https://www.youtube.com/watch?v=OPf0YbXqDm0",
    "https://www.youtube.com/watch?v=YQHsXMglC9A",
    "https://www.youtube.com/watch?v=6Dh-RL__uN4",
    "https://www.youtube.com/watch?v=RgKAFK5djSk",
    "https://www.youtube.com/watch?v=60ItHLz5WEA",
    "https://www.youtube.com/watch?v=JGwWNGJdvx8",
    "https://www.youtube.com/watch?v=UceaB4D0jpo",
    "https://www.youtube.com/watch?v=7wtfhZwyrcc",
    "https://www.youtube.com/watch?v=VbfpW0pbvaU",
    "https://www.youtube.com/watch?v=09R8_2nJtjg",
    "https://www.youtube.com/watch?v=3AtDnEC4zak",
    "https://www.youtube.com/watch?v=SlPhMPnQ58k",
    "https://www.youtube.com/watch?v=euCqAq6BRa4",
    "https://www.youtube.com/watch?v=lp-EO5I60KA",
    "https://www.youtube.com/watch?v=JfVOs4VSpmA",
    "https://www.youtube.com/watch?v=2Vv-BfVoq4g",
    "https://www.youtube.com/watch?v=34Na4j8AVgA",
    "https://www.youtube.com/watch?v=8j9zMok6two",
    "https://www.youtube.com/watch?v=PMivT7MJ41M",
    "https://www.youtube.com/watch?v=uelHwf8o7_U",
    "https://www.youtube.com/watch?v=YykjpeuMNEk",
    "https://www.youtube.com/watch?v=JGwWNGJdvx8",
    "https://www.youtube.com/watch?v=8aGhZQkoFbQ",
    "https://www.youtube.com/watch?v=OPf0YbXqDm0",
    "https://www.youtube.com/watch?v=3JZ_D3ELwOQ",
    "https://www.youtube.com/watch?v=2vjPBrBU-TM",
    "https://www.youtube.com/watch?v=9bZkp7q19f0",
    "https://www.youtube.com/watch?v=OPf0YbXqDm0",
    "https://www.youtube.com/watch?v=YQHsXMglC9A",
    "https://www.youtube.com/watch?v=6Dh-RL__uN4",
    "https://www.youtube.com/watch?v=RgKAFK5djSk",
    "https://www.youtube.com/watch?v=60ItHLz5WEA",
    "https://www.youtube.com/watch?v=JGwWNGJdvx8",
    "https://www.youtube.com/watch?v=UceaB4D0jpo",
    "https://www.youtube.com/watch?v=7wtfhZwyrcc",
    "https://www.youtube.com/watch?v=VbfpW0pbvaU",
    "https://www.youtube.com/watch?v=09R8_2nJtjg",
    "https://www.youtube.com/watch?v=3AtDnEC4zak",
    "https://www.youtube.com/watch?v=SlPhMPnQ58k",
    "https://www.youtube.com/watch?v=euCqAq6BRa4",
    "https://www.youtube.com/watch?v=lp-EO5I60KA",
    "https://www.youtube.com/watch?v=JfVOs4VSpmA",
    "https://www.youtube.com/watch?v=2Vv-BfVoq4g",
    "https://www.youtube.com/watch?v=34Na4j8AVgA",
    "https://www.youtube.com/watch?v=8j9zMok6two",
    "https://www.youtube.com/watch?v=PMivT7MJ41M",
]

video_titles = [
    "Chris Luno - Ibiza Deep House Mix",
    "Ben Böhmer - Sunset Melodic Session",
    "Lane 8 - Miami Progressive House Set",
    "CamelPhat - Live at Tulum Beach",
    "ARTBAT - Melodic Techno Night Mix",
    "Nora En Pure - Chillout Ibiza Vibes",
    "Yotto - Deep House Grooves 2024",
    "Kygo - Tropical House Sunset Mix",
    "Black Coffee - Organic House Journey",
    "Claptone - Masked House Magic",
    "Chris Luno - Rooftop Deep Vibes",
    "Ben Böhmer - Berlin Melodic Nights",
    "Lane 8 - Winter Chill Progressive Set",
    "CamelPhat - Deep & Dark Underground",
    "ARTBAT - Techno Sunrise Set 2024",
    "Nora En Pure - Ocean Breeze Mix",
    "Yotto - Hypnotic Melodic House",
    "Kygo - Endless Summer Chillout",
    "Black Coffee - Afro House Grooves",
    "Claptone - Secret Garden DJ Set",
    "Chris Luno - Cozy Deep House Night",
    "Ben Böhmer - Dreamy Melodic Waves",
    "Lane 8 - Late Night Progressive Mix",
    "CamelPhat - London Underground Vibes",
    "ARTBAT - Euphoric Techno Session",
    "Nora En Pure - Sunset Yacht Mix",
    "Yotto - Chill Melodic Soundscape",
    "Kygo - Beach Club House Vibes",
    "Black Coffee - House of Soul Mix",
    "Claptone - Mystical Deep House Set",
    "Chris Luno - Lost in Ibiza Mix",
    "Ben Böhmer - Melodic House Journey",
    "Lane 8 - Progressive House Escape",
    "CamelPhat - Midnight Club Mix",
    "ARTBAT - Rising Techno Sounds",
    "Nora En Pure - Serenity Chill Mix",
    "Yotto - Deep House Therapy",
    "Kygo - Summer Poolside Beats",
    "Black Coffee - Sunset Afro Groove",
    "Claptone - Secret Sunset Set",
    "Chris Luno - Late Night House Flow",
    "Ben Böhmer - Floating Melodic Set",
    "Lane 8 - Dreamscape Progressive Mix",
    "CamelPhat - Underground Club Session",
    "ARTBAT - Afterhours Techno Mix",
    "Nora En Pure - Nature Sounds House",
    "Yotto - Otherworldly Deep Journey",
    "Kygo - Island Breeze House Mix",
    "Black Coffee - Deep Afro Experience",
    "Claptone - Magic House Night",
]

def generate_video_link():
    chars = string.digits + string.ascii_letters

    while True:
        link = ''.join(random.choices(chars, k=11))
        if not Video.objects.filter(video_id=link).exists():
            return link

def run():
    videos = []
    author = Channel.objects.get(slug='root')

    for i in range(48):
        v = Video(
                video_id=generate_video_link(),
                author=author,
                name=video_titles[i],
                yt_link=video_urls[i],
            )
        videos.append(v)

    Video.objects.bulk_create(videos)
    print('done!')


    