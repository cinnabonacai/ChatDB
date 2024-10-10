# Frontend-Backend API Documentation

This document describes the REST API endpoints and WebSocket connections that facilitate the interaction between the frontend and backend systems for ChatDB, a project designed to allow users to query databases using natural language.

---

## **1. API Overview**

| Endpoint | Method | Description |
| --- | --- | --- | --- |
| `/databases` | GET | Retrieve the list of available databases (SQL and NoSQL) for the user to query. |
| `/databases/{db_type}/{db_name}/schema` | GET | Fetch the schema (tables/collections and their attributes) for the selected database. |
| `/databases/{db_type}/{db_name}/query` | POST | Execute a query on the selected database and return the results. |
| `/databases/{db_type}/{db_name}/sample-query` | POST | Generate a sample query with a specified language construct (e.g., `group by`).  |
| `/databases/{db_type}/{db_name}/create` | POST | Create a new product in the database and sync it with Shopify.  |
| `/databases/{db_type}/{db_name}/update/{product_id}` | PATCH | Update an existing product and sync with Shopify. |
| `/databases/{db_type}/{db_name}/delete/{product_id}` | DELETE | Delete a product from the database and Shopify.  |
| `/ws/chat` | WebSocket | Real-time interaction for user queries and responses.  |


---

## **2. API Endpoints**

### **2.1 Retrieve Databases**

#### **GET /databases**

**Description**: Retrieve a list of available databases (both SQL and NoSQL) for the user to select.

**Request**:
- No request body required.

**Response**:
- **Content-Type**: `application/json`

**Response Body**:
```json
{
  "databases": [
    {"name": "MySQL", "type": "SQL"},
    {"name": "MongoDB", "type": "NoSQL"}
  ]
}
```

### **2.2 Get Database Schema**

#### **GET /databases/{db_type}/{db_name}/schema**

**Description**: Retrieve the schema (tables/collections and attributes) of the selected database.

**Parameters:**
- db_type (string): Type of database (e.g., SQL, NoSQL).
- db_name (string): Name of the database (e.g., MySQL, MongoDB).

**Request:**
No request body required.

**Response:**
- Content-Type: application/json

**Response Body:**
```json
{
  "tables": [
    {
      "name": "products",
      "attributes": [
        {"name": "id", "type": "integer"},
        {"name": "name", "type": "string"},
        {"name": "category", "type": "string"},
        {"name": "price", "type": "decimal"}
      ]
    }
  ]
}
```

### **2.3 Execute a Database Query**

#### **POST /databases/{db_type}/{db_name}/query**

**Description**: Execute a SQL or NoSQL query on the selected database and return the results.

**Parameters:**
- db_type (string): Type of the database (e.g., SQL, NoSQL).
- db_name (string): Name of the database (e.g., MySQL, MongoDB).

**Request:**
Content-Type: application/json

**Request Body:**
```json
{
  "query": "SELECT * FROM products WHERE category = 'Tea';"
}
```

**Response:**
- Content-Type: application/json

**Response Body:**
```json
{
  "results": [
    {"id": 1, "name": "Green Tea", "category": "Tea", "price": 10.99},
    {"id": 2, "name": "Black Tea", "category": "Tea", "price": 9.99}
  ]
}

```

### **2.4 Generate Sample Query**

#### **POST /databases/{db_type}/{db_name}/sample-query**

**Description**: Generate and return a sample query that uses a specified language construct (e.g., group by).

**Parameters:**
- db_type (string): Type of database (e.g., SQL, NoSQL).
- db_name (string): Name of the database (e.g., MySQL, MongoDB).

**Request:**
No request body required.

**Request Body:**
```json
{
  "construct": "group by"
}
```

**Response:**
- Content-Type: application/json

**Response Body:**
```json
{
  "query": "SELECT category, COUNT(*) FROM products GROUP BY category;",
  "description": "Get the count of products by category."
}
```

### **2.5 Create a New Product**

#### **POST /databases/{db_type}/{db_name}/create**

**Description**: Add a new product to the database and sync it with Shopify.

**Parameters:**
- db_type (string): Type of database (e.g., SQL, NoSQL).
- db_name (string): Name of the database (e.g., MySQL, MongoDB).

**Request:**
No request body required.

**Response:**
- Content-Type: application/json

**Response Body:**
```json
{
  "message": "Product created successfully.",
  "product_id": 2
}
```

### **2.6 Update an Existing Product**

#### **PATCH /databases/{db_type}/{db_name}/update/{product_id}**

**Description**: Update product details in the database and sync it with Shopify.

**Parameters:**
- db_type (string): Type of database (e.g., SQL, NoSQL).
- db_name (string): Name of the database (e.g., MySQL, MongoDB).
- product_id (integer): ID of the product to update.

**Request:**
- Content-Type: application/json

**Request Body**:
```json
{
  "product": {
    "price": 11.99
  }
}
```

**Response:**
- Content-Type: application/json

**Response Body:**
```json
{
  "message": "Product updated successfully."
}
```

### **2.7 Delete a Product**

#### **DELETE /databases/{db_type}/{db_name}/delete/{product_id}**

**Description**: Delete a product from the database and Shopify.

**Parameters:**
- db_type (string): Type of database (e.g., SQL, NoSQL).
- db_name (string): Name of the database (e.g., MySQL, MongoDB).
- product_id (integer): ID of the product to delete.

**Request:**
No request body required.

**Response:**
- Content-Type: application/json

**Response Body:**
```json
{
  "message": "Product deleted successfully."
}
```
