
import os
from dotenv import load_dotenv
import json

import discord
from discord import app_commands
from discord.ext import commands

load_dotenv()
MY_GUILD = discord.Object(id=os.getenv("GUILD_ID"))
ADMIN_ROLES = [int(role.strip()) for role in os.getenv("ADMIN_ROLES").split(",")]

with open("embeds.json", "r") as file:
    private = json.load(file)

JoinDetails = discord.Embed(title="Join details", description= "Please avoid sharing the credentials outside this server thank you.", color=discord.Colour(0x009cff))
JoinDetails.add_field(name="Server IP:", value=private["ip"], inline=False)
JoinDetails.add_field(name="Password:", value=private["password"], inline=False)

r2Setup = discord.Embed(title="Starter Pack", description="We'll help you get set up with a starter mod pack of curated mods that we recommend.", color=discord.Colour(0x0785cb))
r2Setup.set_thumbnail(url="https://thunderstore.io/thumbnail-serve/repository/icons/ebkr-r2modman-3.2.17.png/?width=256&height=256")
r2Setup.add_field(name="STEPS", value="1. Install [r2modman](https://thunderstore.io/package/ebkr/r2modman/) from the Thunderstore by clicking **Manual Download**.\n2. Run the application and select Valheim.\n3. In the Profile selection screen click **Import / Update.**\n4. Select **From code**.\n5. Paste this code `019eabd4-e017-8ccb-acc0-6a165f0c3896` into the text box and select **Continue** then **Import**.\n6. Click on the profile and then **Select profile**.\n7. In the top left click **Start modded** to run Valheim with the mods installed.", inline=False)

