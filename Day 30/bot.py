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
    
@bot.command()
async def deposit(ctx, amount = None):
    await open_account(ctx.author)
    
    if amount == None:
        await ctx.send("請輸入數字")
        return 
    bal = await update_bank(ctx.author)
    amount = int(amount)
    if bal[1] + amount >= 5000:
        await ctx.send("加進去總額超過5000不能再存囉")
        return
    if amount > bal[0]:
        await ctx.send("你沒這麼多錢拉幹")
        return 
    if amount > 200:
        await ctx.send("要小於200喔")
    if amount< 0:
        await ctx.send("北七喔，錢有負的喔")
        return

    await update_bank(ctx.author, -1*amount)
    await update_bank(ctx.author, amount, "bank")
    
    await ctx.send(f"你存了 {amount} 塊錢!!!")
    
@bot.command()
async def send(ctx, member:discord.Member, amount = None):
    await open_account(ctx.author)
    await open_account(member)
    
    if amount == None:
        await ctx.send("請輸入數字")
        return 
    bal = await update_bank(ctx.author)
    
    if amount == "all":
        amount = bal[0]
    amount = int(amount)
    if amount > bal[1]:
        await ctx.send("你沒這麼多錢拉幹")
        return 
    if amount< 0:
        await ctx.send("北七喔，錢有負的喔")
        return

    await update_bank(ctx.author, -1*amount, "bank")
    await update_bank(member, amount, "bank")
    member = str(member)
    member = member.split("#")[0]
    await ctx.send(f"你給了{member} {amount} 塊錢!!!")

@bot.command()
async def rw(ctx, member:discord.Member):
    await open_account(ctx.author)
    await open_account(member)
    
    if ctx.author == member:
        await ctx.send("禁止洗錢")
        return
    
    bal = await update_bank(member)
    if bal[0] < 100:
        member = str(member)
        member = member.split("#")[0]
        await ctx.send(f"{member} 的所有錢沒超過100")
        return 
    earnings = random.randrange(0, 100)
    
    await update_bank(ctx.author, earnings)
    await update_bank(member, -1*earnings)
    member = str(member)
    member = member.split("#")[0]
    await ctx.send(f"你搶到 {member} 的 {earnings} 塊錢!!!")

@bot.command()
async def rb(ctx, member:discord.Member):
    await open_account(ctx.author)
    await open_account(member)
    
    if ctx.author == member:
        await ctx.send("禁止搶自己的錢")
        return
    
    bal = await downdate_bank(member)
    if bal[1] < 100:
        member = str(member)
        member = member.split("#")[0]
        await ctx.send(f"{member} 銀行裡的所有錢沒超過100")
        return 
    earnings = random.randrange(0, 100)
    
    await downdate_bank(ctx.author, earnings)
    await downdate_bank(member, -1*earnings)
    member = str(member)
    member = member.split("#")[0]
    await ctx.send(f"你搶到 {member} 存在銀行裡的 {earnings} 塊錢!!!")

@bot.command()
async def slots(ctx, amount = None, mang = None):
    await open_account(ctx.author)
    if amount == None:
        await ctx.send("請輸入數字")
        return 
    bal = await update_bank(ctx.author)
    amount = int(amount)
    mang = int(mang)
    if bal[0] <= 0:
        await ctx.send("沒錢的，滾拉")
        return 
    if amount > bal[0]:
        await ctx.send("你沒這麼多錢拉幹")
        return
    if amount< 0:
        await ctx.send("正整數...")
        return
    if amount > 200 or mang > 10 :
        await ctx.send("不接受太高金額及倍率，最高為199$$") 
        return
    final = []
    for i in range(3):
        a = random.choice(["X", "O", "Q"])
        final.append(a)
    ans = mang * amount
    pos = mang * amount * -1
    if final[0] == final[1] == final[2]:
        await update_bank(ctx.author, ans)
        await ctx.send("想贏嗎??")
        asyncio.sleep(3)
        await ctx.send(str(final))
        await ctx.send(f"你贏了 {ans} 塊錢")  
    else:
        await update_bank(ctx.author, pos)
        await ctx.send("想贏嗎??")
        asyncio.sleep(3)
        await ctx.send(str(final))
        await ctx.send(f"你輸了 {pos} 塊錢")

@bot.command()
async def bag(ctx):
    await open_account(ctx.author)
    user = ctx.author    
    users = await get_bank_data()
    
    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []
    
    em = discord.Embed(title = "Bag", color = 0xFF5733)
    em.set_thumbnail(url = user.avatar_url)
    for item in bag:
        name = item["item"]
        amount = item["amount"]
        
        em.add_field(name = name, value = amount)
    await ctx.send(embed = em)

