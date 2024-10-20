package main

import (
    "database/sql"
    "encoding/csv"
    "fmt"
    "log"
    "os"
    //"strconv"

    _ "github.com/go-sql-driver/mysql"
)

func main() {
    // connect to MySQL database
    db, err := sql.Open("mysql", "root:Ilikedsci551@tcp(127.0.0.1:3306)/project551")
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()

    // import CSV files into tables
    importCSVToTable(db, "../data/Vendor_data.csv", "Vendor")
    importCSVToTable(db, "../data/Manufacturer_data.csv", "Manufacturer")
    importCSVToTable(db, "../data/Reviewer_data.csv", "Reviewer")
    importCSVToTable(db, "../data/Warehouse_data.csv", "Warehouse")
    importCSVToTable(db, "../data/Product_data.csv", "Product")
    importCSVToTable(db, "../data/Relationship_product_vendor_data.csv", "Relationship_Product_Vendor")
    importCSVToTable(db, "../data/Relationship_product_manufacturer_data.csv", "Relationship_Product_Manufacturer")
    importCSVToTable(db, "../data/Relationship_product_reviewer_data.csv", "Relationship_Product_Reviewer")

    fmt.Println("Data import is complete!")
}

// import a CSV file to a specified table
func importCSVToTable(db *sql.DB, csvFilePath, tableName string) {
    file, err := os.Open(csvFilePath)
    if err != nil {
        log.Fatalf("Unable to open file: %v", err)
    }
    defer file.Close()

    reader := csv.NewReader(file)
    records, err := reader.ReadAll()
    if err != nil {
        log.Fatalf("Unable to read CSV file: %v", err)
    }

    // Getting the column names of a CSV file
    columns := records[0]

    for i, record := range records[1:] {
        // Generating Insert SQL Statements
        placeholders := make([]string, len(record))
        values := make([]interface{}, len(record))
        for j := range record {
            placeholders[j] = "?"
            values[j] = record[j]
        }

        sqlStmt := fmt.Sprintf("INSERT INTO %s (%s) VALUES (%s)", tableName, join(columns, ","), join(placeholders, ","))
        _, err := db.Exec(sqlStmt, values...)
        if err != nil {
            log.Printf("Error inserting table %s row %d: %v", tableName,i+1, err)
        }
    }
}

// help function: concatenate slice into a string
func join(elements []string, sep string) string {
    var result string
    for i, el := range elements {
        if i > 0 {
            result += sep
        }
        result += el
    }
    return result
}
