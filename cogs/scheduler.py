import os
from dotenv import load_dotenv
import json
from enum import Enum
from datetime import datetime, timedelta
import math

import discord
from discord import app_commands
from discord.ext import commands

load_dotenv()
MY_GUILD = discord.Object(id=os.getenv("GUILD_ID"))
ADMIN_ROLES = [int(role.strip()) for role in os.getenv("ADMIN_ROLES").split(",")]
with open("boss.json", "r") as file:
    private = json.load(file)

class Boss(Enum):
    EIKTHYR = 0
    ELDER = 1
    BONEMASS = 2
    MODER = 3
    YAGLUTH = 4
    QUEEN = 5
    FADER = 6

    @property
    def display_name(self) -> str:
        mapping = {
            Boss.EIKTHYR: "Eikthyr",
            Boss.ELDER: "The Elder",
            Boss.BONEMASS: "Bonemass",
            Boss.MODER: "Moder",
            Boss.YAGLUTH: "Yagluth",
            Boss.QUEEN: "The Queen",
            Boss.FADER: "Fader"
        }
        return mapping[self]

class BossScheduler(commands.Cog):
    def __init__(self,client):
        self.client = client
        

    async def cog_load(self):
        self.client.add_view(BossView())

    @app_commands.command(name="bsschedule", description="Sets the boss scheduler in this channel")
    @app_commands.guilds(MY_GUILD)
    @app_commands.checks.has_any_role(*ADMIN_ROLES)
    async def createBossScheduler(self, interaction: discord.Interaction):
        channel = private["bs-channel"]
        if channel is not None:
            message = private["bs-message"]
            if message is not None:
                try:
                    channel = self.client.get_channel(private["bs-channel"])
                    message = await channel.fetch_message(private["bs-message"])
                    await message.delete()
                except discord.NotFound:
                    pass
        bossi = private["current-boss"]
        if bossi is None:
            bossi = 0
            private["current-boss"] = 0
        boss = Boss(bossi)

        ready = private["ready"]
        if ready is None:
            ready = []
            private["ready"] = []
        count = len(ready)

        threshold = private["threshold"]
        if threshold is None:
            threshold = 10
            private["threshold"] = 10
        
        embed = discord.Embed(title=f"{boss.display_name}")
        embed.add_field(name="Ready:",value=f"{count}/{threshold}",inline=False)

        view = BossView()

        channel = interaction.channel
        message = await interaction.response.send_message(embed=embed, view=view)

        private["bs-channel"] = channel.id
        private["bs-message"] = message.message_id
        saveJson()

    @app_commands.command(name="bsset", description="Sets the currently scheduled boss, option to reset the votes")
    @app_commands.choices(boss=[
        app_commands.Choice(name="Eikthyr", value=0),
        app_commands.Choice(name="The Elder", value=1),
        app_commands.Choice(name="Bonemass", value=2),
        app_commands.Choice(name="Moder", value=3),
        app_commands.Choice(name="Yagluth", value=4),
        app_commands.Choice(name="The Queen", value=5),
        app_commands.Choice(name="Fader", value=6)
    ])
    @app_commands.guilds(MY_GUILD)
    @app_commands.checks.has_any_role(*ADMIN_ROLES)
    async def setBoss(self, interaction: discord.Interaction, boss: int, reset: bool = True):
        message = await fetchBossMessage(interaction.client)
        if not message:
            await interaction.response.send_message("There is no boss scheduled", ephemeral=True)
            return
        private["current-boss"] = boss
        if reset:
            private["ready"] = []
            private["primed"] = True
        saveJson()
        await updateBoss(message)
        await interaction.response.send_message("Updated the current boss", ephemeral=True)


    @app_commands.command(name="bsnext", description="Increments the boss")
    @app_commands.guilds(MY_GUILD)
    @app_commands.checks.has_any_role(*ADMIN_ROLES)
    async def incrementBoss(self, interaction: discord.Interaction):
        message = await fetchBossMessage(interaction.client)
        if not message:
            await interaction.response.send_message("There is no boss scheduled", ephemeral=True)
            return
        nextBoss = private["current-boss"]+1
        if nextBoss > 6:
            nextBoss = 0
        private["current-boss"] = nextBoss
        private["ready"] = []
        private["primed"] = True
        poll = await fetchBossPoll(interaction.client)
        if poll:
            await poll.delete()
            private["bs-poll"] = None
            
        saveJson()
        await updateBoss(message)
        await interaction.response.send_message("Next boss scheduled", ephemeral=True)

    @app_commands.command(name="bsfound", description="Upload an image of the boss location")
    @app_commands.guilds(MY_GUILD)
    @app_commands.checks.has_any_role(*ADMIN_ROLES)
    async def foundBoss(self, interaction: discord.Interaction):
        await interaction.response.send_message("hi", ephemeral=True) 

    @app_commands.command(name="bsreset", description="Reset the boss scheduler votes")
    @app_commands.guilds(MY_GUILD)
    @app_commands.checks.has_any_role(*ADMIN_ROLES)
    async def resetReady(self, interaction: discord.Interaction):
        private["ready"] = []
        private["primed"] = True
        saveJson()
        message = await fetchBossMessage(interaction.client)
        if not message:
            await interaction.response.send_message("Reset ready counter but couldn't find a boss scheduler to update", ephemeral=True)
            return
        await updateBoss(message)
        await interaction.response.send_message("Reset ready counter", ephemeral=True)

    @app_commands.command(name="bsthreshold", description="Sets how many players are needed to initiate a boss poll")
    @app_commands.guilds(MY_GUILD)
    @app_commands.checks.has_any_role(*ADMIN_ROLES)
    async def ready_command(self, interaction: discord.Interaction, threshold: int):
        private["threshold"] = threshold
        saveJson()
        message = await fetchBossMessage(interaction.client)
        if not message:
            await interaction.response.send_message("Adjusted the ready threshold but couldn't find a boss scheduler to update", ephemeral=True)
            return
        await updateBoss(message)
        await interaction.response.send_message("Updated ready threshold", ephemeral=True)
        saveJson()

        if readyForPoll():
            await createBossPoll(interaction.client, private["default-poll-template"])
    
    @app_commands.command(name="bsclearpoll", description="Removes the current poll and re-primes the scheduler")
    @app_commands.guilds(MY_GUILD)
    @app_commands.checks.has_any_role(*ADMIN_ROLES)
    async def bsclearpoll_command(self, interaction: discord.Interaction, prime: bool = False):
        poll = await fetchBossPoll(interaction.client)
        if not poll:
            await interaction.response.send_message("There is no poll registered to the boss scheduler", ephemeral=True)
            return
        await poll.delete()
        private["primed"] = prime
        private["bs-poll"] = None
        saveJson()
        if prime:
            await interaction.response.send_message("Poll removed, the bot will create a new poll after the ready threshold is reached", ephemeral=True)
        else:
            await interaction.response.send_message("Poll removed, the bot won't create a new poll after the ready threshold is reached", ephemeral=True)
    
    @app_commands.command(name="bscreatepoll", description="Creates a new boss poll, option to register the poll with the current boss schedule")
    @app_commands.choices(template=[
        app_commands.Choice(name="3DAYS", value=0),
        app_commands.Choice(name="TOMORROW", value=1),
        app_commands.Choice(name="WEEKEND", value=2)
    ])
    @app_commands.guilds(MY_GUILD)
    @app_commands.checks.has_any_role(*ADMIN_ROLES)
    async def bscreatepoll_command(self, interaction: discord.Interaction, template: int = 0, register: bool = True):
        channel = None
        if register:
            channel = await fetchChannelMessage(interaction.client)
            if not channel:
                await interaction.response.send_message("There is no boss scheduler to register the poll to, create one with /bsschedule or repeat the command without registration", ephemeral=True)
                return
            await createBossPoll(interaction.client, template)
            await interaction.response.send_message("Registered a new boss poll", ephemeral=True)
        else:
            await interaction.response.send_message(poll=pollBuilder(template))
        
    @app_commands.command(name="bsprime", description="Primes the boss scheduler")
    @app_commands.guilds(MY_GUILD)
    @app_commands.checks.has_any_role(*ADMIN_ROLES)
    async def bsprime_command(self, interaction: discord.Interaction):
        private["primed"] = True
        saveJson()
        await interaction.response.send_message("Re-primed the boss scheduler", ephemeral=True)
    
