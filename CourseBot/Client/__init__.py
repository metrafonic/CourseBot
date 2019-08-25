import discord
import asyncio
import requests
import datetime
from sqlalchemy.orm import sessionmaker
from bs4 import BeautifulSoup
from .models import engine, Course, Channel, association_table, Lecture
Session = sessionmaker(bind=engine)
session = Session()

forelesning_main = "http://forelesning.gjovik.ntnu.no/publish/"
forelesning_url_base = f"{forelesning_main}index.php?sortby=start&sorting=reverse&sortby=start&sorting=normal&topic="

class DiscordClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.courses_channels = {}

        # create the background task and run it in the background
        self.scrape_sourse_task = self.loop.create_task(self.scrape_courses())

    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return
        if message.content.startswith("$follow-course "):
            course = str(message.content).split("$follow-course ")[1]
            channel = message.channel.id
            result = self.subscribe_to_course(channel, course)
            await message.channel.send(result)


    def subscribe_to_course(self, channel, course):
        while True:
            course_obj = session.query(Course).filter_by(id=course).first()
            if not course_obj:
                course_obj = Course(id=course)
                session.add(course_obj)
                session.commit()
                continue
            break
        while True:
            channel_obj = session.query(Channel).filter_by(id=channel).first()
            if not channel_obj:
                channel_obj = Channel(id=channel)
                session.add(channel_obj)
                session.commit()
                continue
            break
        if not channel_obj in course_obj.channels:
            course_obj.channels.append(channel_obj)
            session.add(course_obj)
            session.commit()
            return f"Now following '{course}' in this channel"
        else:
            return "Already followed in this channel!"

    async def scrape_courses(self):
        await self.wait_until_ready()
        while not self.is_closed():
            for course in session.query(Course).all():
                print(course)
                r = requests.get(f"{forelesning_url_base}{course.id}")
                b = BeautifulSoup(r.text)
                rows = b.find_all("tr", {"class": "lecture"})
                scraped_lecture_dates = session.query(Lecture.released).filter_by(course=course).all()
                print(scraped_lecture_dates)
                for row in rows:
                    columns = row.find_all("td")
                    released = datetime.datetime.strptime(str(columns[0].contents[0]), "%Y-%m-%d %H:%M")
                    length = str(columns[1].contents[0])
                    lecturer = str(columns[2].contents[0])
                    title = str(columns[3].contents[0])
                    audio = columns[5].find("a", {"title": "Audio, MP3"})["href"]
                    camera = columns[5].find("a", {"title": "Camera - MP4"})["href"]
                    screen = columns[5].find("a", {"title": "Screen - MP4"})["href"]
                    combined = columns[5].find("a", {"title": "Combined camera and screen - MP4"})["href"]
                    if released in [dt[0] for dt in scraped_lecture_dates]:
                        break
                    lecture_obj = Lecture(course_id=course.id, audio=audio, camera=camera, screen=screen, combined=combined, length=length, title=title, lecturer=lecturer, released=released)
                    session.add(lecture_obj)
                    session.commit()
                    for channel in course.channels:
                        channel = self.get_channel(int(channel.id))
                        await channel.send(f"__**New lecture for '{course.id}'**__\n"
                                           f"'{lecture_obj.title}' by {lecture_obj.lecturer} - {lecture_obj.length}\n"
                                           f"Screen: {forelesning_main}{lecture_obj.screen}\n"
                                           f"Audio: {forelesning_main}{lecture_obj.audio}\n"
                                           f"Camera: {forelesning_main}{lecture_obj.camera}\n"
                                           f"Combined: {forelesning_main}{lecture_obj.combined}\n"
                                           f"")
            await asyncio.sleep(20)  # task runs every 60 seconds
