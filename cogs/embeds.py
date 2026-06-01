
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
        await interaction.response.send_message(f"Set the server IP to {ip}")

    @app_commands.command(name="set-password", description="Sets the server password")
    @app_commands.guilds(MY_GUILD)
    @app_commands.checks.has_any_role(*ADMIN_ROLES)
    async def setip(self, interaction: discord.Interaction, passw: str):
        private["password"] = passw
        with open("private.json","w") as file:
            json.dump(private, file)
        await interaction.response.send_message(f"Set the server password to {passw}")

    @app_commands.command(name="wiki", description="information")
    @app_commands.guilds(MY_GUILD)
    async def wiki(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Title",
            description="Descriptions",
            color=discord.Colour.blue()
            )
        embed.add_field(name="Field 1", value="Hi", inline=True)
        embed.set_footer(text="ID: " + str(interaction.user.id))

        view = PersistentView()

        await interaction.response.send_message(embed=embed, view=view)

class PersistentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Rules", style=discord.ButtonStyle.primary)
    async def rules_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        rules_embed = discord.Embed(title="Rules", color=discord.Colour.red())
        rules_embed.add_field(name="rule 1", value="ayo be chill")

        await interaction.response.send_message(embed=rules_embed, ephemeral=True)

    @discord.ui.button(label="How to Join", style=discord.ButtonStyle.primary)
    async def joinInstructions_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        join_embed = discord.Embed(title="How to Join", color=discord.Colour.red())
        join_embed.add_field(name="Server IP:", value=private["ip"])
        join_embed.add_field(name="Password:", value=private["pass"])

        await interaction.response.send_message(embed=join_embed, ephemeral=True)




async def setup(client):
    await client.add_cog(Embeds(client))