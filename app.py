from flask import Flask, jsonify, request
from pymongo import MongoClient
import json
from flask_socketio import SocketIO,emit
import bcrypt
app = Flask(__name__)
sio = SocketIO(app)
app.config['SECRET_KEY'] = "hdgjfash"
client = MongoClient(
    "mongodb+srv://atuldubey:08091959@cluster0-isxbl.mongodb.net/<dbname>?retryWrites=true&w=majority")
db = client.Shop
usercart = db.Cart
users = db.users

@sio.on('addtocart')
def addtocart(data):
 
    existingcart = usercart.find_one({"uniqueid" : data['uniqueid']})
    if existingcart is not None:
        existingitem = usercart.find_one({"title" :  data["title"]})
        if existingitem is None:
            usercart.insert_one({"uniqueid" : data["uniqueid"] , "title" : data["title"] , "qty" : 1, "itemid" : data["itemid"], "price" : data['price']})
        else :
            updateditem = existingitem['qty'] + data['qty']
            if updateditem == 0 :
                usercart.delete_one({"uniqueid" : existingitem['uniqueid'], "title" : existingitem['title']})
            else:
                item = {"uniqueid" : existingitem["uniqueid"] , "title" : existingitem["title"] , "qty" : updateditem, "itemid" : data["itemid"]}
                usercart.update_one({"uniqueid" : existingitem["uniqueid"] , "title" : existingitem['title']}, {"$set" : item})
    else :
        usercart.insert_one({"uniqueid" : data["uniqueid"] , "title" : data["title"] , "qty" : 1, "itemid" : data["itemid"], "price" : data['price']})
    print("emitting")
    print(data['uniqueid'])
    emit(data['uniqueid'],data, broadcast = True)

@app.route("/orderItem", methods = ['POST'])
def orderItem():
    request_data = request.get_json()
    userItem = request_data['data']
    username = request_data['uniqueid']
    for item in userItem:
        usercart.delete_one({"title" : item, "uniqueid" : username})
    emit(username,"hjufa" , broadcast = True)
    return ({"status" : "ok"  , "data" : "placed"})
@app.route('/getcartlist/<string:uid>')
def getcartlist(uid):
    usercartitem = usercart.find_one({"uniqueid" : uid})
    usercartlist = []
    if usercartitem is None:
        return jsonify({"status" : "ok" , "mess" : "additemtocart" , "data" : "NO"})
    for items in usercart.find({"uniqueid" : uid}):
        itemtoadd = {"title" : items["title"] , "qty" : items['qty'] , "itemid" : items['itemid'], "price" : items['price'] * items['qty']}
        usercartlist.append(itemtoadd)
    return jsonify({"stats" : "ok" , "mess" : "yes" , "data" : usercartlist})
@app.route("/")
def checkServerStatus():
    print("Server Running")
    return jsonify({"status" : "ok" , "data" : {} , "error" : {}})


@app.route("/getgrocery")
def getgrocery():
    f = open("grocery.json")
    itemList = []
    data = json.load(f)
    for item in data:
        if (item['title'] == "Italian ciabatta" or item['type'] == "dairy"):
            itemList.append(item)
        print(itemList)
    return jsonify({"status" : "ok" , "data" : data , "error" : {}})


@app.route('/login', methods=['POST'])
def loginuser():
    request_data = request.get_json()
    username = request_data['user']
    password = request_data['password']
    existing_user = users.find_one({'user': username})
    if existing_user is None:
        return jsonify({"status": "notok", "mess": "user does not exist"})
    if(bcrypt.hashpw(password.encode('utf-8'), existing_user['password']) == existing_user['password']):
        return jsonify({"status": "ok", "mess": "user logged in", "user": username, "uid" : existing_user['uniqueid']})
        print("User Logged in", username)
    return jsonify({"status": "notok", "mess": "password incorrect"})

@app.route('/register', methods=['POST'])
def register():
    request_data = request.get_json()
    username = request_data['user']
    password = request_data['password']
    idofuser = request_data['uniqueid']
    existing_user = users.find_one({'user': username})
    if existing_user is None:
        hasspass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        users.insert_one({'user': username, 'password': hasspass, 'uniqueid' : idofuser})
        print("User Registered", username)
        return jsonify({"status": "OK", "mess": "usercreated", "user": username})
    return jsonify({"status": "notok", "mess": "username already exist", 'user': username})


@app.route('/findItem/<string:name>')
def findItem(name):
    f = open('grocery.json')
    data = json.load(f)
    itemList = []
    for item in data:
        if name in item['title'] or name in item['type'] :
            itemList.append(item)
    if itemList is None:
        
        return jsonify({"status" : "noitem" , "mess" : "No item", "data" : {}})
    return jsonify({"status": "ok" , "mess" : "found" , "data" : itemList})
if __name__ == "__main__":
   
    sio.run(app,host= "0.0.0.0" , debug= True,)
