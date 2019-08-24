import discord
import asyncio

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
        if not course in self.courses_channels.keys():
            self.courses_channels[course] = []
        if not channel in self.courses_channels[course]:
            self.courses_channels[course].append(channel)
            return f"Now following '{course}' in this channel"
        return "Already followed!"

    async def scrape_courses(self):
        while not self.is_closed():
            for course in self.courses_channels.keys():
                for channel in [self.get_channel(channel_text) for channel_text in self.courses_channels[course]]:
                    await channel.send(course)
            await asyncio.sleep(60)  # task runs every 60 seconds
