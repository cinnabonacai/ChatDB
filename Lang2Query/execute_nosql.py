import json
from pymongo import MongoClient
from bson import json_util

def execute_nosql_query(nosql_query, json_file_list):
    """
    Executes a NoSQL query on a MongoDB database and returns the results.

    Args:
        nosql_query (str): The NoSQL query string (e.g., aggregate pipeline or find query).
        json_file_list (list): A list of file paths containing JSON data to import into MongoDB collections.

    Returns:
        tuple: A tuple where the first element is a boolean indicating success,
               and the second element is the query result or an error message.
    """
    try:
        # Connect to MongoDB (default localhost:27017)
        client = MongoClient("mongodb://127.0.0.1:27017/")
        db = client["example_database"]  # Replace with your desired database name

        # Import JSON files into MongoDB collections
        for file_path in json_file_list:
            collection_name = file_path.split("/")[-1].replace(".json", "")
            collection = db[collection_name]

            # Load JSON data from file, parsing with `json_util` for MongoDB compatibility
            with open(file_path, 'r', encoding='utf-8') as json_file:
                data = json_util.loads(json_file.read())
                if isinstance(data, list):
                    collection.insert_many(data)
                else:
                    collection.insert_one(data)

        # Parse and execute the NoSQL query
        # Assuming the query is written as valid Python code (e.g., "db.collection_name.aggregate([...])")
        result = eval(nosql_query, {"db": db})
        print("result: ", result)
        return True, list(result)  # Convert cursor to list for easier handling

    except Exception as err:
        # Return error details
        return False, str(err)

    finally:
        # Close the MongoDB connection
        client.close()

# Example usage
if __name__ == "__main__":
    # Example NoSQL query
    query = "db.city.aggregate([{'$sort': {'CountryCode': -1}}, {'$project': {'Name': 1}}])"
    
    # Example JSON file paths
    json_files1 = [
        "../Database/NoSQL/city.json",
        "../Database/NoSQL/country.json",
        "../Database/NoSQL/countrylanguage.json",
        "../Database/NoSQL/sampleCultureProducts.json"
    ]
    json_files2 = []

    # Execute the query and display results
    success, result = execute_nosql_query(query, json_files2)
    if success:
        print("Query executed successfully:")
        for doc in result:
            print(doc)
    else:
        print("Error executing query:", result)