def addReady(id: int):
    ready = private["ready"]
    if ready is None:
        ready = []
    if id in ready:
        return False
    ready.append(id)
    private["ready"] = ready
    saveJson()
    return True

def removeReady(id: int):
    ready = private["ready"]
    if ready is None:
        return False
    try:
        ready.remove(id)
    except ValueError:
        return False
    private["ready"] = ready

    saveJson()
    return True

async def updateBoss(message):
    if not message or not message.embeds:
        return False
    embed = message.embeds[0]
    if not embed:
        return False
    embed.title = Boss(private["current-boss"]).display_name
    embed.set_field_at(0, name="Ready", value=f"{len(private["ready"])}/{private["threshold"]}")
    await message.edit(embed=embed)
    return True

def readyForPoll():
    if len(private["ready"]) >= private["threshold"] and private["primed"] and private["enable-poll"]:
        return True
    return False

async def fetchChannelMessage(client):
    try:
        return client.get_channel(private["bs-channel"]) or await client.fetch_channel(private["bs-channel"])
    except (discord.NotFound, discord.HTTPException):
        return None

async def fetchBossMessage(client):
    channel = await fetchChannelMessage(client)
    if channel is not None:
        message = private["bs-message"]
        if message is not None:
            try:
                message = await channel.fetch_message(private["bs-message"])
                return message
            except (discord.NotFound, discord.HTTPException):
                pass
    return None

