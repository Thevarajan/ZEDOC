from website import create_app
import pymysql

db_config = {
    'user': 'root',
    'password': '2005',
    'host': 'localhost',
    'database': 'capstone',
}

mydb = pymysql.connect(user=db_config['user'], password=db_config['password'], host=db_config['host'], database=db_config['database'])

app = create_app(mydb)
app.secret_key = 'theva&raksh'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)