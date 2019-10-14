import discord
import asyncio
import requests
import datetime
from sqlalchemy.orm import sessionmaker
from bs4 import BeautifulSoup
from CourseBot.Client.models import engine, Course, Channel, association_table, Lecture

Session = sessionmaker(bind=engine)
session = Session()

forelesning_main = "https://forelesning.gjovik.ntnu.no/publish/"
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
        if message.content.startswith("ping"):
            await message.channel.send("pong")
        if message.content.startswith("$subscribe "):
            try:
                course = str(message.content).split("$subscribe ")[1]
                channel = message.channel.id
                result = self.subscribe_to_course(channel, course)
                await message.channel.send(result)
            except:
                print("Sub fail")
        if message.content.startswith("$unsubscribe "):
            try:
                course = str(message.content).split("$unsubscribe ")[1]
                channel = message.channel.id
                result = self.subscribe_to_course(channel, course, unsubscribe=True)
                await message.channel.send(result)
            except:
                print("unSub fail")
        if message.content.startswith("$last-lecture"):
            try:
                author = message.author.mention
                lecture_obj = session.query(Lecture).join(Course).join(association_table).join(Channel).filter(
                    Channel.id == int(message.channel.id)).order_by(Lecture.released.desc()).first()
                text = self.get_lecture_formatted(lecture_obj, new=False, mention=[author])
                await message.channel.send(text)
            except:
                print("lastlecture fail")

    def subscribe_to_course(self, channel, course, unsubscribe=False):
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
            if unsubscribe:
                return f"Not subscribed to '{course}'"
            course_obj.channels.append(channel_obj)
            session.add(course_obj)
            session.commit()
            return f"Now subscribed to '{course}' in this channel\nNew lectures will be posted as soon as they are available"
        else:
            if unsubscribe:
                course_obj.channels.remove(channel_obj)
                session.add(course_obj)
                session.commit()
                return f"Unsubscribed from '{course_obj.id}'"
            else:
                return "Already subscribed in this channel!"

    async def scrape_courses(self):
        await self.wait_until_ready()
        while not self.is_closed():
            for course in session.query(Course).join(association_table).join(Channel).all():
                try:
                    r = requests.get(f"{forelesning_url_base}{course.id}", timeout=10)
                    b = BeautifulSoup(r.text, features="html.parser")
                    rows = b.find_all("tr", {"class": "lecture"})
                    scraped_lecture_dates = session.query(Lecture.released).filter_by(course=course).all()
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
                        lecture_obj = Lecture(course_id=course.id, audio=audio, camera=camera, screen=screen,
                                              combined=combined, length=length, title=title, lecturer=lecturer,
                                              released=released)
                        session.add(lecture_obj)
                        session.commit()
                        if released > course.added:
                            for channel in course.channels:
                                channel = self.get_channel(int(channel.id))
                                await channel.send(self.get_lecture_formatted(lecture_obj, new=True))
                except:
                    print("Scrape excp")
            await asyncio.sleep(300)  # task runs every 60 seconds

    def get_lecture_formatted(self, lecture_obj, new: bool=False, mention: list = []) -> str:
        header=""
        title = "Last"
        if new:
            header="@everyone\n"
            title = "New"
        if mention:
            for user in mention:
                header += f"{user} "
            header += "\n"
        return f"{header}__**{title} lecture for '{lecture_obj.course_id}'**__\n'{lecture_obj.title}' by {lecture_obj.lecturer} - {lecture_obj.length}\nScreen: {forelesning_main}{lecture_obj.screen}\nAudio: {forelesning_main}{lecture_obj.audio}\nCamera: {forelesning_main}{lecture_obj.camera}\nCombined: {forelesning_main}{lecture_obj.combined}\n"
