import os
import re
import discord
from discord.ext import commands

# ---------- CONFIG ----------
TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # <-- lee el token desde variable de entorno  
TARGET_BOT_ID = 1194084819915771924  
# -----------------------------

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

money_regex = re.compile(r"\$?([0-9]+(?:\.[0-9]{1,2})?)")

def parse_money(value: str) -> float:
    match = money_regex.search(value)
    return float(match.group(1)) if match else 0.0

def extract_values(embed: discord.Embed):
    tips = ppv = posts = mm = None

    for field in embed.fields:
        name = field.name.lower()

        if "tips" in name:
            tips = parse_money(field.value)
        elif "ppv messages" in name:
            ppv = parse_money(field.value)
        elif "posts" in name:
            posts = parse_money(field.value)
        elif "mm messages" in name:
            mm = parse_money(field.value)

    return tips, ppv, posts, mm

@bot.event
async def on_ready():
    print(f"🔥 Bot conectado como {bot.user}")

@bot.event
async def on_message(message: discord.Message):
    # No responderse a sí mismo
    if message.author.id == bot.user.id:
        return

    await bot.process_commands(message)

    # Solo analizar mensajes de bots
    if not message.author.bot:
        return

    # Filtrar el bot de reportes correcto
    if message.author.id != TARGET_BOT_ID:
        return

    if not message.embeds:
        return

    embed = message.embeds[0]
    tips, ppv, posts, mm = extract_values(embed)

    if None in (tips, ppv, posts, mm):
        return

    chatting = tips + ppv
    schedulers = posts + mm

    respuesta = (
        f"📊 **Resumen de ventas**\n"
        f"🗨️ **Chatting (Tips + PPV):** `${chatting:.2f}`\n"
        f"📅 **Schedulers (Posts + MM):** `${schedulers:.2f}`\n"
        f"\nDetalles:\n"
        f"• Tips: `${tips:.2f}`\n"
        f"• PPV: `${ppv:.2f}`\n"
        f"• Posts: `${posts:.2f}`\n"
        f"• MM Messages: `${mm:.2f}`"
    )

    await message.channel.send(respuesta)

bot.run(TOKEN)
