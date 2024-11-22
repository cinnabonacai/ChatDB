# Function to reformat the JSON files as lists where each line is an element in the list.
def reformat_json_to_list(file_paths):
    reformatted_data = {}
    for file_path in file_paths:
        with open(file_path, "r", encoding="utf-8") as file:
            data = file.readlines()  # Read all lines into a list
            reformatted_data[file_path] = [line.strip() for line in data]  # Strip whitespace and store in a dictionary
    return reformatted_data

# Paths to the uploaded files
file_paths = [
        "../Database/NoSQL/city-mongodb.json",  # 示例文件 1
        "../Database/NoSQL/country-mongodb.json",                 # 示例文件 2
        "../Database/NoSQL/countrylanguage-mongodb.json",             # 示例文件 3
    ]

# Reformatting the JSON files
reformatted_json_data = reformat_json_to_list(file_paths)

# Save the reformatted data back to new files for verification
output_files = {}
for file_path, data in reformatted_json_data.items():
    output_file_path = file_path.replace(".json", "-reformatted.json")
    with open(output_file_path, "w", encoding="utf-8") as file:
        file.write("[\n" + ",\n".join(data) + "\n]")
    output_files[file_path] = output_file_path

output_files
