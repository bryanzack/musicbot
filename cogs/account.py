""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 6.1.0
"""

from discord.ext import commands
from discord.ext.commands import Context
import aiosqlite
import os


# Here we name the cog and create a new class for the cog.
class Account(commands.Cog, name="account"):
    def __init__(self, bot) -> None:
        self.bot = bot

    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.

    @commands.hybrid_command(
        name="link",
        description="links last.fm account name to bot database.",
    )
    async def link(self, context: Context, arg) -> None:
        id = context.author.id
        print(f"id: {id}")
        print(f"fmname: {arg}")
        async with aiosqlite.connect(
            f"{os.path.realpath(os.path.dirname(__file__))}/../database/database.db"
        ) as db:
            async with db.execute(f"SELECT * FROM User WHERE Discord_ID = {id}") as select_cursor:
                select_rows = await select_cursor.fetchall()
                print(select_rows)
                if (len(select_rows) == 0):
                    await db.execute(f"INSERT INTO User values ({id}, '{arg}')")
                    await db.commit()
                    await context.send(f'user linked last.fm account "{arg}"')
                else:
                    print('name test')
                    print(arg)
                    print(select_rows[0][1])
                    if (arg != select_rows[0][1]):
                        await db.execute(f"UPDATE User SET Lastfm_Name = '{arg}' WHERE Discord_ID = {id}")
                        await db.commit()
                        await context.send(f'user switched link to last.fm account "{arg}"')
                    else:
                        await context.send('user already has this account linked')


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(Account(bot))
