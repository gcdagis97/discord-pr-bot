# This example requires the 'message_content' intent.

import asyncio
import datetime as dt
import discord
import os

intents = discord.Intents.default()
intents.message_content = True

def get_active_verifications_list_from_memory():
    """gets a list of (guild_id, channel_id, message_id, verification_type) tuples for each active verification in memory

    Returns:
        List[Tuple[int,int,int,str]]: List of (guild_id, channel_id, message_id, verification_type) tuples
        verification_type is one of "addemoji", "deleteemoji", "addsticker", "deletesticker"
    """
    combos = []
    for guild_id in os.listdir("active-verification"):
        for channel_id in os.listdir(f"active-verification/{guild_id}"):
            for verification in os.listdir(f"active-verification/{guild_id}/{channel_id}"):
                verification_id = verification
                combos.append((int(guild_id), int(channel_id), int(verification_id)))
    return combos

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    while True:
        timeout = 60
        await asyncio.sleep(timeout)

        verification_list = get_active_verifications_list_from_memory()
        for guild_id, channel_id, verification_id in verification_list:
            channel = client.get_channel(channel_id)

            try:
                message = await channel.fetch_message(verification_id)

                if (dt.datetime.now(dt.timezone.utc) - message.created_at).total_seconds() > timeout:
                    reaction_ids = []
                    for reaction in message.reactions:
                        if str(reaction.emoji) == "✅":
                            async for user in reaction.users():
                                reaction_ids.append(user.id)    
                            break
                        print(message.content)

                    m_ids = [m.id for m in message.mentions]
                    if all([m_id in reaction_ids for m_id in m_ids]):
                        await message.channel.send(f"Match result verified.", reference=message)
                        with open("results.csv", "a") as f:
                            message_split = message.content.split()                            
                            
                            player1_id = remove_non_numeric_and_cast(message_split[2])
                            if player2_id is not None:
                                print("Modified string as an integer:", player2_id)

                            player2_id = remove_non_numeric_and_cast(message_split[4])
                            if player2_id is not None:
                                print("Modified string as an integer:", player2_id)

                            player1_user = await client.fetch_user(player1_id)
                            player2_user = await client.fetch_user(player2_id)
                            player1_name = player1_user.name
                            player2_name = player2_user.name
                            
                            player1_score, player2_score = message_split[-1].split("-")

                            timestamp = dt.datetime.now().isoformat()
                            f.write(";".join([timestamp, player1_name, player2_name, player1_score, player2_score])+"\n")
                    else:
                        await message.channel.send(f"Match result not verified - not all players mentioned have reacted with '✅'", reference=message)
                    
                    try:
                        os.remove(f"active-verification/{guild_id}/{channel_id}/{message.id}")
                    except FileNotFoundError:
                        pass

            except discord.errors.NotFound:
                os.remove(f"active-verification/{guild_id}/{channel_id}/{verification_id}")


def remove_non_numeric_and_cast(s):
    s = ''.join(c for c in s if c.isdigit())
    return int(s)


with open(".token", "r") as f:
    client.run(token=f.read().strip())