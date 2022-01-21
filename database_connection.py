import psycopg2
"""
# Connect to the database
# The database create table is in a text file called database, just copy and run it in pgadmin
# Need to create a database in pgadmin first and change these parameters into your own details to allow succesful connection
conn = psycopg2.connect(database = 'ai', user = 'postgres', password='password',host='127.0.0.1', port='5432')
# Create a cursor
cursor = conn.cursor()
# Execute the command
cursor.execute('SELECT * FROM traindata')
# Get all the row in traindata
data = cursor.fetchall()
print(data)
# Close connection
conn.close()
"""

# before running this code, you need to make sure that the name exist in the database and change the name variable to the one that you want
try:
    name = 'name'
    conn = psycopg2.connect(database='ai', user='postgres', password='password', host='127.0.0.1', port='5432')
    cursor = conn.cursor()
    query = """SELECT * FROM userdata WHERE username = %s"""
    cursor.execute(query, (name,))
    data = cursor.fetchall()
    print(data)

except (Exception, psycopg2.Error) as error:
    print("Failed executing query", error)
finally:
    if conn:
        cursor.close()
        conn.close()
        print("Database connection close")