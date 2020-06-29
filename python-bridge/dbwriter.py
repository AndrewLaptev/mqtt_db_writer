import os.path
import paho.mqtt.client as mqtt
import psycopg2
from psycopg2 import sql

broker="172.16.1.2"
port=1883
timelive=60
nametable='lux'

def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))
  client.subscribe("esp32/test/lux")
def on_message(client, userdata, msg):
    con = psycopg2.connect(
        database="postgres",
        user="admin",
        password="admin",
        host="172.16.1.3",
        port="5432"
    )
    print("Database opened successfully")
    cur = con.cursor()
    datedata = msg.payload.decode()
    datedata = datedata.split(" | ")
    cur.execute(sql.SQL("INSERT INTO {} (TIME,VALUE) VALUES (%s, %s)").format(sql.Identifier(nametable)),[datedata[0],datedata[1]])
    print("Record inserted successfully")
    con.commit()
    con.close()

# create table
if (os.path.isfile('./marker.txt')==0):
    f=open("marker.txt","w+")
    f.close()
    con = psycopg2.connect(
        database="postgres",
        user="admin",
        password="admin",
        host="172.16.1.3",
        port="5432"
    )
    cur = con.cursor()
    cur.execute(sql.SQL("CREATE TABLE {} (TIME TEXT PRIMARY KEY NOT NULL, VALUE TEXT NOT NULL)").format(sql.Identifier(nametable)))
    print("Table created successfully")
    con.commit()
    con.close()

client = mqtt.Client()
client.connect(broker,port,timelive)
client.on_connect = on_connect
client.on_message = on_message
client.loop_forever()
