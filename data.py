import pymysql.cursors
from config import host, port, user, passkey, database

connection = pymysql.connect(
    host=host,
    port=port,
    user=user,
    password=passkey,
    database=database,
    cursorclass=pymysql.cursors.DictCursor
)

with connection.cursor() as cursor:
    insert_query = """SELECT * FROM users"""
    cursor.execute(insert_query)
    rows = cursor.fetchall()
    for row in rows:
        print(row)