@bot.command()
async def buy(ctx, item, amount = 1):
    await open_account(ctx.author)
    
    res = await buy_this(ctx.author, item, amount)
    
    if not res[0]:
        if res[1] == 1:
            await ctx.send("沒有這個東西喔")
            return
        if res[1] == 2:
            await ctx.send(f"你的錢包裡沒有足夠的錢去買 {item}")
            return
        
    await ctx.send(f"你買到了 {amount} x{item}")



@bot.command()
async def sell(ctx,item,amount = 1):
    await open_account(ctx.author)

    res = await sell_this(ctx.author,item,amount)

    if not res[0]:
        if res[1]==1:
            await ctx.send("沒有這個東西!")
            return
        if res[1]==2:
            await ctx.send(f"你沒有 {amount}個{item} 在你的包裡.")
            return
        if res[1]==3:
            await ctx.send(f"你沒有 {item} 在你的包.")
            return

    await ctx.send(f"你賣了 {amount}個{item}.")



@bot.command(aliases = ["lb"])
async def leaderboard(ctx,x = 1):
    users = await get_bank_data()
    leader_board = {}
    total = []
    for user in users:
        name = int(user)
        total_amount = users[user]["wallet"] + users[user]["bank"]
        leader_board[total_amount] = name
        total.append(total_amount)

    total = sorted(total ,reverse=True)    

    em = discord.Embed(title = f"前{x}個有錢的傢伙" , description = "在銀行與錢包的總和排名",color = 0xfa43ee)
    em.set_thumbnail(url = "https://imgur.com/rudjq8G.gif")
    index = 1
    for amt in total:
        id_ = leader_board[amt]
        member = await bot.fetch_user(id_)
        name = member.name
        em.add_field(name = f"{index}. {name}" , value = f"{amt}",  inline = False)
        if index == x:
            break
        else:
            index += 1

    await ctx.send(embed = em)

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
    embed.add_field(name = "!money", value = "看錢包裡有多少錢", inline = True)
    embed.add_field(name = "!bag", value = "包包", inline = True)
    embed.add_field(name = "!beg", value = "乞討中(ing)", inline = True)
    embed.add_field(name = "!withdraw", value = "提款", inline = True)
    embed.add_field(name = "!deposit", value = "存錢", inline = True)
    embed.add_field(name = "!send", value = "匯款 @某人", inline = True)
    embed.add_field(name = "!rw", value = "搶劫，@人，錢包", inline = True)
    embed.add_field(name = "!rb", value = "搶劫，@人，銀行", inline = True)
    embed.add_field(name = "!slots", value = "賭博，可以自己設定賭注跟倍率", inline = True)
    embed.add_field(name = "!market", value = "看能買甚麼", inline = True)
    embed.add_field(name = "!buy", value = "買東西，ex: 手錶之類的", inline = True)
    embed.add_field(name = "!sell", value = "賣東西", inline = True)
    embed.add_field(name = "!lb", value = "排行榜", inline = True)
    embed.set_footer(text = "use this to have fun")
    await ctx.send(embed = embed)

async def sell_this(user,item_name,amount,price = None):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            if price==None:
                price = 0.9* item["price"]
            break

    if name_ == None:
        return [False,1]

    cost = price*amount

    users = await get_bank_data()

    bal = await update_bank(user)
    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt - amount
                if new_amt < 0:
                    return [False,2]
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index+=1 
        if t == None:
            return [False,3]
    except:
        return [False,3]    

    with open("mainbank.json","w") as f:
        json.dump(users,f)

    await update_bank(user,cost,"wallet")

    return [True,"Worked"]

async def buy_this(user, item_name, amount):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            price = item["price"]
            break
    
    if name_ == None:
        return [False, 1]
    
    cost = price * amount
    
    users = await get_bank_data()
    bal = await update_bank(user)
    
    if bal[0] < cost:
        return [False, 2]
    
    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt + amount
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index += 1
        
        if t == None:
            obj = {"item": item_name, "amount": amount}
            users[str(user.id)]["bag"].append(obj)
    except:
        obj = {"item": item_name, "amount": amount}
        users[str(user.id)]["bag"] = [obj]
    with open("Json//mainbank.json", "w") as f:
        json.dump(users, f)
    
    await update_bank(user, cost*-1, "wallet")
    return [True, "worked"]
  
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

    with open("Json//mainbank.json", "w") as f:
        json.dump(users, f)
    bal = [users[str(user.id)]["wallet"], users[str(user.id)]["bank"]]    
    return bal


async def downdate_bank(user, change = 0, mode = "bank"):
    users = await get_bank_data()
    users[str(user.id)][mode] += change

    with open("Json//mainbank.json", "w") as f:
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