async def fetchBossPoll(client):
    channel = await fetchChannelMessage(client)
    if channel is not None:
        try:
            poll = await channel.fetch_message(private["bs-poll"])
            return poll
        except (discord.NotFound, discord.HTTPException):
            pass
    return None

async def createBossPoll(client, template: int = 0):
    channel = await fetchChannelMessage(client)
    if channel is not None:
        try:
            poll = await channel.fetch_message(private["bs-poll"])
            if hasattr(poll, "delete"):
                await poll.delete()
        except (discord.NotFound, discord.HTTPException):
            pass
        poll = pollBuilder(template)
        message = await channel.send(poll=poll)
        private["bs-poll"] = message.id
        private["primed"] = False
        print(private["primed"])
        saveJson()
        return True
    return None

#0 = 2 days, 1 = tomorrow, 2 = weekend
def pollBuilder(template: int):
    poll = discord.Poll(
        question=f"What time are you ready to fight {Boss(private["current-boss"]).display_name}?",
        duration=timedelta(days=1),
        multiple=False
    )
    now = datetime.now()
    match template:
        case 2:
            diff = math.floor(4 - now.weekday())
            if diff >= 1:
                duration = timedelta(days=diff)
            else:
                duration = timedelta(hours=12)
            poll.duration = duration
            poll.add_answer(text=f"Friday 12:00 - 24:00 UTC", emoji=None)
            poll.add_answer(text=f"Saturday 0:00 - 12:00 UTC", emoji=None)
            poll.add_answer(text=f"Saturday 12:00 - 24:00 UTC", emoji=None)
            poll.add_answer(text=f"Sunday 0:00 - 12:00 UTC", emoji=None)
            poll.add_answer(text=f"Sunday 12:00 - 24:00 UTC", emoji=None)
        case 1:
            tomorrow = (now + timedelta(days=1)).strftime("%A")
            poll.add_answer(text=f"{tomorrow} 0:00 - 6:00 UTC", emoji=None)
            poll.add_answer(text=f"{tomorrow} 6:00 - 12:00 UTC", emoji=None)
            poll.add_answer(text=f"{tomorrow} 12:00 - 18:00 UTC", emoji=None)
            poll.add_answer(text=f"{tomorrow} 18:00 - 24:00 UTC", emoji=None)
        case 0 | _:
            day = 1
            if now.time().hour >= 12:
                day = 2
            poll.add_answer(text=f"{(now + timedelta(days=day)).strftime('%A')} 12:00 - 24:00 UTC", emoji=None)
            poll.add_answer(text=f"{(now + timedelta(days=day+1)).strftime('%A')} 0:00 - 12:00 UTC", emoji=None)
            poll.add_answer(text=f"{(now + timedelta(days=day+1)).strftime('%A')} 12:00 - 24:00 UTC", emoji=None)
            poll.add_answer(text=f"{(now + timedelta(days=day+2)).strftime('%A')} 12:00 - 24:00 UTC", emoji=None)
            poll.add_answer(text=f"This Weekend", emoji=None)
    return poll
        

def saveJson():
    with open("boss.json", "w") as file:
        json.dump(private, file)

class BossView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Let's Go", style=discord.ButtonStyle.success, custom_id=f"{MY_GUILD}:boss_ready")
    async def ready_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        message = await fetchBossMessage(interaction.client)
        if not message:
            await interaction.response.send_message("There is no boss scheduled", ephemeral=True)
            return
        
        if not addReady(interaction.user.id):
            await interaction.response.send_message("You have already voted to fight the boss", ephemeral=True)
            return
        
        if await updateBoss(message):
            await interaction.response.send_message("Vote registered", ephemeral=True)
        else:
            await interaction.response.send_message("Vote failed", ephemeral=True)
        
        if readyForPoll():
            await createBossPoll(interaction.client, private["default-poll-template"])
            
    
    @discord.ui.button(label="Not Yet", style=discord.ButtonStyle.danger, custom_id=f"{MY_GUILD}:boss_wait")
    async def wait_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        message = await fetchBossMessage(interaction.client)
        if not message:
            await interaction.response.send_message("There is no boss scheduled", ephemeral=True)
            return
        removeReady(interaction.user.id)
        await updateBoss(message)
        if private["primed"]:
            await interaction.response.send_message("Vote registered", ephemeral=True)
        else:
            await interaction.response.send_message("Unfortunately the vote is already underway. But if enough players rescind their votes, the moderators may decide to cancel the fight!", ephemeral=True)

    @discord.ui.button(label="Location", style=discord.ButtonStyle.primary, custom_id=f"{MY_GUILD}:boss_location")
    async def locate_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Location not found", ephemeral=True)


async def setup(client):
    await client.add_cog(BossScheduler(client))