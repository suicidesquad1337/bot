import discord
from discord.ext import commands

class Bot(commands.Bot):

  def __init__(self):
    pass

  def run(self):
    pass
    
  async def on_connect(self):
    pass
    
  async def on_ready(self):
      print(f'Logged in as {self.user.name}')
      print(f'ID: {self.user.id}')
      print(f'Owner: {self.owner}')
