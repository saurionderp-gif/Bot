import discord
import random
from datetime import date
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True




class MyClient(discord.Client):
    def __init__(self, *, intents):
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)


    async def setup_hook(self):
        await self.tree.sync()

client = MyClient(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Only respond in the "hog-check" text channel
    if message.channel.name == "hog-check" or message.channel.name == "testing":
        
        if message.content.startswith('!hog'):
            size = random.randint(0, 45)
            User = str(message.author.display_name)
            today = date.today().isoformat()
            try:
                with open("hog_results.txt", "r") as f:
                    lines = f.readlines()
            except FileNotFoundError:
                print("File not found, creating new one.")
                lines = []
            # Check if author already has an entry for today
            found = None
            for line in lines:
                if User in line and today in line:
                    found = line.strip()
                    break
            if found:
                print("Duplicate entry found")
                await message.channel.send(
                    f'{User}, your existing Hog for today is: {found.split(":")[1].strip()}'
                )
            else:
                print("No duplicate, adding entry")
                with open("hog_results.txt", "a") as f:
                    f.write(f"{today} {User}: {size}cm\n")
                await message.channel.send(
                    f'Your new Hog is {size}cm, {User}!'
                )

        if message.content.startswith('!leaderboard'):
            today = date.today().isoformat()
            try:
                with open("hog_results.txt", "r") as f:
                    lines = f.readlines()
            except FileNotFoundError:
                lines = []
            results = []
            for line in lines:
                if "cm" not in line or today not in line:
                    continue  
                try:
                    # Split on the first colon to get author and size
                    date_and_author, size_str = line.strip().split(":", 1)
                    # Remove the date from author
                    author = date_and_author.strip().split(" ", 1)[1]
                    size = int(size_str.strip().replace("cm", ""))
                    results.append((author, size))
                except Exception:
                    continue
            top5 = sorted(results, key=lambda x: x[1], reverse=True)[:5]
            if top5:
                leaderboard = "\n".join(
                    [f"{author}: {size} cm" for author, size in top5]
                )
                await message.channel.send(f"🏆 Top 5 Hog Results for Today:\n{leaderboard}")
            else:
                await message.channel.send("No results yet for today!")


        if message.content.startswith('!loserboard'):
            today = date.today().isoformat()
            try:
                with open("hog_results.txt", "r") as f:
                    lines = f.readlines()
            except FileNotFoundError:
                lines = []
            results = []
            for line in lines:
                if "cm" not in line or today not in line:
                    continue  
                try:
                    date_and_author, size_str = line.strip().split(":", 1)
                    author = date_and_author.strip().split(" ", 1)[1]
                    size = int(size_str.strip().replace("cm", ""))
                    results.append((author, size))
                except Exception:
                    continue
            bottom5 = sorted(results, key=lambda x: x[1])[:5]
            if bottom5:
                loserboard = "\n".join(
                    [f"{author}: {size} cm" for author, size in bottom5]
                )
                await message.channel.send(f"🐷 Motions of the ocean Hog Results for Today:\n{loserboard}")
            else:
                await message.channel.send("No results yet for today!")

        if message.content.startswith('!average'):
            User = str(message.author.display_name)
            try:
                with open("hog_results.txt", "r") as f:
                    lines = f.readlines()
            except FileNotFoundError:
                lines = []
            sizes = []
            for line in lines:
                if "cm" not in line:
                    continue
                try:
                    date_and_author, size_str = line.strip().split(":", 1)
                    author = date_and_author.strip().split(" ", 1)[1]
                    size = int(size_str.strip().replace("cm", ""))
                    if author == User:
                        sizes.append(size)
                except Exception:
                    continue
            if sizes:
                avg = sum(sizes) / len(sizes)
                await message.channel.send(f"{User}, your Hog average is {avg:.2f} cm")
            else:
                await message.channel.send(f"{User}, you have no Hog results yet.")

@client.tree.command(name="leaderboard", description="Show leaderboard for a date range (YYYY-MM-DD)")
async def leaderboard(interaction: discord.Interaction, start: str, end: str):
    """Slash command: /leaderboard start end"""
    try:
        with open("hog_results.txt", "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []
    author_best = {}
    for line in lines:
        if "cm" not in line:
            continue
        try:
            date_part = line.split(" ", 1)[0]
            if start <= date_part <= end:
                date_and_author, size_str = line.strip().split(":", 1)
                author = date_and_author.strip().split(" ", 1)[1]
                size = int(size_str.strip().replace("cm", ""))
                # Keep only the highest size per author
                if author not in author_best or size > author_best[author]:
                    author_best[author] = size
        except Exception:
            continue
    # Convert to list and sort
    top5 = sorted(author_best.items(), key=lambda x: x[1], reverse=True)[:5]
    if top5:
        leaderboard = "\n".join(
            [f"{author}: {size} cm" for author, size in top5]
        )
        await interaction.response.send_message(
            f"🏆 Top 5 Hog Results for {start} to {end}:\n{leaderboard}"
        )
    else:
        await interaction.response.send_message(
            f"No results found between {start} and {end}."
        )

@client.tree.command(name="average", description="Show the average Hog size for a user")
async def average(interaction: discord.Interaction, user: discord.Member):
    User = user.display_name
    try:
        with open("hog_results.txt", "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []
    sizes = []
    for line in lines:
        if "cm" not in line:
            continue
        try:
            date_and_author, size_str = line.strip().split(":", 1)
            author = date_and_author.strip().split(" ", 1)[1]
            size = int(size_str.strip().replace("cm", ""))
            if author == User:
                sizes.append(size)
        except Exception:
            continue
    if sizes:
        avg = sum(sizes) / len(sizes)
        await interaction.response.send_message(f"{User}'s Hog average is {avg:.2f} cm")
    else:
        await interaction.response.send_message(f"{User} has no Hog results yet.")

@client.tree.command(name="dice", description="Roll a dice with a specified number of sides")
async def roll_dice(interaction: discord.Interaction, number: int):
   if number < 1:
       await interaction.response.send_message('Please enter a number greater than 0')
       return
   if number != int(number):
       await interaction.response.send_message('Please enter a whole number')
       return
   dice  = random.randint(1, number)
   await interaction.response.send_message(f'You rolled a {dice} out of {number}')

client.run(TOKEN)
