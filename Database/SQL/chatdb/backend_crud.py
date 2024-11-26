import mysql.connector

def main():
    # Connect to the MySQL database
    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="Ilikedsci551",
            database="project551"
        )
        print("Connected to the database successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return

    cursor = connection.cursor()

    print("Please enter the SQL query statement and type 'chatbot-exit' to exit:")

    while True:
        # Read user input
        sql_query = input("SQL> ").strip()
        
        # Check for exit command
        if sql_query.lower() == "chatbot-exit":
            print("Successful exit from chatbot!")
            break

        try:
            # Execute SQL query
            cursor.execute(sql_query)
            # Fetch and display results for SELECT queries
            if sql_query.lower().startswith("select"):
                results = cursor.fetchall()
                for row in results:
                    print(row)
            else:
                # Commit changes for non-SELECT queries
                connection.commit()
                print(f"Query executed successfully: {cursor.rowcount} rows affected.")
        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")

    # Close the database connection
    cursor.close()
    connection.close()
    print("Database connection closed.")

# Run the main function
if __name__ == "__main__":
    main()
