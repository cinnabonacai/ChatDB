package main

import (
    "bufio"
    "database/sql"
    "fmt"
    "log"
    "os"
    "strings"

    _ "github.com/go-sql-driver/mysql"
)

func main() {       
    // connect to MySQL database
    db, err := sql.Open("mysql", "root:Ilikedsci551@tcp(127.0.0.1:3306)/project551")
    if err != nil {
        log.Fatal("Fail to conect MySQL database:", err)
    }
    defer db.Close()

    reader := bufio.NewReader(os.Stdin)
    var sqlBuilder strings.Builder

    fmt.Println("Please enter the SQL query statement and type 'chatbot-exit' to exit:.")

    for {
        // read Input
        fmt.Print("SQL> ")
        line, err := reader.ReadString('\n')
        if err != nil {
            log.Fatalf("read input error: %v", err)
        }

        // check if the user has typed 'chatbot-exit' to exit the program
        if strings.TrimSpace(line) == "chatbot-exit" {
            fmt.Println("Successful exit from chatbot!")
            break
        }

        // append the input rows to the SQL statement builder
        sqlBuilder.WriteString(line)

        // if ';' is detected, indicate the end of the SQL statement
        if strings.Contains(line, ";") {
            // get the full SQL statement
            sqlQuery := sqlBuilder.String()
            // empty the sqlBuilder for subsequent inputs
            sqlBuilder.Reset()
            // execute SQL query
            executeSQL(db, sqlQuery)
        }
    }
}

// execute SQL query
func executeSQL(db *sql.DB, query string) {
    // remove whitespace from both ends
    query = strings.TrimSpace(query)
    // process SELECT queries
    if strings.HasPrefix(strings.ToUpper(query), "SELECT") {
        rows, err := db.Query(query)
        if err != nil {
            log.Printf("Error executing query: %v", err)
            return
        }
        defer rows.Close()
        // get column names
        columns, err := rows.Columns()
        if err != nil {
            log.Fatalf("Error retrieving column name: %v", err)
        }
        // print search results
        printQueryResults(rows, columns)
    } else {
        // for non-query statements (INSERT, UPDATE, DELETE)
        // take care!!!
        _, err := db.Exec(query)
        if err != nil {
            log.Printf("Error executing SQL: %v", err)
            return
        }
        fmt.Println("SQL statement executed successfully")
    }
}

// print search results
func printQueryResults(rows *sql.Rows, columns []string) {
    // print column names
    fmt.Println(strings.Join(columns, "\t"))
    // create a slice to store the values in each column
    values := make([]interface{}, len(columns))
    valuePtrs := make([]interface{}, len(columns))
    for i := range values {
        valuePtrs[i] = &values[i]
    }
    // print results
    for rows.Next() {
        err := rows.Scan(valuePtrs...)
        if err != nil {
            log.Fatalf("Error while scanning line: %v", err)
        }
        // format and print each line of data
        for _, val := range values {
            if val != nil {
                switch v := val.(type) {
                case bool:
                    fmt.Printf("%t\t", v)
                case int, int32, int64:
                    fmt.Printf("%d\t", v)
                case float32, float64:
                    fmt.Printf("%f\t", v)
                case []byte:
                    fmt.Printf("%s\t", string(v)) // convert []byte to string
                case string:
                    fmt.Printf("%s\t", v)
                default:
                    fmt.Printf("%v\t", v)
                }
            } else {
                fmt.Print("NULL\t")
            }
        }
        fmt.Println()
    }

    if err := rows.Err(); err != nil {
        log.Fatalf("Error while processing result: %v", err)
    }
}
