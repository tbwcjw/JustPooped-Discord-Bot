import os
import asyncio
import time
from datetime import datetime

import random

import discord
import sqlite3
import config

from discord.ext import commands
from discord import app_commands

import graph

conn = sqlite3.connect('database/app.db', check_same_thread=False)
conn.execute("PRAGMA journal_mode=WAL;")
conn.execute("PRAGMA synchronous=NORMAL;")
conn.commit()
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS poops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_id TEXT NOT NULL,
    poop_description TEXT NOT NULL,
    poop_rating NUMBER NOT NULL,
    bristol_type NUMBER NOT NULL,
    timestamp NUMBER NOT NULL
)
''')

conn.commit()

@staticmethod
def log_action(action: str, user: discord.Member):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {user} executed: {action}")

@staticmethod
def log_execution_time(func):
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {func.__name__} executed in {elapsed_time:.4f} seconds")
        return result
    return wrapper

class JustPoopedBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.add_commands()

    def add_commands(self):
        @self.event
        async def on_ready():
            await self.tree.sync()
            print(f'Logged in as {self.user.name}')

        @self.tree.command(name="help", description="Lists all available commands")
        async def help(interaction: discord.Interaction):
            log_action("/help", interaction.user)
            await self.show_help(interaction)

        @self.tree.command(name="stats", description="Show server stats or stats for a specific user")
        @app_commands.describe(username="The username to get stats for (optional)")
        async def stats(interaction: discord.Interaction, username: discord.Member = None):
            log_action("/stats" + (f" {username}" if username else ""), interaction.user)
            await self.show_stats(interaction, username)

        @self.tree.command(name="bsc", description="View the bristol stool chart, for your reference")
        async def bsc(interaction: discord.Interaction):
            log_action("/bsc", interaction.user)
            await self.show_bsc(interaction)

        @self.tree.command(name="justpooped", description=f"Log your recent {random.choice(config.POOP_SYNONYMS)} experience")
        async def poop_check(interaction: discord.Interaction):
            log_action("/justpooped", interaction.user)
            await self.log_poop(interaction)

        @self.tree.command(name="minigame", description="Play the shitty minigame")
        async def minigame(interaction: discord.Interaction):
            log_action("/minigame", interaction.user)
            await self.show_minigame(interaction)
        
        @self.tree.command(name="trivia", description=f"Play a {random.choice(config.POOP_SYNONYMS)} trivia minigame!")
        async def trivia(interaction: discord.Interaction):
            log_action("/trivia", interaction.user)
            await self.show_trivia(interaction)

    @log_execution_time
    async def show_trivia(self, interaction:discord.Integration):
        embed = discord.Embed(title="🤔 Trivia", description="Answer the question before the time runs out!", color=discord.Color.blue())
        embed.add_field(name="", value=f"Starting in {config.TRIVIA_COUNTDOWN}...")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        for i in range(config.TRIVIA_COUNTDOWN, 0, -1):
            embed.set_field_at(0, name="", value=f"Starting in {i}...", inline=False)
            await interaction.edit_original_response(embed=embed)
            await asyncio.sleep(1)

        trivia_object = random.choice(config.TRIVIA_QUESTIONS)
        trivia_q = trivia_object['question']
        trivia_c = trivia_object['choices']
        trivia_a = trivia_object['answer']

        choices_str = '\n'.join([f"{chr(65 + index)}. {choice}" for index, choice in enumerate(trivia_c)])
        new_embed = discord.Embed(title=f"{trivia_q} 🤔", description=f"{choices_str}", color=discord.Color.blue())
        new_embed.add_field(name="", value=f"Time remaining: {config.TRIVIA_TIME} seconds", inline=False)
        view = TriviaView(trivia_a, interaction=interaction)
        
        await interaction.edit_original_response(embed=new_embed, view=view)

        remaining_time = config.TRIVIA_TIME
        while not view.game_ended:
            if remaining_time < 1:
                view.clear_items()
                view.game_ended = True
                sad_emoji = config.RATING_EMOJIS[random.choice(list(config.RATING_EMOJIS.keys())[:4])]
                new_embed = discord.Embed(title=f"{random.choice(config.MINIGAME_LOSE_TITLE)}", description=f"You ran out of time! Don't think so hard, you might hurt yourself {sad_emoji}", color=discord.Color.red())
                await interaction.edit_original_response(embed=new_embed, view=view)
                break

            remaining_time -= 1
            new_embed.set_field_at(0, name="", value=f"Time remaining: {remaining_time} seconds", inline=False)
            await interaction.edit_original_response(embed=new_embed, view=view)

            await asyncio.sleep(1 + bot.latency)

    @log_execution_time
    async def show_minigame(self, interaction:discord.Interaction):
        embed = discord.Embed(title="Drop the poop!", description="Drop the poop in the toilet before the time runs out!", color=discord.Color.blue())
        embed.add_field(name="", value=f"Starting in {config.MINIGAME_COUNTDOWN}...")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        for i in range(config.MINIGAME_COUNTDOWN, 0, -1):
            embed.set_field_at(0, name="", value=f"Starting in {i}...", inline=False)
            await interaction.edit_original_response(embed=embed)
            await asyncio.sleep(1)
        
        # | 0 | 1 | 2 | 
        # |   |   |   | p bouncing
        # |   |   |   | t static
        
        poop_positions = [
            "💩 ||......|| ||......||",
            "||......|| 💩 ||......||",
            "||......|| ||......|| 💩"
        ]
        toilet_positions = [
            "🚽 ||......|| ||......||",
            "||......|| 🚽 ||......||",
            "||......|| ||......|| 🚽"
        ]

        index = 0
        direction  = 1 #1 right -1 left
        remaining_time = config.MINIGAME_TIME

        toilet_pos = random.choice(toilet_positions)

        view = MinigameView(index=index, toilet_pos=toilet_positions.index(toilet_pos), interaction=interaction)

        new_embed = discord.Embed(title="Drop the poop!", color=discord.Color.red())
        new_embed.add_field(name=f"", value=poop_positions[1], inline=False)
        new_embed.add_field(name=f"", value=toilet_pos, inline=False)
        new_embed.add_field(name=f"", value=f"Time Remaining: {remaining_time} seconds", inline=False)
        await interaction.edit_original_response(embed=new_embed, view=view)
        
        while not view.game_ended:
            for _ in range(remaining_time):
                index += direction
                view.index = index

                #print(f"loop {_} poop_pos {index} latency {bot.latency}")
                if index == 0 or index == len(poop_positions) -1:
                    direction *= -1

                remaining_time -= 1
                new_embed.set_field_at(2, name="", value=f"Time Remaining: {remaining_time} seconds", inline=False)

                new_embed.set_field_at(0, name="", value=poop_positions[index], inline=False)
                if view.game_ended: #game ended, view handled response
                    await interaction.delete_original_response()
                    break

                await interaction.edit_original_response(embed=new_embed, view=view)
                await asyncio.sleep(config.MINIGAME_SPEED+ bot.latency)
                
            if not view.game_ended: #end game state out of time
                sad_emoji = config.RATING_EMOJIS[random.choice(list(config.RATING_EMOJIS.keys())[:4])]
                new_embed = discord.Embed(title=f"{random.choice(config.MINIGAME_LOSE_TITLE)}", description=f"You ran out of time and the poop fell on the floor! {sad_emoji}", color=discord.Color.red())
                await interaction.edit_original_response(embed=new_embed, view=view)
                break

    @log_execution_time
    async def show_help(self, interaction: discord.Interaction):
        embed = discord.Embed(title=f"🆘 Help", color=discord.Color.orange())
        embed.add_field(name=f"```/help```", value='Lists all available commands', inline=False)
        embed.add_field(name=f"```/stats```", value='Show server stats', inline=False)
        embed.add_field(name=f"```/stats [username]```", value='Show stats stats for a specific user', inline=False)
        embed.add_field(name=f"```/bsc```", value='View the bristol stool chart, for your reference', inline=False)
        embed.add_field(name=f"```/justpooped```", value=f'Log your recent {random.choice(config.POOP_SYNONYMS)} experience', inline=False)
        embed.add_field(name=f"```/minigame```", value=f'Play a {random.choice(config.POOP_SYNONYMS)} themed minigame', inline=False)
        embed.add_field(name=f"```/trivia```", value=f'Play a {random.choice(config.POOP_SYNONYMS)} trivia minigame!', inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @log_execution_time
    async def show_stats(self, interaction: discord.Interaction, username: discord.Member = None):
        if username:
            if username.id == interaction.user.id:
                await self.show_user_stats(interaction, username)
            elif config.PUBLIC_STATS == True:
                await self.show_user_stats(interaction, username)
            else:
                await self.stats_perm_denied(interaction) # deny if config.public_stats false and trying to view other user stats
        else:
            await self.show_server_stats(interaction)

    @log_execution_time
    async def stats_perm_denied(self, interaction: discord.Integration):
        embed = discord.Embed(title=f"❌ Permission denied", color=discord.Color.red())
        embed.add_field(name=f"", value=f"This server does not allow the viewing of other peoples {random.choice(config.POOP_SYNONYMS)} statistics", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @log_execution_time
    async def show_user_stats(self, interaction: discord.Interaction, username: discord.Member):
        cursor.execute(f'SELECT * from poops WHERE discord_id = {username.id} ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        poop_count = len(rows)
        if(poop_count < 1):
            await interaction.response.send_message(f"No {random.choice(config.POOP_SYNONYMS)}s logged yet!", ephemeral=True)
            return 

        last_poop = datetime.fromtimestamp(rows[0][5]).strftime('%Y-%m-%d %H:%M:%S')
        timestamps = [datetime.fromtimestamp(row[5]) for row in rows]
        poop_ratings = [row[3] for row in rows]
        bsc_ratings = [row[4] for row in rows]
        avg_rating = sum(poop_ratings) / len(poop_ratings)

        graph_buf = await graph.rating_vs_bsctype(timestamps, poop_ratings, bsc_ratings)

        embed_color = self.get_embed_color(avg_rating)
        embed = discord.Embed(title=f"🧑 {username}'s {random.choice(config.POOP_SYNONYMS)} statistics", color=embed_color)
        embed.add_field(name=f"Number of {random.choice(config.POOP_SYNONYMS)}s", value=f"{poop_count} {random.choice(config.POOP_SYNONYMS)}s", inline=False)
        embed.add_field(name=f"Last {random.choice(config.POOP_SYNONYMS)}", value=f"{self.time_since(rows[0][5])}", inline=False)
        embed.add_field(name="Average rating", value=f"**{round(avg_rating, 2)} {config.RATING_EMOJIS[round(avg_rating, 0)]}**", inline=False)
        if config.ENABLE_GRAPH:
            embed.set_image(url='attachment://graph.png')
            file = discord.File(fp=graph_buf, filename='graph.png')
        else:
            file = None

        view = StatisticsView()
        if file:
            await interaction.response.send_message(embed=embed, file=file, view=view)
        else:
            await interaction.response.send_message(embed=embed, view=view)

    @log_execution_time
    async def show_server_stats(self, interaction: discord.Interaction):
        cursor.execute(f'SELECT discord_id, COUNT(*) AS count FROM poops GROUP BY discord_id ORDER BY count DESC LIMIT 3')
        user_poop_counts = cursor.fetchall()
        poop_count_list = [{discord_id: count} for discord_id, count in user_poop_counts]

        cursor.execute(f'SELECT * from poops ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        poop_count = len(rows)
        if(poop_count < 1):
            await interaction.response.send_message(f"No {random.choice(config.POOP_SYNONYMS)}s logged yet!", ephemeral=True)
            return

        last_poop = datetime.fromtimestamp(rows[0][5]).strftime('%Y-%m-%d %H:%M:%S')
        last_pooper = await self.fetch_user(rows[0][1])
        poop_ratings = [row[3] for row in rows]
        avg_rating = sum(poop_ratings) / len(poop_ratings)

        embed_color = self.get_embed_color(avg_rating)
        embed = discord.Embed(title=f"🌐 This server's {random.choice(config.POOP_SYNONYMS)} statistics", color=embed_color)
        embed.add_field(name=f"Number of {random.choice(config.POOP_SYNONYMS)}s", value=f"{poop_count} {random.choice(config.POOP_SYNONYMS)}s on this server", inline=False)
        embed.add_field(name=f"Last {random.choice(config.POOP_SYNONYMS)}", value=f"{self.time_since(rows[0][5])} by **{last_pooper}**", inline=False)
        embed.add_field(
            name=f"Top {random.choice(config.POOP_SYNONYMS)}-ers:",
            value="\n".join([f"{idx}. **{await bot.fetch_user(discord_id)}**: {count} poops" for idx, (discord_id, count) in enumerate(user_poop_counts, start=1)]),
            inline=False
        )
        embed.add_field(name="Average rating", value=f"**{round(avg_rating, 2)} {config.RATING_EMOJIS[round(avg_rating, 0)]}**", inline=False)

        await interaction.response.send_message(embed=embed)

    @log_execution_time
    async def show_bsc(self, interaction: discord.Interaction):
        chart_image_url = "https://data.templateroller.com/pdf_docs_html/183/1830/183010/bristol-stool-chart_print_big.png"
        embed = discord.Embed(title="Bristol Stool Chart", color=discord.Color.orange())
        embed.set_image(url=chart_image_url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @log_execution_time
    async def log_poop(self, interaction: discord.Interaction):
        chart_image_url = "https://data.templateroller.com/pdf_docs_html/183/1830/183010/bristol-stool-chart_print_big.png"
        embed = discord.Embed(title=f"{random.choice(config.JUST_POOPED_TITLE)}", description="Refer to the Bristol Stool Chart and describe your experience.")
        embed.set_image(url=chart_image_url)

        view = JustPoopedView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @staticmethod
    def get_embed_color(avg_rating):
        if avg_rating < 5:
            return discord.Color.red()
        elif avg_rating < 8:
            return discord.Color.yellow()
        else:
            return discord.Color.green()

    @staticmethod
    def time_since(timestamp):
        timestamp = datetime.fromtimestamp(timestamp)
        time_diff = datetime.now() - timestamp

        years = time_diff.days // 365
        days = time_diff.days % 365
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        parts = []
        if years > 0:
            parts.append(f"{years} years")
        if days > 0:
            parts.append(f"{days} days")
        if hours > 0:
            parts.append(f"{hours} hours")
        if minutes > 0:
            parts.append(f"{minutes} minutes")

        return ", ".join(parts) + " ago" if parts else "just now"


class JustPoopedModal(discord.ui.Modal, title="Just Pooped"):

    poop_description = discord.ui.TextInput(
        label="🤔 How was the experience?",
        placeholder="Be detailed",
        style=discord.TextStyle.long,
        required=True
    )
    poop_rating = discord.ui.TextInput(
        label="🚦 Rating (1-10)",
        placeholder="Rate your butt brownies out of 10...",
        style=discord.TextStyle.short,
        required=True
    )
    bristol_type = discord.ui.TextInput(
        label="💩 Bristol Stool Chart Type (1-7)",
        placeholder="Enter a number from 1 to 7...",
        style=discord.TextStyle.short,
        required=True
    )

    @log_execution_time
    async def on_submit(self, interaction: discord.Interaction):
        try:
            rating = int(self.poop_rating.value)
            if rating < 1 or rating > 10:
                await interaction.response.send_message("Please provide a rating between 1 and 10.", ephemeral=True)
                return
        except ValueError:
            await interaction.response.send_message("Invalid rating. Please provide a number between 1 and 10.", ephemeral=True)
            return

        try:
            bristol_type = int(self.bristol_type.value)
            if bristol_type < 1 or bristol_type > 7:
                await interaction.response.send_message("Please provide a number between 1 and 7.", ephemeral=True)
                return
        except ValueError:
            await interaction.response.send_message("Invalid Bristol Stool Chart type. Provide a number between 1 and 7.", ephemeral=True)
            return

        embed_color = JustPoopedBot.get_embed_color(rating)
        embed = discord.Embed(title=f"{interaction.user.name}'s {random.choice(config.POOP_SYNONYMS)}s", color=embed_color)
        embed.add_field(name=f"🤔 Description", value=f"```{self.poop_description.value}```", inline=False)
        embed.add_field(name="🚦Rating", value=f"**{rating}/10 {config.RATING_EMOJIS[rating]}**", inline=False)
        embed.add_field(name="💩 Bristol Stool Chart", value=f"**{bristol_type}** - {config.BRISTOL_STOOL_CHART[bristol_type]}", inline=False)
        embed.add_field(name="🤖 says", value=f"*''{config.RATING_ADVICE[rating]}''*", inline=False)

        await interaction.response.send_message(embed=embed)

        user_id = interaction.user.id
        cursor.execute(
            '''INSERT INTO poops (discord_id, poop_description, poop_rating, bristol_type, timestamp) VALUES (?, ?, ?, ?, ?)''',
            (user_id, self.poop_description.value, rating, bristol_type, interaction.message.created_at.timestamp())
        )
        conn.commit()

class JustPoopedView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Open the form", style=discord.ButtonStyle.primary)
    async def open_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(JustPoopedModal())

class StatisticsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label=f"View my {random.choice(config.POOP_SYNONYMS)}s!", style=discord.ButtonStyle.primary)
    async def create_thread(self, interaction: discord.Interaction, button: discord.ui.Button):
        start_time = time.time()

        thread = await interaction.channel.create_thread(
            name=f"{interaction.user.name}'s {random.choice(config.POOP_SYNONYMS)}s!",
            type=discord.ChannelType.public_thread,
            auto_archive_duration=60,
        )

        cursor.execute(f'SELECT * FROM poops WHERE discord_id = {interaction.user.id} ORDER BY timestamp ASC LIMIT 100')
        rows = cursor.fetchall()

        for idx, row in enumerate(rows, start=1):
            embed_color = JustPoopedBot.get_embed_color(row[3])
            embed = discord.Embed(title=f"💩 #{idx}", color=embed_color)
            embed.add_field(name="📝 Description", value=f"```{row[2]}```", inline=False)
            embed.add_field(name="🚦 Rating", value=f"**{row[3]}/10 {config.RATING_EMOJIS[row[3]]}**", inline=False)
            embed.add_field(name="💩 Bristol Type", value=f"**{row[4]}** - {config.BRISTOL_STOOL_CHART[row[4]]}", inline=False)
            embed.add_field(name="🕓 Time taken", value=f"{JustPoopedBot.time_since(row[5])}", inline=False)

            await thread.send(embed=embed)
            await asyncio.sleep(0.5)

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] create_thread executed in {elapsed_time:.4f} seconds")

class TriviaView(discord.ui.View):
    def __init__(self, expected_answer, interaction):
        super().__init__(timeout=None)
        self.expected_answer = expected_answer
        self.interaction = interaction
        self.game_ended = False
    
    async def handle_button(self, interaction: discord.Interaction, button: discord.ui.Button, answer: str):
        self.game_ended = True
        self.clear_items()
        if self.expected_answer == answer:
            await self.win_state(answer, interaction)
        else:
            await self.lose_state(answer, interaction)
    
    @discord.ui.button(label="A", style=discord.ButtonStyle.primary)
    async def a(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_button(interaction, button, "A")

    @discord.ui.button(label="B", style=discord.ButtonStyle.primary)
    async def b(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_button(interaction, button, "B")

    @discord.ui.button(label="C", style=discord.ButtonStyle.primary)
    async def c(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_button(interaction, button, "C")

    @discord.ui.button(label="D", style=discord.ButtonStyle.primary)
    async def d(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_button(interaction, button, "D")

    
    async def win_state(self, answer, interaction: discord.Interaction):
        new_embed = discord.Embed(title=f"✅ {random.choice(config.MINIGAME_WIN_TITLE)}", description=f"Correct! The answer was {answer}.", color=discord.Color.green())
        await self.interaction.edit_original_response(embed=new_embed, view=self)

    async def lose_state(self, answer, interaction: discord.Interaction):
        new_embed = discord.Embed(title=f"❌ {random.choice(config.MINIGAME_LOSE_TITLE)}", description=f"Incorrect! The correct answer was {self.expected_answer}, but you answered {answer}.", color=discord.Color.red())
        await self.interaction.edit_original_response(embed=new_embed, view=self)

    
class MinigameView(discord.ui.View):
    def __init__(self, index, toilet_pos, interaction):
        super().__init__(timeout=None)
        self.index = index
        self.toilet_pos = toilet_pos
        self.interaction = interaction
        self.game_ended = False

    @discord.ui.button(label="Drop the poop", style=discord.ButtonStyle.primary)
    async def dropper(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.game_ended = True
        self.clear_items()
        if self.index == self.toilet_pos:
            new_embed = discord.Embed(
                title=f"{random.choice(config.MINIGAME_WIN_TITLE)}", description=f"You successfully dropped the {random.choice(config.POOP_SYNONYMS)} in the toilet!", color=discord.Color.green())
            await self.interaction.followup.send(embed=new_embed, view=self)
        else:
            sad_emoji = config.RATING_EMOJIS[random.choice(list(config.RATING_EMOJIS.keys())[:4])]
            new_embed = discord.Embed(
                title=f"{random.choice(config.MINIGAME_LOSE_TITLE)}", description=f"The poop fell on the floor! {sad_emoji}", color=discord.Color.red())
            await self.interaction.followup.send(embed=new_embed, view=self)
            
intents = discord.Intents.default()
intents.message_content = True
bot = JustPoopedBot(command_prefix="!", intents=intents)
bot.run(config.TOKEN)
