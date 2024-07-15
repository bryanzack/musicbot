
""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 6.1.0
"""

from state import game_states
from helpers import shuffleString

from discord.ext import commands
from discord.ext.commands import Context
import requests
import json
import aiosqlite
import os
import random
import discord
import asyncio
import datetime

# Timer logic
async def jumble_timer(self,context:Context, guild_id, message:discord.Message,result_string,playcount,rank):
    try:
        await asyncio.sleep(25)
        if guild_id in game_states:
            embed = discord.Embed(
                title=f"`{result_string}`",
                type='rich',
                colour=discord.Color.red()
            )
            embed.add_field(name='Jumble - Guess the artist', value=f'You have `{playcount}` plays on this artist \n They are rank `{rank}` on your charts', inline=False) 
            embed.add_field(name='', value='', inline=False)
            embed.add_field(name='Add answer', value='Type your answer within 25 seconds to make a guess', inline=False)
            embed.add_field(name=f"Time's up! The correct word was **{game_states[guild_id]['current_word']}**", value='', inline=False)
            await message.edit(embed=embed)
    except asyncio.CancelledError:
        pass
    finally:
        game_states.pop(guild_id, None)

# Button logic
class Buttons(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
    
    # Add hint button
    @discord.ui.button(label="Add hint", style=discord.ButtonStyle.gray, disabled=True)
    async def add_hint(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.send_message("Add hint logic now")

    # Reshuffle button
    @discord.ui.button(label="Reshuffle", style=discord.ButtonStyle.gray)
    async def reshuffle(self,interaction:discord.Interaction,button:discord.ui.Button):
        guild_id = interaction.guild_id
        embed = interaction.message.embeds[0]
        embed.title = f"`{shuffleString(game_states[guild_id]['current_word'])}`"
        await interaction.response.edit_message(embed=embed)

    # Give up button
    @discord.ui.button(label="Give up", style=discord.ButtonStyle.gray, disabled=False)
    async def give_up(self,interaction:discord.Interaction,button:discord.ui.Button):
        guild_id = interaction.guild_id
        message_author = game_states[guild_id]['command_author']
        embed = interaction.message.embeds[0]
        embed.colour = discord.Color.red()
        embed.add_field(name=f'**{message_author} gave up!**', value=f"It was **{game_states[guild_id]['current_word']}**")
        game_states[guild_id]['jumble_task'].cancel()
        await interaction.response.edit_message(embed=embed)

# Command logic
class Jumble(commands.Cog, name="jumble"):
    def __init__(self, bot) -> None:
        self.bot = bot

    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.

    @commands.hybrid_command(
        name="jumble",
        description="Album name guessing game",
    )
    # when someone types the .jumble command, do the following, command prefix is changed in config.json file
    async def jumble(self, context: Context) -> None:
        guild_id = context.guild.id

        id = context.author.id
        # Attempt to find local sqlite3 database
        # 'with' means it will auto close the connection on fail, no need to close manually
        # set database variable to 'db'
        async with aiosqlite.connect(
            f"{os.path.realpath(os.path.dirname(__file__))}/../database/database.db"
        ) as db:
            # check to see if command author's discord ID exists in sqlite3 database
            async with db.execute(f"SELECT * FROM User WHERE Discord_ID = {id}") as select_cursor:
                select_rows = await select_cursor.fetchall()
                # if user does not exist in database (zero matching records), tell user to link account
                if (len(select_rows) == 0):
                    await context.send("user does not have last.fm account linked, please link with .link")
                # user has account linked, we will now run the last.fm api logic
                else:
                    # TODO:
                    # 1.) turn response into navigable json
                    artists = requests.get(f"{os.getenv('API_ROOT')}/?method=user.gettopartists&user={select_rows[0][1]}&api_key={os.getenv('LASTFM_KEY')}&limit=300&format=json").json()
                    #albums = requests.get(f"{os.getenv('API_ROOT')}/?method=user.gettopalbums&user={select_rows[0][1]}&api_key={os.getenv('LASTFM_KEY')}&format=json").json()
                    artists_array = artists['topartists']['artist']
                    

                    # 3.) get random album
                    rand = random.choice(artists_array)

                    # 5.) deserialize relevant json key/values into variables
                    artist_name =  rand['name']
                    playcount = rand['playcount']
                    rank = rand['@attr']['rank']
                    print(f"artist: {artist_name}")

                    # 6.) do shuffle logic
                    result_string = shuffleString(artist_name)

                    # 7.) Create embed
                    embed = discord.Embed(
                        title=f"`{result_string}`",
                        type='rich',
                        colour=discord.Color.blue()
                    )
                    embed.add_field(name='Jumble - Guess the artist', value=f'You have `{playcount}` plays on this artist \n They are rank `{rank}` on your charts', inline=False) 
                    embed.add_field(name='', value='', inline=False)
                    embed.add_field(name='Add answer', value='Type your answer within 25 seconds to make a guess', inline=False)
                    message = await context.send(embed=embed, view=Buttons())

                    game_states[guild_id] = {
                        'command_author': context.message.author,
                        'current_word': artist_name,
                        'jumble_task': asyncio.create_task(jumble_timer(self,context, guild_id, message,result_string,playcount,rank)),
                        'timestamp': datetime.datetime.now(),
                        'channel': context.channel.id
                    }

                    # 8.) Create game state for server



# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(Jumble(bot))