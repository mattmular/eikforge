import sys
import os
from dotenv import load_dotenv
import json
import subprocess

import discord
from discord import app_commands
from discord.ext import commands

client = commands.Bot(command_prefix="!",intents=discord.Intents.all())

load_dotenv()
MY_GUILD = discord.Object(id=os.getenv("GUILD_ID"))
ADMIN_ROLES = [role.strip() for role in os.getenv("ADMIN_ROLES").split(",")]

with open("private.json", "r") as file:
    private = json.load(file)

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await client.load_extension(f"cogs.{filename[:-3]}")
    try:
        synced = await client.tree.sync(guild=MY_GUILD)
        print(f"Synced {len(synced)} command(s) to guild {MY_GUILD.id}")
    except Exception as e:
        print(f"Error syncing commands: {e}")

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
    try:
        await client.reload_extension("cogs.embeds")
        await interaction.response.send_message("Embeds have been refreshed", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Failed to reload embeds.\nError: `{e}`", ephemeral=True) 



@client.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):

    if isinstance(error, (app_commands.MissingRole, app_commands.MissingAnyRole)):
        print(error)
        print(interaction.user.roles)
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
    
async def git_pull():
    try:
        result = subprocess.run(["git","pull","origin","main"], check=True,capture_output=True,text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error during git pull: {e.stderr}", file=sys.stderr)


client.run(os.getenv("BOT_TOKEN"))