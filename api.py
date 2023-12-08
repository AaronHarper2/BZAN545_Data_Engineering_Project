import flask
from flask import request, jsonify
import json
import sqlalchemy
import pandas as pd
import csv

with open("credentials.json") as fp:
    credentials = json.load(fp)

server_details = {
    "host": credentials["host"],
    "port": credentials["port"],
    "username": credentials["username"],
    "password": credentials["password"],
    "database": "aharpe22_Project_DB",
}

# Look up what *args and **kwargs do to further understand the below line
connection_string = sqlalchemy.URL.create("mysql+pymysql", **server_details)
print(connection_string)

engine = sqlalchemy.create_engine(connection_string)

SQLdata = pd.read_sql("SELECT * FROM scrape", engine)
SQLdata.to_csv("SQLdata.csv")

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route("/")
def index():
    return """
        <html>
        <head>
            <style>
                body {
                    background-color: #fffff;
                    font-family: Tahoma, sans-serif;
                    line-height: 1.6;
                }
                div {
                    text-align: center;
                    margin: 50px;
                }
                h1 {
                    font-size: 48px;
                    color: #58595b;
                }
                h2 {
                    color: #ff8200;
                }
            </style>
        </head>
        <body>
            <div>
                <h1>Welcome to our BZAN 545 project API!</h1>
            </div>
            <h2>&nbsp;&nbsp;User Instructions:</h2>
            &nbsp;&nbsp;&nbsp;You can call rows from our database using the endpoints /data with parameters salesdate, region, and freeship.<br><br>
            &nbsp;&nbsp;&nbsp;For salesdate, the user entry must be in the format of YYYY-MM-DD.<br><br>
            &nbsp;&nbsp;&nbsp;For region, the user can select one region of A, B, C, D, or E.<br><br>
            &nbsp;&nbsp;&nbsp;For freeship, the user entry can either be 0 or 1.<br><br><br>
            <h2>&nbsp;&nbsp;Example API calls:</h2>
            &nbsp;&nbsp;&nbsp;http://127.0.0.1:5000/data?salesdate=2023-11-11<br><br>
            &nbsp;&nbsp;&nbsp;http://127.0.0.1:5000/data?salesdate=2023-11-21&ampregion=A&freeship=1
        </body>
        </html>
    """


@app.route("/data")
def get_data():
    salesdate = request.args.get("salesdate")
    region = request.args.get("region")
    freeship = request.args.get("freeship")

    if salesdate and freeship and region:
        query = f"SELECT salesdate, productid, region, freeship, discount, itemssold FROM scrape WHERE salesdate = '{salesdate}' AND freeship = '{freeship}' AND region = '{region}' LIMIT 10;"
    elif salesdate and freeship:
        query = f"SELECT salesdate, productid, region, freeship, discount, itemssold FROM scrape WHERE salesdate = '{salesdate}' AND freeship = '{freeship}' LIMIT 10;"
    elif salesdate and region:
        query = f"SELECT salesdate, productid, region, freeship, discount, itemssold FROM scrape WHERE salesdate = '{salesdate}' AND region = '{region}' LIMIT 10;"
    elif freeship and region:
        query = f"SELECT salesdate, productid, region, freeship, discount, itemssold FROM scrape WHERE freeship = '{freeship}' AND region = '{region}' LIMIT 10;"
    elif salesdate:
        query = f"SELECT salesdate, productid, region, freeship, discount, itemssold FROM scrape WHERE salesdate = '{salesdate}' LIMIT 10;"
    elif freeship:
        query = f"SELECT salesdate, productid, region, freeship, discount, itemssold FROM scrape WHERE freeship = '{freeship}' LIMIT 10;"
    elif region:
        query = f"SELECT salesdate, productid, region, freeship, discount, itemssold FROM scrape WHERE region = '{region}' LIMIT 10;"
    else:
        return {"message": "Please provide at least one of salesdate, region, or freeship parameters."}, 400

    result = pd.read_sql(query, engine)
    return jsonify(result.to_dict()), 200

if __name__ == "__main__":
    app.run(debug=True)
