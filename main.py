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
CONNECTION_STRING = os.getenv("CONNECTION_STRING")
GOOGLE_SHEET_LINK = os.getenv("GOOGLE_SHEET_LINK")
DDAY_COMMAND = os.getenv("DDAY_COMMAND")

#setting up mongo DB    
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.neuraldb
students = db.student

#roles
verified_role = 1148751191409430588
section_role = 1149348634828210176
#checking that we are connected to the database
try:
    client.admin.command('ping')
    print("connected to the database")
except Exception as e:
    print(e)

#initializing the bot
intents = discord.Intents.all()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)
guild_id = 1148742430800228432

#on ready
@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=guild_id))
    print('[DONE]: We have logged in as {0.user}'.format(bot))

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

    if str(your_id) in section_Ids_List and (str(your_id) not in db_list): 
        #create the student obejct
        student = {
            "matricule": int(your_id),
            "name": str(your_name),
            "surname": str(your_surname)
        }

        #insert the student object in the db
        students.insert_one(student)

        #interact with the student
        await interaction.response.send_message(f"{interaction.author.mention} WELCOME TO THE: `{your_name}`")
        await interaction.user.add_roles(sec_role)
    if str(your_id) in section_Ids_List and (str(your_id) in db_list):
        await interaction.response.send_message(f"{interaction.author.mention} WTF ARE U DOING !")
    else:
        await interaction.response.send_message(f"{interaction.author.mention} GET THE FUCK OUT !")

#the doom command
@bot.event
async def on_message(message):
    #check that the bot can't reply to himself
    if message.author == bot.user:
        return

    #starting the doom command
    if message.content.startswith(DDAY_COMMAND):
        #getting the verified role
        ver_role = message.guild.get_role(verified_role)
        #setting permissions
        overwrite = discord.PermissionOverwrite()
        overwrite.view_channel = False
        for guild in bot.guilds:
            for channel in guild.channels:
                await channel.set_permissions(ver_role, overwrite=overwrite)
            
bot.run(TOKEN)
