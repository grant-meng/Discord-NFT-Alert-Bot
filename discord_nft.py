from discord.ext import tasks
import requests
import discord
import json
import os

client = discord.Client()
TOKEN = ''


### Math & nice functions
def removeCollection(collection):
    os.remove(f"Collection Data/{collection}.json")
    file = open("Collection_FP.json", "r")
    data = json.load(file)
    data.pop(collection)
    file = open("Collection_FP.json", "w")
    file.write(json.dumps(data))
    file.close()



def lowerTargetFloor(collection):
    file = open("Collection_FP.json", "r")
    data = json.load(file)
    target_floor = float(data[collection])
    data[collection] = (target_floor * 0.9)
    file = open("Collection_FP.json", "w")
    file.write(json.dumps(data))
    file.close()


def updateTargetFloor(collection, new_floor):
    file = open("Collection_FP.json", "r")
    data = json.load(file)
    data[collection] = float(new_floor)
    file = open("Collection_FP.json", "w")
    file.write(json.dumps(data))
    file.close()


def getCollection(collection):
    url = f"https://api.opensea.io/api/v1/collection/{collection}"
    response = requests.request("GET", url)
    collection_file = open(f"Collection Data/{collection}.json", "w")
    try:
        collection_file.write(response.text)
        collection_file.close()
        return True
    except:
        collection_file.close()
        removeCollection(collection)
        return False



### Sends message in welcome channel when a new person joins server
# @client.event
# async def on_member_join(member):
#     channel = await client.fetch_channel('939225334509875321')
#     await channel.send(f'Welcome @{member}, to {message.guild.channels.cache.get(channelid)}')


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@tasks.loop(seconds=15)
async def auto_send():
    print("Checking Prices...")
    channel = await client.fetch_channel('954506174651306004')
    file = open("Collection_FP.json", "r")
    data = json.load(file)
    for collection in data:
        bool = getCollection(collection)
        if bool:
            try:
                collection_file = open(f"Collection Data/{collection}.json", "r")
                collection_data = json.load(collection_file)
                floor_price = collection_data["collection"]["stats"]["floor_price"]
                collection_name = collection_data["collection"]["primary_asset_contracts"][0]["name"]
                collection_file.close()

                if floor_price <= data[collection]:
                    await channel.send(f"@everyone {collection_name} just hit a floor price of {floor_price}! https://opensea.io/collection/{collection}")
                    lowerTargetFloor(collection)
            except Exception as e:
                print(f"something went wrong with {collection} because of {e}")
                continue
        else: 
            await channel.send(f"Something went wrong with {collection}. It has been deleted.")
    file.close()



### On_Message Commands 
### and Logs


@client.event
async def on_message(message):

### Chat Logs
    username = str(message.author).split('#')[0]
    user_message = str(message.content)
    channel = str(message.channel.name)
    print(f'{username}: {user_message} ({channel})')

### Makes sure it doesnt respond to itself
    if message.author == client.user:
        return

### Only works if the message is in the 'nft-buy-floor' channel
    if message.channel.name == '📉nft-buy-floor':
        message_split = user_message.split(' ')

        ### These are global variables used throughout multiple commands
        file = open("Collection_FP.json", "r")
        data = json.load(file)

### Reads to command !add. It takes a collection and new floor price and adds that to the Collection_FP.json file.
### It does check for any errors like non existing collections or wrong command format used.
        if message_split[0] == '!add':
            if len(message_split) == 3:
                if message_split[1] not in data:
                    data.update({message_split[1]: float(message_split[2])})
                    file = open("Collection_FP.json", "w")
                    file.write(json.dumps(data))
                    if getCollection(message_split[1]):
                        await message.channel.send(f'{message_split[1]} has been added!')
                    else: 
                        await message.channel.send(f'There was a problem adding {message_split[1]} make sure the format is correct!')
                else:
                    await message.channel.send(f'That collection already exists with a floor limit of {data[message_split[1]]}. Update floor limit using [!add (collection) (limit_floor)]')
            else:
                await message.channel.send('Format for adding floor price purchase limit: !add (collection_slug) (limit_floor_price)')
                    

### Reads to command !update. It takes a collection and new floor price and updates that to the Collection_FP.json file.
### It does check for any errors like non existing collections or wrong command format used.
        if message_split[0] == '!update':
            if len(message_split) == 3:
                if message_split[1] in data:
                    updateTargetFloor(message_split[1], message_split[2])
                    await message.channel.send(f"{message_split[1]} floor limit has been updated to {message_split[2]}")
                else:
                    await message.channel.send(f'That collection does not exists.')
            else:
                await message.channel.send('Format for updating floor price purchase limit: !update (collection_slug) (limit_floor_price)')


### Help Command, shows all possible commands
        if message_split[0] == '!help' or message_split[0] == '!commands' or message_split[0] == '!command':
            msg = "!help - displays all commands\n!add (collection) (limit_floor_price)\n!update (collection) (limit_floor_price)\n!showall - Displays all collections and their floor limit price"
            embedVar = discord.Embed(title="Commands", description=msg, color=0x00ff00)
            await message.channel.send(embed=embedVar)




### Prints out all collections and floor limits
### 
        if message_split[0] == '!showall':
            if len(message_split) == 1:
                str_list = ""
                for coll in data:
                    str_list += (f"{coll} - {data[coll]}\n")
                embedVar = discord.Embed(title="Collections &Floor Limit", description=str_list, color=0x00ff00)
                await message.channel.send(embed=embedVar)


    file.close()



auto_send.start()
client.run('TOKEN')