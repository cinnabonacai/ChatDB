package main

import (
    "database/sql"
    "fmt"
    "io/ioutil"
    "log"
    "strings"

    _ "github.com/go-sql-driver/mysql"
)

func main() {
    // connect to MySQL database
    db, err := sql.Open("mysql", "root:Ilikedsci551@tcp(127.0.0.1:3306)/project551")
    if err != nil {
        log.Fatal("Database connection failed: ", err)
    }
    defer db.Close()

    // read SQL files
    sqlFile := "../sql/create_table.sql"
    queries, err := ioutil.ReadFile(sqlFile)
    if err != nil {
        log.Fatalf("Unable to read SQL file: %v", err)
    }

    // splite file contents into multiple SQL statements
    commands := strings.Split(string(queries), ";")

    // execute each SQL statement
    for _, command := range commands {
        trimmedCommand := strings.TrimSpace(command)
        if len(trimmedCommand) > 0 {
            _, err := db.Exec(trimmedCommand)
            if err != nil {
                log.Fatalf("Error executing SQL: %v", err)
            }
        }
    }

    fmt.Println("Tables were created successfully!")
}
