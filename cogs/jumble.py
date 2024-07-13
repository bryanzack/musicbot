
""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 6.1.0
"""

from discord.ext import commands
from discord.ext.commands import Context

import requests
import json
import aiosqlite
import os
import random
import discord.embeds

# Here we name the cog and create a new class for the cog.
class Jumble(commands.Cog, name="jumble"):
    def __init__(self, bot) -> None:
        self.bot = bot

    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.

    @commands.hybrid_command(
        name="jumble",
        description="Album name guessing game",
    )
    # when someone types the .jumble command, do the following, command prefix is changed in config.json file
    async def px(self, context: Context) -> None:
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
                print(select_rows)
                # if user does not exist in database (zero matching records), tell user to link account
                if (len(select_rows) == 0):
                    await context.send("user does not have last.fm account linked, please link with .link")
                # user has account linked, we will now run the last.fm api logic
                else:
                    # TODO:
                    # 1.) turn response into navigable json
                    albums = requests.get(f"{os.getenv('API_ROOT')}/?method=user.gettopalbums&user={select_rows[0][1]}&api_key={os.getenv('LASTFM_KEY')}&format=json").json()
                    albums_array = albums['topalbums']['album']

                    # 3.) get random album
                    rand = random.choice(albums_array)
                    print(rand)

                    # 5.) deserialize relevant json key/values into variables
                    artist_name =  rand['artist']['name'] 
                    album_name = rand['name']
                    playcount = rand['playcount']
                    rank = rand['@attr']['rank']

                    #print(f"artist: {artist_name}")
                    print(f"album: {album_name}")
                    #print(f"playcount: {playcount}")
                    #print(f"rank: {rank}")

                    # 6.) do shuffle logic
                    substrings = album_name.split(' ')
                    shuffled_substrings = []
                    for substring in substrings:
                        substring_list = list(substring)
                        random.shuffle(substring_list)
                        shuffled_substring = ''.join(substring_list)
                        shuffled_substrings.append(shuffled_substring)
                    result_string = ' '.join(shuffled_substrings).upper()
                    #print(f'shuffled: {result_string}')

                    # 7.) Create embed
                    asdf = discord.Embed(
                        title=f"```{result_string}```",
                        description=f'''
                        **Jumble - Guess the artist**
                        **•**\tYou have **{playcount}** plays on this artist
                        **•**\tThey are rank **{rank}** on your charts
                        ''',
                        type='rich',
                        colour=0x3498db
                    )
                    await context.send(embed=asdf)


                    #print(albums.text)
                    #await context.send(albums.text)



# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(Jumble(bot))
