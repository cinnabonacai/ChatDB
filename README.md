# culture521
This project mainly aims to emphasize the application of ChatDB. It is mainly comprised of three folders: **Database**, **Frontend**, and **Backend**, where each of them is conducive to the development regarding full-stack projects. To better list what files are stored in each folder, it can be interpreted as below for final verificiation

Database

    NoSQL
      data 
        city.json
        country.json
        countryLanguage.json
        sampleCultureProducts.json
      Models
        Products.js //Schema
      Routes
        Products.js //Server
        
    SQL
      data
         Manufacturer_data.csv
         Product_data.csv
         Reviewer_data.csv
         Vendor_data.csv
         Warehouse_data.csv
         Relationship_product_manufacturer_data.csv
         Relationship_product_reviewer_data.csv
         Relationship_product_vendor_data.csv
         Relationship_product_warehouse_data.csv
         
      backend_create_table.go  //Schema
      backend_insert_data.go  //Schema
      backend_crud.py // Server

Frontend

    index.html
    script.js
    style.css

Backend

   my.py
   execute_nosql.py
   execute_sql.py




# NoSQL database
Given that a folder named NoSQL is created under Database folder, your terminal needs to be navigated under the directory Database/NoSQL/Routes, where you are able to see a file called **Products.js**. Similar to the traditional approach that uses server.js for lauching backend, the file Products.js can be executed via the command **node Products.js** to insert, update, or delete data whatever you want.

Later, once any additional data is updated via REST endpoint, you can replace a json file named sampleCultureProducts.json with a new json file at your MongoDB compass by clicking Export Data, Exporting the full collection, and the data format in JSON. 

# SQL database
The commands to run SQL database might differ from those for running NoSQL database in that the folder named **SQL** is selected under **Database**. There are two Go files and one python file required to be investigated: **backend_create_table.go**, **backend_insert_data.go**, and **backend_crud.py**. First, multiple SQL tables are constructed via the command **go run backend_create_table.go**, and then the data embedded into each table can be manipulated via the command **go run backend_insert_data.go**. Then any data update, retrieval, and deletion is performed in backend_crud.py so that the latest version of my SQL data can be obtained immediately.

**Point: When you attempt to insert data in the database, make sure the port numbers and the password are based on your own laptop instead of us because we are running SQL database at local.**


# Lang2Query
This is the most important part of our program, where it mainly handles the implementation associated with leveraging the principles of traditional compilers. In order to guarantee the functionality of our compiler, the command **python/python3 my.py** can be typed on your terminal to ensure the backend endpoint at Flask can be connected to the frontend at JavaScript in JSON format.  


# Frontend
You can directly open the web page at the directory to see the outline of the website
