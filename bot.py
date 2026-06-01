import os
from dotenv import load_dotenv
import subprocess
import sys

import discord
from discord import app_commands
from discord.ext import commands

client = commands.Bot(command_prefix="!",intents=discord.Intents.all())

load_dotenv()
MY_GUILD = discord.Object(id=os.getenv("GUILD_ID"))
ADMIN_ROLES = [role.strip() for role in os.getenv("ADMIN_ROLES").split(",")]

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    
    try:
        synced = await client.tree.sync(guild=MY_GUILD)
        print(f"Synced {len(synced)} command(s) to guild {MY_GUILD.id}")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@client.tree.command(name="wiki", description="information", guild=MY_GUILD)
async def wiki(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Title",
        description="Descriptions",
        color=discord.Colour.blue()
        )
    embed.add_field(name="Field 1", value="Hi", inline=True)
    embed.set_footer(text="ID: " + str(interaction.user.id))

    view = PersistentView()

    await interaction.response.send_message(embed=embed, view=view)

@client.tree.command(name="gitpull", description="Pulls the latest commit from the git repository", guild=MY_GUILD)
@app_commands.checks.has_any_role(*ADMIN_ROLES)
async def gitpull(interaction: discord.Interaction):
    await interaction.response.defer()
    await git_pull()
    await interaction.followup.send("complete", ephemeral=True)

@client.tree.command(name="restart", description="Restarts the bot", guild=MY_GUILD)
@app_commands.checks.has_any_role(*ADMIN_ROLES)
async def restart(interaction: discord.Interaction):
    await interaction.response.send_message("restarting...", ephemeral=True)
    await client.close()

@client.tree.command(name="refresh", description="Refreshes embeds", guild=MY_GUILD)
@app_commands.checks.has_any_role(*ADMIN_ROLES)
async def refresh(interaction: discord.Interaction):
    await interaction.response.send_message("Embeds have been refreshed")

@client.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):

    if isinstance(error, (app_commands.MissingRole, app_commands.MissingAnyRole)):

        await interaction.response.send_message(
            "insufficient permissions", 
            ephemeral=True
        )
        return # Stop execution here so it doesn't print to console
        
    # Catch other check failures (like cooldowns)
    elif isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"Command is on cooldown. Try again in {error.retry_after:.1f}s", 
            ephemeral=True
        )
        return

    # Print any other unexpected bugs to your terminal so you can debug them
    print(f"Sorry we ran into an error processing your command: {error}")

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
        join_embed.add_field(name="Server IP:", value="doed.dat.airforce:20134")
        join_embed.add_field(name="Password:", value="beeefcake")

        await interaction.response.send_message(embed=join_embed, ephemeral=True)

async def git_pull():
    try:
        result = subprocess.run(["git","pull","origin","main"], check=True,capture_output=True,text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error during git pull: {e.stderr}", file=sys.stderr)


client.run(os.getenv("BOT_TOKEN"))