from glob import glob
import discord
import requests
import asyncio
import json


client = discord.Client()

showFiat = False
infos = []
adminRole = "admins"
startSymbol = "$"

async def get_price():
    global TokenAddress
    global network
    global showFiat
    global infos

    url = "https://api.dexscreener.io/latest/dex/pairs/"+network+"/"+TokenAddress
    r = requests.get(url)
    json_data = json.loads(r.text)
    infos = json_data["pair"]
    
    if showFiat:
        return str(infos["priceUsd"])
    else :
        return str(infos["priceNative"])

async def refreshStatus(): 
    global showFiat
    while True:
        prix = await get_price()
        if showFiat:
            symbol = "$"
        else:
            symbol = infos["quoteToken"]["symbol"]
        await client.change_presence(activity=discord.Game(name=str(prix) + " " + symbol))
        await asyncio.sleep(5)


@client.event
async def on_ready():
    global TokenAddress
    global network
    global showFiat
    global adminRole
    
    print('We have logged in as {0.user}'.format(client))
    TokenAddress = str(input("Please enter the Pair Address: "))
    network = str(input("Please enter the network as in dexscreener's URL: "))
    adminRole = str(input("Please enter the name of admin's role : ")).lower()
    if(input("How do you want to show the price 1 : USD / 0 : Network's native ): ") == "1"):
        showFiat = True
    else:
        showFiat = False

    client.loop.create_task(refreshStatus())


@client.event
async def on_message(message):
    global TokenAddress
    global adminRole
    global showFiat
    global startSymbol

    if message.author == client.user:
        return
    if (adminRole in [y.name.lower() for y in message.author.roles]):
        if message.content.startswith(startSymbol+'showFiat'):
            showFiat = True
            await message.channel.send("Showing price in fiat")
        
        if message.content.startswith(startSymbol+'showNative'):
            showFiat = False
            await message.channel.send("Showing price in network's native coin")
        
        if message.content.startswith(startSymbol+'setTokenAddr'):
            TokenAddress = str(input("Please enter the Token Address: "))
            await message.channel.send("Token address set to : "+TokenAddress)

        if message.content.startswith(startSymbol+'setNetwork'):
            network = str(input("Please enter the network as in dexscreener's URL: "))
            await message.channel.send("Network set to : "+network)

        if message.content.startswith(startSymbol+'help'):
            await message.channel.send("List of all commands : ")
            await message.channel.send("```\r\n"+startSymbol+"showFiat : Show the price in fiat\r\n"+startSymbol+"showNative : Show the price in native\r\n"+startSymbol+"setTokenAddr : Set the Token Address\r\n"+startSymbol+"setNetwork : Set the network\r\n"+startSymbol+"help : Show this message ```")
            
        if message.content.startswith(startSymbol+'setStartSymbol'):
            splited = message.content.split(" ")
            if len(splited) >= 2:
                startSymbol = splited[1]
                await message.channel.send("Start symbol set to : "+startSymbol)
    else :
        await message.channel.send("You need to be '"+adminRole+"' to use this command")

client.run('<YOUR DISCORD TOKEN>')