class Embeds(commands.Cog):
    def __init__(self,client):
        self.client = client

    async def cog_load(self):
        self.client.add_view(WikiView())
        self.client.add_view(ModsView())

    @app_commands.command(name="set-ip", description="Sets the server IP")
    @app_commands.guilds(MY_GUILD)
    @app_commands.checks.has_any_role(*ADMIN_ROLES)
    async def setip(self, interaction: discord.Interaction, ip: str):
        private["ip"] = ip
        with open("embeds.json","w") as file:
            json.dump(private, file)
        await interaction.response.send_message(f"Set the server IP to {ip}", ephemeral=True)

    @app_commands.command(name="set-password", description="Sets the server password")
    @app_commands.guilds(MY_GUILD)
    @app_commands.checks.has_any_role(*ADMIN_ROLES)
    async def setpass(self, interaction: discord.Interaction, passw: str):
        private["password"] = passw
        with open("embeds.json","w") as file:
            json.dump(private, file)
        await interaction.response.send_message(f"Set the server password to {passw}", ephemeral=True)

    @app_commands.command(name="wiki", description="information")
    @app_commands.guilds(MY_GUILD)
    async def wiki(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Eikforge - Server Wiki",
            description="Welcome to Eikforge! Our server aspires to create a highly immersive world and community bound together by challenging gameplay modifiers. This season our goal is to develop every inch of the world. Our server caters to highly experienced players looking for something to get absorbed in, but we're eager to help newer players get acquainted with the gameplay style!",
            color=discord.Colour(0x54ad60)
            )
        embed.add_field(name="World Settings", value="- **No Map**\n- **No Portals**\n- **Combat:** Custom ~ VeryHigh\n- **Raids:** Dynamic ~ MuchMore\n- **Resource Rate:** 1x\n- **Building Material Resource Rate:** 3x (Experimental)", inline=False)
        embed.add_field(name="Server Info", value="- **Region:** US-East\n- **Daily Restart:** <t:1779084000:t>", inline=False)
        embed.add_field(name="Rules", value="- Brand new character\n- No griefing or stealing\n- No skipping bosses\n- Our general rule for mods is: If it negatively affects others, it is no good. That *includes* pulling ahead and exploring regions beyond the current boss. Check out our full mods policy using the navigation buttons below.", inline=False)

        view = WikiView()

        await interaction.response.send_message(embed=embed, view=view)
    
    @app_commands.command(name="join", description="how to join")
    @app_commands.guilds(MY_GUILD)
    async def join(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=JoinDetails)

    @app_commands.command(name="r2modman", description="r2modman setup")
    @app_commands.guilds(MY_GUILD)
    async def r2command(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=r2Setup)
    
    @app_commands.command(name="screenshotwebhook", description="Webhooks for screenshot uploads")
    @app_commands.guilds(MY_GUILD)
    async def screenshots(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Discord Screenshot Webhooks",
            description="Install [Discord_Screenshots](https://thunderstore.io/c/valheim/p/warpalicious/Discord_Screenshots/) and add these URLs to the config to let your client post screencaps and deaths directly to our pictures channel!",
            url="https://thunderstore.io/c/valheim/p/warpalicious/Discord_Screenshots/",
            color=discord.Color(0x7cbcff)
        )
        embed.set_thumbnail(url="https://thunderstore.io/thumbnail-serve/repository/icons/warpalicious-Discord_Screenshots-1.6.1.png/?width=256&height=256")
        embed.add_field(name="[Player Capture Webhook]", value="`URL = https://discord.com/api/webhooks/1511382668200382525/9ohSupu_0OjXZxXnctHvwlo1t2WgBcCqD2OhAxgIt4tZkqTclNaI3g9oTKpdl7bm0jLn`", inline=False)
        embed.add_field(name="[Webhook]", value="`URL = https://discord.com/api/webhooks/1512509167259095182/YdFMVDpMZkh-xjiO-7ZPAsSszEf9M19osVgmqnI7b1crejztnxdXIRYgO2lSESnlVHnh`", inline=False)
        embed.set_footer(text="alternatively you can copy the attached config file")
        await interaction.response.send_message(embed=embed, file=discord.File("cogs/warpalicious.discordScreenshots.cfg"))

    @app_commands.command(name="bshelp", description="boss scheduler help")
    @app_commands.guilds(MY_GUILD)
    async def bshelp(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Boss Scheduler Help",
            description="This is a tool that lets players vote when they are ready to fight the next boss!"
        )
        embed.add_field(name="How it works", value="By clicking 'Let's go' you can ready up to fight the next boss. Once enough players vote a poll will be created to choose what time they'd like to fight the boss. We plan to fight the boss multiple times for multiple players! So if you can't make it to the fight you can plan your own!", inline=False)
        embed.add_field(name="What if I'm not ready?", value="It's up to the admins to decide what the vote threshold should be. Currently there's no way for players to vote *against* starting the fight, only rescinding their vote if they change their mind.", inline=False)
        embed.add_field(name="How does 'Location' work?", value="WIP", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="bswiki", description="boss scheduler wiki")
    @app_commands.guilds(MY_GUILD)
    @app_commands.checks.has_any_role(*ADMIN_ROLES)
    async def bswiki(self, interaction: discord.Interaction, ephemeral: bool = True):
        embed = discord.Embed(
            title="Boss Scheduler Wiki",
            description="THIS EMBED IS ONLY ACCESSIBLE BY ADMINS"
        )
        embed.add_field(name="Basics", value="The scheduler is basically just an interactable message. Players can vote to initiate the boss fight when they are ready, they can also rescind their vote. At the moment there is no way to vote *against* starting the boss fight. It's up to the admins to configure how many people are needed to initate the fight. Once the vote reaches the threshold a poll is automatically generated.", inline=False)
        embed.add_field(name="Basic Commands", value="""- `/bschedule` this creates a boss scheduler in the current channel. This should only ever need to be used once unless something goes wrong. Also, it doesn't support multiple schedulers, only one sorry.
- `/bsset` set the currently scheduled boss.
- `/bsnext` progress to the next boss. This resets the vote counter and deletes any existing polls.""", inline=False)
        embed.add_field(name="Advanced Commands", value="""- `/bsfound` not set up yet.
- `/bsreset` resets the vote counter. 
- `/bsthreshold` sets the amount of players needed to initate a boss poll.
- `/bscreatepoll` can create a new poll using my custom poll builder which provides 3 templates. Option to register the poll with the scheduler, replacing the existing poll, or create it independently.
- `/bsclearpoll` deletes the existing poll and re-primes the scheduler.
- `/bsprime` when the scheduler reaches its vote threshold and creates a poll it becomes 'un-primed.' This means if someone un-votes and re-votes it won't generate a new poll. If the scheduler becomes un-primed this command can re-prime it.""", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
        

class WikiView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="How to Join", style=discord.ButtonStyle.primary, custom_id=f"{MY_GUILD}:wiki_join")
    async def joinDetails_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=JoinDetails, ephemeral=True)

    @discord.ui.button(label="Mods", style=discord.ButtonStyle.primary, custom_id=f"{MY_GUILD}:wiki_mods")
    async def mods_button(self,interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="Mods Policy", description= "EIKFORGE IS VANILLA FRIENDLY\n\nWe have a lenient QOL mods policy but we intend to maintain the culture of collaborative, slow, and fair progression. Since we welcome crossplay it's important those players feel included as well. If you have a restrictive schedule and rely on certain mods to keep up with the server's progression, you can ping a @Jarl to ask for an exception.", color=discord.Colour(0xb674ea))
        embed.add_field(name="Greylisted Mods", value="These are strictly mods with gameplay adjustments we have made exceptions for, mods with simple QOL improvements are encouraged!\n- **Gizmo**\n- **InstantComfort**\n- **ComfyAddAllFuel**\n- **Sailing** (Smoothbrain)\n- **MorDoor**\n- **AutoRepair**\n- **AzuAreaRepair**\n- **UsefulPaths** (RustyMods)\n- **MassFarming**\n- **TopMining**", inline=False)
        embed.add_field(name="Server Side Mods", value="- **Groups**\n- **BetterNetworking** (tibijczyk)\n- **Expand World Prefabs:** Applies custom gameplay features\n- **Server_devcommands**\n- **FiresDiscordIntegration**\n- **Cron Job**\n- **LocalizationCache**", inline=False)
        embed.add_field(name="Dependencies", value="\n- **YamlDotNet**\n- **JsonDotNET**", inline=False)

        view = ModsView()
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="Modifiers", style=discord.ButtonStyle.primary, custom_id=f"{MY_GUILD}:wiki_modifiers")
    async def modifiers_button(self,interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="Server Modifiers", description= "We use a set of custom modifiers to curate an immersive experience with an emphasis on developing the world first and exploring second.", color=discord.Colour(0xf44020))
        embed.add_field(name="Combat Modifiers", value="- Enemy Damage **+75%** = `enemydamage 175`\n- Enemy HP **+25%** = `playerdamage 75`\n- Enemy Speed and Size **+40%** = `enemyspeedsize 140`\n- Enemy Level Up Chance **20%** = `enemyleveluprate 200`", inline=False)
        embed.add_field(name="Events", value="- [Player Based Events](https://valheim.fandom.com/wiki/Events)\n- Event Rate is configured dynamically based on the amount of players online. In general it will be about double the usual rate.", inline=False)
        embed.add_field(name="Death Penalty", value="- Keep Equipped Items\n- Skill reduction **7.5%**", inline=False)
        embed.add_field(name="Resources", value="- **1x**\n-  **3x** `Wood, Finewood, Corewood, Yggdrasilwood, Ashwood, Stone, Marble, Grausten, Coal, Tar, Wisps, Red Jute, Blue Jute, Crystal` (warning: feature is experimental)", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ModsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="r2modman Setup", style=discord.ButtonStyle.primary, custom_id=f"{MY_GUILD}:mods_r2modman")
    async def r2modman_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=r2Setup, ephemeral=True)

    #@discord.ui.button(label="FDI Setup", style=discord.ButtonStyle.primary)
    #async def fdi_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    #    embed = discord.Embed(title="FiresDiscordIntegration Setup", description="This mod requires a bit of setup to be able to see discord chat in-game. If you used the r2modman setup pack you can ignore this.", color=discord.Colour(0xb674ea))
    #    embed.set_thumbnail(url="https://thunderstore.io/thumbnail-serve/repository/icons/VerdantsAscent-FiresDiscordIntegration-1.0.1.png/?width=256&height=256")
    #    embed.add_field(name="STEPS", value="1. Install [FiresDiscordIntegration](https://thunderstore.io/c/valheim/p/VerdantsAscent/FiresDiscordIntegration/) and anything that enables JereKuusela's Server chat such as [Server_devcommands](https://thunderstore.io/c/valheim/p/JereKuusela/Server_devcommands/).\n2. Ensure **Server chat** is set to **true** in the **Server_devcommands** config.", inline=False)
    #    await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="EWP Scripts", style=discord.ButtonStyle.primary, custom_id=f"{MY_GUILD}:mods_ewp")
    async def ewp_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(file=discord.File("cogs/ewp.zip"), ephemeral=True)

async def setup(client):
    await client.add_cog(Embeds(client))