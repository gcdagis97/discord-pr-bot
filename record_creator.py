import os
import re
from interactions import OptionType

import interactions

with open(".token", "r") as f:
    bot = interactions.Client(token=f.read().strip())


@bot.command(
    name="verify_match",
    description="Log PR match result",
    options=[
        interactions.Option(
            name="user1",
            description="First user",
            type=OptionType.USER,
            required=True,
        ),
        interactions.Option(
            name="user2",
            description="Second user",
            type=OptionType.USER,
            required=True,
        ),
        interactions.Option(
            name="score1",
            description="Score of the first user",
            type=OptionType.INTEGER,
            required=True,
        ),
        interactions.Option(
            name="score2",
            description="Score of the second user",
            type=OptionType.INTEGER,
            required=True,
        ),
    ],
)
async def verify_match(
    ctx: interactions.CommandContext,
    user1: interactions.Member,
    user2: interactions.Member,
    score1: int,
    score2: int,
):
    if user1.id == user2.id:
        await ctx.send("Those are the same person dummy!", ephemeral=True)
        return
    self_user = await ctx.client.get_self_user()
    if user1.id == self_user.id or user2 == self_user.id:
        await ctx.send("The bot can't play hardhat!", ephemeral=True)
        return
    if not all([score1 >= 0, score2 >= 0, score1 + score2 >= 3, score1 + score2 <= 5]):
        await ctx.send("These scores don't add up numnuts!", ephemeral=True)
        return

    if not os.path.exists("active-verification/"):
        os.mkdir("active-verification/")
    if not os.path.exists(f"active-verification/{ctx.guild_id}/"):
        os.mkdir(f"active-verification/{ctx.guild_id}/")
    if not os.path.exists(f"active-verification/{ctx.guild_id}/{ctx.channel_id}/"):
        os.mkdir(f"active-verification/{ctx.guild_id}/{ctx.channel_id}/")

    message = await ctx.send(
        f"Please verify {user1.mention} vs {user2.mention} match result: {score1}-{score2}"
    )
    await message.create_reaction("✅")
    message_id = message.id
    with open(
        f"active-verification/{ctx.guild_id}/{ctx.channel_id}/{message_id}", "a"
    ) as f:
        pass


bot.start()
