from discord.ext import commands
import match_json_remove
import random
import discord
import json
import time

bot = commands.Bot(command_prefix="!")

with open('bot_id.json', "r", encoding = "utf8") as datafile:
    jsondata = json.load(datafile)

lucky = ["lucky~~~", "not bad", "Soso", "green hat"
            , "fuck your self"]
   
        
@bot.event
async def on_ready():
    print("Bot in ready")

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(jsondata["join"])
    await channel.send("Hello")

@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(jsondata["remove"])
    await channel.send("goodbye {member}")
    
@bot.command()
async def hello(ctx):
    await ctx.send(f"!Hi <@{ctx.author.id}>")

@bot.command()
async def clear(ctx, num:int):
    await ctx.channel.purge(limit = num+1)
 
@bot.command(pass_context = True)
async def gura(ctx):
    await ctx.send(file = discord.File(jsondata["gura"]))

@bot.command()
async def nt(ctx):
    await ctx.send(time.ctime())

@bot.command()
async def fjson(ctx):
    match_json_remove.fileremove_match_json()
    match_json_remove.filecreate_match_json()
    await ctx.send("本日運氣已刪除")
   
@bot.command(pass_context = True)
async def rand(ctx):
    users, mat = await write_data(ctx.author, mat = 0)
    if mat == 1:
        get = await match_data(ctx.author, mat) 
        cat = random.randint(0, 4)
        await ctx.send(lucky[int(cat)])
    else:
        await ctx.send("本日次數已用完")
  
async def write_data(user, mat):
    users = await read_data()
    if str(user) in users:
        return False
    
    #find json.key   
    if str(user.id) not in users : 
        users[str(user.id)] = {}
        users[str(user.id)]["count"] = 0
        mat = 1
    
    if users[str(user.id)]["count"] == 0:
        users[str(user.id)] = {}
        users[str(user.id)]["count"] = 1
        mat = 1
    
    
    with open("match.json", "w") as f:
        json.dump(users, f)
  
    return True, mat

async def match_data(user, mat):
    users = await read_data()
    
    if mat == 1:
        mat = 2
        return True, mat
        

async def read_data():
    with open("match.json", "r") as f:
        users = json.load(f)
    return users

        


bot.run(jsondata['token']) 