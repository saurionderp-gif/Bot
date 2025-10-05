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
            user_id = str(message.author.id)
            display_name = message.author.display_name
            today = date.today().isoformat()
            # Update old entries
            lines = update_old_entries_with_id(user_id, display_name)
            # Check if user already has an entry for today
            found = None
            for line in lines:
                try:
                    date_and_author, size_str = line.strip().split(":", 1)
                    parts = date_and_author.strip().split(" ")
                    entry_date = parts[0]
                    entry_id = parts[1]
                    entry_name = " ".join(parts[2:])
                    if entry_date == today and entry_id == user_id:
                        found = size_str.strip()
                        break
                except Exception:
                    continue
            if found:
                await message.channel.send(
                    f'{display_name}, your existing Hog for today is: {found}'
                )
            else:
                with open("hog_results.txt", "a") as f:
                    f.write(f"{today} {user_id} {display_name}: {size}cm\n")
                await message.channel.send(
                    f'Your new Hog is {size}cm, {display_name}!'
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
                    date_and_author, size_str = line.strip().split(":", 1)
                    parts = date_and_author.strip().split(" ")
                    user_id = parts[1]
                    display_name = " ".join(parts[2:]) if len(parts) > 2 else "(unknown)"
                    size = int(size_str.strip().replace("cm", ""))
                    results.append((display_name, user_id, size))
                except Exception:
                    continue
            # Only keep the highest result per user_id
            user_best = {}
            for display_name, user_id, size in results:
                if user_id not in user_best or size > user_best[user_id][1]:
                    user_best[user_id] = (display_name, size)
            top5 = sorted(user_best.values(), key=lambda x: x[1], reverse=True)[:5]
            leaderboard = [f"{name}: {size} cm" for name, size in top5]
            if leaderboard:
                await message.channel.send(f"🏆 Top 5 Hog Results for Today:\n" + "\n".join(leaderboard))
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
                    user_id = date_and_author.strip().split(" ", 1)[1]
                    display_name = " ".join(date_and_author.strip().split(" ")[2:])
                    size = int(size_str.strip().replace("cm", ""))
                    results.append((display_name, user_id, size))
                except Exception:
                    continue
            # Only keep the lowest result per user_id
            user_worst = {}
            for display_name, user_id, size in results:
                if user_id not in user_worst or size < user_worst[user_id][1]:
                    user_worst[user_id] = (display_name, size)
            bottom5 = sorted(user_worst.values(), key=lambda x: x[1])[:5]
            loserboard = [f"{name}: {size} cm" for name, size in bottom5]
            if loserboard:
                await message.channel.send(f"🐷 Motions of the ocean Hog Results for Today:\n" + "\n".join(loserboard))
            else:
                await message.channel.send("No results yet for today!")

        if message.content.startswith('!average'):
            user_id = str(message.author.id)
            display_name = message.author.display_name
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
                    author_id = date_and_author.strip().split(" ", 1)[1]
                    size = int(size_str.strip().replace("cm", ""))
                    if author_id == user_id:
                        sizes.append(size)
                except Exception:
                    continue
            if sizes:
                avg = sum(sizes) / len(sizes)
                await message.channel.send(f"{display_name}, your Hog average is {avg:.2f} cm")
            else:
                await message.channel.send(f"{display_name}, you have no Hog results yet.")

        if message.content.startswith('!suck'):
            if not message.mentions:
                await message.channel.send("Usage: !suck @username (mention the user)")
                return
            target_member = message.mentions[0]
            target_id = str(target_member.id)
            today = date.today().isoformat()
            try:
                with open("hog_results.txt", "r") as f:
                    lines = f.readlines()
            except FileNotFoundError:
                lines = []
            found = None
            display_name = target_member.display_name
            for line in lines:
                if "cm" not in line or today not in line:
                    continue
                try:
                    date_and_author, size_str = line.strip().split(":", 1)
                    parts = date_and_author.strip().split(" ")
                    entry_date = parts[0]
                    entry_id = parts[1]
                    entry_name = " ".join(parts[2:])
                    if entry_date == today and entry_id == target_id:
                        found = size_str.strip().replace("cm", "")
                        # Optionally, use entry_name if you want the name from the file
                        break
                except Exception:
                    continue
            if found is not None:
                await message.channel.send(
                    f"You sucked {display_name} {found}cm hog"
                )
            else:
                await message.channel.send(
                    f"{display_name} has no Hog result for today!"
                )

def update_old_entries_with_id(user_id, display_name):
    """Update old entries with display name only to include user ID."""
    try:
        with open("hog_results.txt", "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []
    updated_lines = []
    for line in lines:
        if "cm" not in line:
            updated_lines.append(line)
            continue
        try:
            date_and_author, size_str = line.strip().split(":", 1)
            parts = date_and_author.strip().split(" ")
            # If line has only display name (no user ID)
            if len(parts) == 2 and parts[1] == display_name:
                updated_line = f"{parts[0]} {user_id} {display_name}:{size_str}\n"
                updated_lines.append(updated_line)
            else:
                updated_lines.append(line)
        except Exception:
            updated_lines.append(line)
    with open("hog_results.txt", "w") as f:
        f.writelines(updated_lines)
    return updated_lines

# Slash commands
@client.tree.command(name="leaderboard", description="Show leaderboard for a date range (YYYY-MM-DD)")
async def leaderboard(interaction: discord.Interaction, start: str, end: str):
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
                user_id = date_and_author.strip().split(" ", 1)[1]
                size = int(size_str.strip().replace("cm", ""))
                if user_id not in author_best or size > author_best[user_id]:
                    author_best[user_id] = size
        except Exception:
            continue
    top5 = sorted(author_best.items(), key=lambda x: x[1], reverse=True)[:5]
    leaderboard = []
    guild = interaction.guild
    for user_id, size in top5:
        try:
            member = guild.get_member(int(user_id)) if guild else None
            name = member.display_name if member else user_id
        except ValueError:
            name = user_id
        leaderboard.append(f"{name}: {size} cm")
    if leaderboard:
        await interaction.response.send_message(
            f"🏆 Top 5 Hog Results for {start} to {end}:\n" + "\n".join(leaderboard)
        )
    else:
        await interaction.response.send_message(
            f"No results found between {start} and {end}."
        )

@client.tree.command(name="average", description="Show the average Hog size for a user")
async def average(interaction: discord.Interaction, user: discord.Member):
    user_id = str(user.id)
    display_name = user.display_name
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
            author_id = date_and_author.strip().split(" ", 1)[1]
            size = int(size_str.strip().replace("cm", ""))
            if author_id == user_id:
                sizes.append(size)
        except Exception:
            continue
    if sizes:
        avg = sum(sizes) / len(sizes)
        await interaction.response.send_message(f"{display_name}'s Hog average is {avg:.2f} cm")
    else:
        await interaction.response.send_message(f"{display_name} has no Hog results yet.")

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
