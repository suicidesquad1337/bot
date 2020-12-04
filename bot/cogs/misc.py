import discord
import random
from discord.ext import commands
import aiohttp

class MiscCommands(commands.Cog):
    @commands.group()
    async def random(self, ctx):
        """ All random methods """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    @random.command(name="bool", aliases=["b", "boolean"])
    async def random_bool(self, ctx):
        """ Chooses a random boolean """
        await ctx.send(f"Here you go: {random.random() > 0.5}") # https://stackoverflow.com/questions/6824681/get-a-random-boolean-in-python because its fast (I think)

    @random.command(name="choice", aliases=["c"]) # TODO: Errors when args == 0
    async def random_choice(self, ctx, *, args):
        """ Chooses something random """
        if not len(args):
            await ctx.send("Pls specify a argument!")
        await ctx.send(f"Here you go: {random.choice(args.split(' '))}")

    @random.command(name="dog")
    async def random_cat_picture(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://dog.ceo/api/breeds/image/random") as r:
                if r.status == 200:
                    js = await r.json()
                    await ctx.send(js["message"])
