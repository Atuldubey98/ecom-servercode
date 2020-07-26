from flask import Flask, jsonify
import json
app = Flask(__name__)


@app.route("/")
def checkServerStatus():
    print("Server Running")
    return jsonify({"status" : "ok" , "data" : {} , "error" : {}})


@app.route("/getgrocery")
def getgrocery():
    f = open("grocery.json")
    data = json.load(f)
  
    return jsonify({"status" : "ok" , "data" : data , "error" : {}})

@app.route("/getnokiaphone")
def getnokiaphone():
    f = open("nokiaphone.json")
    data = json.load(f)
    
    return jsonify({"status" : "ok" , "data" : data , "error" : {}})

@app.route("/getsearchspring")
def getsearchspring():
    f = open("searchspring.json")
    data = json.load(f)
    
    return jsonify({"status" : "ok" , "data" : data , "error" : {}})


@app.route("/getshirts")
def getshirts():
    f = open("shirts.json")
    data = json.load(f)
    
    return jsonify({"status" : "ok" , "data" : data , "error" : {}})



if __name__ == "__main__":
   
    app.run(host= "0.0.0.0" , debug= True,)
