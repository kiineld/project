import pymysql.cursors

connection = pymysql.connect(
    host='26.234.187.103',
    port=3306,
    user="root",
    password="online123",
    database="user_data",
    cursorclass=pymysql.cursors.DictCursor
)

with connection.cursor() as cursor:
    insert_query = """SELECT * FROM users"""
    cursor.execute(insert_query)
    rows = cursor.fetchall()
    for row in rows:
        print(row)
