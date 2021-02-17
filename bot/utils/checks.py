import discord

from .config import BOT_CONFIG


def is_kerkermeister(member: discord.Member) -> bool:
    return any(r.id == BOT_CONFIG.kerkermeister_role_id for r in member.roles)
