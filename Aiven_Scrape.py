import pymysql, cryptography, requests, os
from datetime import datetime, timedelta

charset = os.environ.get("DB_CHARSET")
host = os.environ.get("DB_HOST")
password = os.environ.get("DB_PASSWORD")
port = int(os.environ.get("DB_PORT"))
user = os.environ.get("DB_USER")

timeout = 500
connection = pymysql.connect(
    charset=charset,
    connect_timeout=timeout,
    cursorclass=pymysql.cursors.DictCursor,
    db="aharpe22_Project_DB",
    host=host,
    password=password,
    read_timeout=timeout,
    port=port,
    user=user,
    write_timeout=timeout,
)

current_date = datetime.now().date()
previous_date = current_date - timedelta(days=1)

url = "https://raw.githubusercontent.com/AdamSpannbauer/rand-daily-records/master/yesterdays-records.txt"
  
try:
    response = requests.get(url)
    cursor = connection.cursor()

    if response.status_code == 200:
        data = response.text.strip()

        if not data:
            print("Data is blank.")
        else:
            data_lines = data.splitlines()

            for line in data_lines:
                parts = line.strip().split(",")

                salesdate_str = parts[0]
                salesdate = datetime.strptime(salesdate_str, "%Y-%m-%d")
                
                if salesdate.date() != previous_date:
                    print("Sales date does not match the previous date.")
                    break 

                productid = int(parts[1])
                region = parts[2]
                freeship = int(parts[3])
                discount = float(parts[4])
                itemssold = int(parts[5])

                cursor.execute("CREATE TABLE IF NOT EXISTS scrape (id INT AUTO_INCREMENT PRIMARY KEY, salesdate DATE, productid INT, region CHAR(1), freeship INT, discount DECIMAL(3,2), itemssold INT, insert_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")

                insert_script = "INSERT INTO scrape (salesdate, productid, region, freeship, discount, itemssold) VALUES (%s, %s, %s, %s, %s, %s);"

                cursor.execute(insert_script, (salesdate_str, productid, region, freeship, discount, itemssold))

    connection.commit()

finally:
    connection.close()
