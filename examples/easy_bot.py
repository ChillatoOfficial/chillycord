import chillycord

bot = chillycord.Bot(prefix='!')


@bot.hybrid()
async def ping(ctx):
    """Works as both `!ping` and `/ping`."""
    await ctx.send('pong')


@bot.slash(description='Say hello')
async def hello(interaction: chillycord.Interaction):
    await interaction.response.send_message(f'Hello {interaction.user.mention}!')


# Token is read from CHILLYCORD_TOKEN or DISCORD_TOKEN.
# Slash commands are synced on startup only when they changed.
bot.run()
