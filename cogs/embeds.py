
import os
from dotenv import load_dotenv
import json

import discord
from discord import app_commands
from discord.ext import commands

load_dotenv()
MY_GUILD = discord.Object(id=os.getenv("GUILD_ID"))
ADMIN_ROLES = [int(role.strip()) for role in os.getenv("ADMIN_ROLES").split(",")]

with open("private.json", "r") as file:
    private = json.load(file)

class Embeds(commands.Cog):
    def __init__(self,client):
        self.client = client

    @app_commands.command(name="set-ip", description="Sets the server IP")
    @app_commands.guilds(MY_GUILD)
    @app_commands.checks.has_any_role(*ADMIN_ROLES)
    async def setip(self, interaction: discord.Interaction, ip: str):
        private["ip"] = ip
        with open("private.json","w") as file:
            json.dump(private, file)
        await interaction.response.send_message(f"Set the server IP to {ip}", ephemeral=True)

    @app_commands.command(name="set-password", description="Sets the server password")
    @app_commands.guilds(MY_GUILD)
    @app_commands.checks.has_any_role(*ADMIN_ROLES)
    async def setpass(self, interaction: discord.Interaction, passw: str):
        private["password"] = passw
        with open("private.json","w") as file:
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
        embed.add_field(name="World Settings", value="- **No Map**\n- **No Portals**\n- **Combat:** Custom ~ VeryHigh\n- **Raids:** Custom ~ MuchMore\n- **Resource Rate:** 1x\n- **Building Material Resource Rate:** 3x (Experimental)", inline=False)
        embed.add_field(name="Server Info", value="- **Region:** US-East\n- **Daily Restart:** <t:1779084000:t>", inline=False)
        embed.add_field(name="Rules", value="- Brand new character\n- No griefing or stealing\n- No skipping bosses\n- QOL mods **ALLOWED** with exceptions, use the navigation buttons below to view our full mods policy", inline=False)

        view = WikiView()

        await interaction.response.send_message(embed=embed, view=view)

class WikiView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="How to Join", style=discord.ButtonStyle.primary)
    async def joinDetails_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="Join details", description= "Please avoid sharing the credentials outside this server thank you.", color=discord.Colour(0x009cff))
        embed.add_field(name="Server IP:", value=private["ip"], inline=False)
        embed.add_field(name="Password:", value=private["password"], inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Mods", style=discord.ButtonStyle.primary)
    async def mods_button(self,interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="Mods Policy", description= "EIKFORGE IS VANILLA FRIENDLY\n\nWe have a lenient QOL mods policy but we intend to maintain the culture of collaborative, balanced, and fair progression. Since we welcome crossplay it's important those players feel included as well. If you have a restrictive schedule and rely on certain mods to keep up with the server's progression, you can ping a @Jarl to ask for an exception.", color=discord.Colour(0xb674ea))
        embed.add_field(name="Greylisted Mods", value="- **FiresDiscordIntegration:** Highly recommended to benefit from chat features\Server_devcommands:** Dependency for FDI\n- **Gizmo**\n- **InstantComfort**\n- **GammaOfNightLights**\n- **FirstPersonMode**\n- **MorDoor**\n- **AutoRepair**\n- **AzuAreaRepair**\n- **UsefulPaths** (RustyMods)\n- **NoBuildDust**\n- **Venture_Farm_Grid**\n- **Discord_Screenshots** (warpalicious)", inline=False)
        embed.add_field(name="Server Side Mods", value="- **BetterNetworking** (tibijczyk)\n- **Expand World Prefabs:** Applies custom gameplay features\n- **FiresDiscordIntegration**\n- **Cron Job**\n- **LocalizationCache**", inline=False)
        embed.add_field(name="Dependencies", value="- **Server_devcommands**\n- **YamlDotNet**\n- **JsonDotNET**", inline=False)

        view = ModsView()
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="Modifiers", style=discord.ButtonStyle.primary)
    async def modifiers_button(self,interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="Server Modifiers", description= "We use a set of custom modifiers to curate an immersive experience with an emphasis on developing the world first and exploring second.", color=discord.Colour(0xf44020))
        embed.add_field(name="Combat Modifiers", value="- **VeryHard**", inline=False)
        embed.add_field(name="Death Penalty", value="- **Normal**", inline=False)
        embed.add_field(name="Resources", value="- **1x**\n-  **3x** `Wood, Finewood, Corewood, Yggdrasilwood, Ashwood, Stone, Marble, Grausten, Coal, Tar, Wisps, Red Jute, Blue Jute, Crystal` (warning: feature is experimental and not 100% consistent)", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ModsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="r2modman Setup", style=discord.ButtonStyle.primary)
    async def r2modman_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="Starter Pack", description="We'll help you get set up with a starter mod pack of curated mods that we recommend.", color=discord.Colour(0x0785cb))
        embed.set_thumbnail(url="https://thunderstore.io/thumbnail-serve/repository/icons/ebkr-r2modman-3.2.17.png/?width=256&height=256")
        embed.add_field(name="STEPS", value="1. Install [r2modman](https://thunderstore.io/package/ebkr/r2modman/) from the Thunderstore by clicking **Manual Download**.\n2. Run the application and select Valheim.\n3. In the Profile selection screen click **Import / Update.**\n4. Select **From code**.\n5. Paste this code `019e88ed-564b-41b8-4550-a1b6d0af9ecf` into the text box and select **Continue** then **Import**.\n6. Click on the profile and then **Select profile**.\n7. In the top left click **Start modded** to run Valheim with the mods installed.", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="FDI Setup", style=discord.ButtonStyle.primary)
    async def fdi_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="FiresDiscordIntegration Setup", description="This mod requires a bit of setup to be able to see discord chat in-game. If you used the r2modman setup pack you can ignore this.", color=discord.Colour(0xb674ea))
        embed.set_thumbnail(url="https://thunderstore.io/thumbnail-serve/repository/icons/VerdantsAscent-FiresDiscordIntegration-1.0.1.png/?width=256&height=256")
        embed.add_field(name="STEPS", value="1. Install [FiresDiscordIntegration](https://thunderstore.io/c/valheim/p/VerdantsAscent/FiresDiscordIntegration/) and anything that enables JereKuusela's Server chat such as [Server_devcommands](https://thunderstore.io/c/valheim/p/JereKuusela/Server_devcommands/).\n2. Ensure **Server chat** is set to **true** in the **Server_devcommands** config.", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="EWP Scripts", style=discord.ButtonStyle.primary)
    async def ewp_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(file=discord.File("cogs/ewp.zip"), ephemeral=True)

async def setup(client):
    await client.add_cog(Embeds(client))