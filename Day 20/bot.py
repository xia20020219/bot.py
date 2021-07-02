from discord.ext import commands
from discord import Member
import stockweb
import remove_json_and_jpg
import random
import discord
import json
import time
import asyncio

bot = commands.Bot(command_prefix="!")

with open('Json//bot_id.json', "r", encoding = "utf8") as datafile:
    jsondata = json.load(datafile)

lucky = ["lucky~~~", "not bad", "Soso", "green hat"
            , "fuck your self"]
   
mainshop = [{"name": "Watch", "price": 8},
            {"name": "Laptop", "price": 87},
            {"name": "PC", "price": 870},
            {"name": "PS5", "price": 690},
            {"name": "Cat", "price": 1000}
            ]
        
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

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed=discord.Embed(title="未知的指令", color=0xdc2e2e)
        embed.add_field(name="清除", value="!clear + 數字", inline=True)
        await ctx.send(embed=embed)

#!hello    
@bot.command()
async def hello(ctx):
    await ctx.send(f"!Hi <@{ctx.author.id}>")
    
#刪除留言
@bot.command()
async def clear(ctx, num:int):
    await ctx.channel.purge(limit = num+1)
    
#!gura 
@bot.command(pass_context = True)
async def gura(ctx):
    await ctx.send(file = discord.File(jsondata["gura"]))

    
#時間
@bot.command()
async def nt(ctx):
    await ctx.send(time.ctime())

@bot.command()
async def catch(ctx, stock:int):
    stockweb.catchweb(stock)
    await ctx.send(file = discord.File('stock.jpg'))
    remove_json_and_jpg.fileremove_jpg()
    await ctx.send("內存已刪除，可以隨時進行爬蟲")    
    
#刪除+創建match.json
@bot.command()
async def fjson(ctx):
    remove_json_and_jpg.fileremove_match_json()
    remove_json_and_jpg.filecreate_match_json()
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

@bot.command()
async def market(ctx):
    em = discord.Embed(title = "market", color = 0xFF5732)
    em.set_thumbnail(url = "https://www.formula-ai.com/wp-content/uploads/2020/09/python_or_java_meme.jpg")
    
    for item in mainshop:
        name = item["name"]
        price = item["price"]
        em.add_field(name = name, value = f"${price}")
    await ctx.send(embed = em)

@bot.command()
async def money(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()
    
    wallet_amt = users[str(user.id)]["wallet"]
    bank_amt = users[str(user.id)]["bank"]
    
    em = discord.Embed(title = f"{ctx.author.name}'s 錢包", color = discord.Color.red())
    em.set_thumbnail(url = user.avatar_url)
    em.add_field(name = "Wallet", value = wallet_amt)
    em.add_field(name = "Bank", value = bank_amt)
    await ctx.send(embed = em)

@bot.command()
async def beg(ctx):
    await open_account(ctx.author)
    
    users = await get_bank_data()
    user = ctx.author
    earnings = random.randrange(101)
    
    await ctx.send(f"某人給了你 {earnings} 塊錢!!")
    users[str(user.id)]["wallet"] += earnings
    
    with open("mainbank.json", "w") as f:
        json.dump(users, f)

@bot.command()
async def withdraw(ctx, amount = None):
    await open_account(ctx.author)
    if amount == None:
        await ctx.send("請輸入數字")
        return 
    bal = await update_bank(ctx.author)
    amount = int(amount)
    if amount > bal[1]:
        await ctx.send("你沒這麼多錢拉幹")
        return 
    if amount > 200:
        await ctx.send("要小於200喔")
        return
    if amount< 0:
        await ctx.send("北七喔，錢有負的喔")
        return

    await update_bank(ctx.author, amount)
    await update_bank(ctx.author, -1*amount, "bank")
    
    await ctx.send(f"你提款了 {amount} 塊錢!!!")

#等於!help
@bot.command()
async def embed(ctx):
    embed = discord.Embed(title = "指令",  
        description = "指令都在這邊~~~~~~", color = 0xFF5733)
    embed.set_thumbnail(url = "https://www.formula-ai.com/wp-content/uploads/2020/09/python_or_java_meme.jpg")
    embed.add_field(name = "!nt", value = "現在時間", inline = True)
    embed.add_field(name = "!rand", value = "運氣測試", inline = True)
    embed.add_field(name = "!gura", value = "gura.gif", inline = True)
    embed.add_field(name = "!clear", value = "用 !clear + 數字刪訊息", inline = True)
    embed.add_field(name = "!fjson", value = "刪除並 ||重新|| 創鍵json檔", inline = True)
    embed.add_field(name = "!catch", value = "!catch + 數字，爬股票", inline = True)
    embed.add_field(name = "!embed", value = "等於 == !help", inline = True)
    await ctx.send(embed = embed) 
  
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
    with open("json//match.json", "w") as f:
        json.dump(users, f)
    return True, mat

async def match_data(user, mat):
    users = await read_data()
    if mat == 1:
        mat = 2
        return True, mat

async def read_data():
    with open("json//match.json", "r") as f:
        users = json.load(f)
    return users


async def update_bank(user, change = 0, mode = "wallet"):
    users = await get_bank_data()
    users[str(user.id)][mode] += change

    with open("mainbank.json", "w") as f:
        json.dump(users, f)
    bal = [users[str(user.id)]["wallet"], users[str(user.id)]["bank"]]    
    return bal


async def open_account(user):
    users = await get_bank_data()
    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["wallet"] = 0
        users[str(user.id)]["bank"] = 0
    
    with open("Json//mainbank.json", "w") as f:
        json.dump(users, f)
        
    return True

async def get_bank_data():
    with open("Json//mainbank.json", "r")as f:            
        users = json.load(f)
    return users

      
bot.run(jsondata['token']) 