import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")

mydb = mysql.connector.connect(
    host="10.10.10.9",
    user=DB_USERNAME,
    password=DB_PASSWORD,
    database="goontech"
)

mycursor = mydb.cursor()

mycursor.execute("SELECT * FROM steamhours")

myresult = mycursor.fetchall()

for x in myresult:
    print(x)