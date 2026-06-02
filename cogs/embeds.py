
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
            description="Welcome to Eikforge! Our server aspires to create a highly immersive world and community bound together by challenging gameplay modifiers. This season our goal is to develop every inch of the world. Our server caters to highly experienced players looking for something to get absorbed in, but we're eager to help newer get acquainted with the gameplay style!",
            color=discord.Colour(0x54ad60)
            )
        embed.add_field(name="World Settings", value="- **No Map**\n- **No Portals**\n- **Combat:** Custom ~ VeryHigh\n- **Raids:** Custom ~ MuchMore\n- **Resource Rate:** 1x\n- **Building Material Resource Rate:** 3x (Experimental)", inline=False)
        embed.add_field(name="Server Info", value="- **Region:** US-West\n- **Daily Restart:** <t:1779084000:t>", inline=False)
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
        embed.add_field(name="Greylisted Mods", value="- **FiresDiscordIntegration:** Highly recommended to benefit from chat features\n- **Gizmo**\n- **InstantComfort**\n- **GammaOfNightLights**\n- **FirstPersonMode**\n- **MorDoor**\n- **AutoRepair**\n- **AzuAreaRepair**\n- **UsefulPaths** (RustyMods)\n- **NoBuildDust**\n- **MassFarming**\n- **PlantEverything: COSMETIC ONLY** We want to enforce the balancing restrictions imposed by no portal gameplay", inline=False)
        embed.add_field(name="Dependencies", value="- **YamlDotNet**\n- **JsonDotNET**", inline=False)
        embed.add_field(name="Server Side Mods", value="- **BetterNetworking** (tibijczyk)\n- **Expand World Prefabs:** Applies custom gameplay features\n- **FiresDiscordIntegration**\n- **Cron Job**\n- **LocalizationCache**", inline=False)
        

        view = ModsView()
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="Modifiers", style=discord.ButtonStyle.primary)
    async def modifiers_button(self,interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="Server Modifiers", description= "We use a set of custom modifiers to curate an immersive experience with an emphasis on developing the world first and exploring second.", color=discord.Colour(0xf44020))
        embed.add_field(name="Combat Modifiers", value="- **VeryHard**", inline=False)
        embed.add_field(name="Resources", value="- **1x**\n-  **3x** `Wood, Finewood, Corewood, Yggdrasilwood, Ashwood, Stone, Marble, Grausten, Coal, Tar, Wisps, Red Jute, Blue Jute, Crystal` (warning: feature is experimental and not 100% consistent)", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ModsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="EWP Scripts", style=discord.ButtonStyle.primary)
    async def modifiers_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(file=discord.File("cogs/ewp.zip"), ephemeral=True)



async def setup(client):
    await client.add_cog(Embeds(client))