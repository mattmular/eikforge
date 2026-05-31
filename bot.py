import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

intents = discord.Intents.all()
client = commands.Bot(command_prefix="!",intents=intents)
MY_GUILD = discord.Object(id=1493321295293841498)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    
    try:
        synced = await client.tree.sync(guild=MY_GUILD)
        print(f"Synced {len(synced)} command(s) to guild {MY_GUILD.id}")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@client.tree.command(name="wiki", description="information", guild=MY_GUILD)
async def ping(interaction: discord.Interaction):
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
        join_embed.add_field(name="Server IP:", value="doed.dat.airforce:20134")
        join_embed.add_field(name="Password:", value="beeefcake")

        await interaction.response.send_message(embed=join_embed, ephemeral=True)

load_dotenv()
client.run(os.getenv("BOT_TOKEN"))