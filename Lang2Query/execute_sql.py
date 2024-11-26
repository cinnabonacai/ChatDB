import mysql.connector

def execute_sql_query(sql_query):
    """
    Executes an SQL query on the MySQL database and returns the results or status.

    Args:
        sql_query (str): The SQL query to be executed.

    Returns:
        tuple: A tuple where the first element is a boolean indicating success,
               and the second element is the query result or an error message.
    """
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="Ilikedsci551",
            database="project551"
        )
        cursor = connection.cursor()

        # Execute the SQL query
        cursor.execute(sql_query)

        # If the query is a SELECT statement, fetch and return results
        if sql_query.strip().lower().startswith("select"):
            results = cursor.fetchall()
            return True, results
        else:
            # Commit changes for non-SELECT queries
            connection.commit()
            return True, f"{cursor.rowcount} rows affected."

    except mysql.connector.Error as err:
        # Return error details
        return False, str(err)

    finally:
        # Ensure resources are cleaned up
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection:
            connection.close()

# Example function usage
if __name__ == "__main__":
    query = "SELECT * FROM your_table_name;"
    success, result = execute_sql_query(query)
    if success:
        print("Query executed successfully:", result)
    else:
        print("Query execution failed:", result)
