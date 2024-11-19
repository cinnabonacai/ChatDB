import re
import json
import csv
from typing import List, Tuple, Dict, Any


# **Token 类定义**
class Token:
    def __init__(self, token_type: str, value: str):
        self.type = token_type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"


# **AST 节点定义**
class ASTNode:
    def __init__(self, node_type: str, children=None, value=None):
        self.type = node_type
        self.children = children if children else []
        self.value = value

    def __repr__(self):
        return f"ASTNode({self.type}, {self.value or self.children})"


# **全局变量与规则**
symbol_table: Dict[str, str] = {}
TOKEN_RULES = []


# **辅助函数**
def infer_sql_type(value: Any) -> str:
    if value is None or value == "":
        return "NULL"
    if isinstance(value, str) and value.lower() in ["true", "false"]:
        return "BOOLEAN"
    if isinstance(value, str) and value.isdigit():
        return "INTEGER"
    try:
        float(value)
        if "." in value:
            return "REAL"
    except ValueError:
        pass
    if re.match(r"^\d{4}-\d{2}-\d{2}$", value):
        return "DATE"
    return "TEXT"


def infer_nosql_type(value: Any) -> str:
    if value is None or value == "":
        return "null"
    if isinstance(value, str) and value.lower() in ["true", "false"]:
        return "bool"
    if isinstance(value, str) and value.isdigit():
        return "int32"
    if isinstance(value, str) and "." in value and ":" not in value:
        return "double"
    if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
        return "array"
    if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
        try:
            json.loads(value)
            return "document"
        except json.JSONDecodeError:
            pass
    return "string"


def detect_field_types(file_path: str) -> Dict[str, str]:
    with open(file_path, "r", encoding="utf-8") as f:
        if file_path.endswith(".csv"):
            reader = csv.DictReader(f)
            return {field: infer_sql_type(next(reader)[field]) for field in reader.fieldnames}
        elif file_path.endswith(".json"):
            data = json.load(f)
            if isinstance(data, dict):
                return {key: infer_nosql_type(value) for key, value in data.items()}
            elif isinstance(data, list) and len(data) > 0:
                return {key: infer_nosql_type(value) for key, value in data[0].items()}
    raise ValueError("Unsupported file format")


def generate_field_patterns(fields: Dict[str, str]) -> str:
    return r"\b(" + "|".join(re.escape(field) for field in fields.keys()) + r")\b"


def generate_token_rules(fields: Dict[str, str]) -> List[Tuple[str, str]]:
    return [
        ("KEYWORD", r"\b(search for|find|select|insert|add|append|create|put|write|store|include|populate|update|modify|edit|change|alter|refresh|adjust|correct|revise|replace|delete|remove|erase|clear|drop|destroy|truncate|discard|sum|count|avg|min|max)\b"),
        ("RELATION", r"\b(equal to|>|<|>=|<=|!=|set|values|into|from|where)\b"),
        ("FIELD", generate_field_patterns(fields)),
        ("LOGICAL_OPERATOR", r"\b(and|or|nor|not)\b"),
        ("VALUE", r"(\d+|'.*?'|\".*?\")"),
        ("WHITESPACE", r"\s+"),
        ("INVALID", r".")
    ]


# **词法分析器**
def lexical_analysis(input_text: str) -> List[Token]:
    tokens = []
    pos = 0
    while pos < len(input_text):
        match = None
        for token_type, pattern in TOKEN_RULES:
            regex = re.compile(pattern)
            match = regex.match(input_text, pos)
            if match:
                if token_type != "WHITESPACE":
                    tokens.append(Token(token_type, match.group(0)))
                pos = match.end()
                break
        if not match:
            raise SyntaxError(f"Illegal character at position {pos}: {input_text[pos]}")
    return tokens


# **解析器**
class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected_type=None):
        token = self.current_token()
        if not token:
            raise SyntaxError("Unexpected end of input.")
        if expected_type and token.type != expected_type:
            raise SyntaxError(f"Expected {expected_type} but got {token.type}.")
        self.pos += 1
        return token

    def parse(self):
        verb = self.consume("KEYWORD").value.lower()
        if verb in ["search for", "find", "select"]:
            return self.parse_select()
        elif verb in ["insert into", "add", "create"]:
            return self.parse_insert()
        elif verb in ["update", "modify"]:
            return self.parse_update()
        elif verb in ["delete from", "remove"]:
            return self.parse_delete()
        else:
            raise SyntaxError(f"Unknown operation: {verb}")

    def parse_select(self):
        condition_node = self.parse_condition()
        return ASTNode("SELECT_QUERY", children=[condition_node])

    def parse_insert(self):
        table_node = self.consume("FIELD")
        values_node = self.parse_values()
        return ASTNode("INSERT_QUERY", children=[table_node, values_node])

    def parse_update(self):
        table_node = self.consume("FIELD")
        set_clause = self.parse_set_clause()
        condition_node = self.parse_condition()
        return ASTNode("UPDATE_QUERY", children=[table_node, set_clause, condition_node])

    def parse_delete(self):
        table_node = self.consume("FIELD")
        condition_node = self.parse_condition()
        return ASTNode("DELETE_QUERY", children=[table_node, condition_node])

    def parse_condition(self):
        conditions = []
        while True:
            field = self.consume("FIELD")
            relation = self.consume("RELATION")
            value = self.consume("VALUE")
            conditions.append(ASTNode("CONDITION", value=(field.value, relation.value, value.value)))
            if not self.current_token() or self.current_token().type != "LOGICAL_OPERATOR":
                break
            self.consume("LOGICAL_OPERATOR")
        return ASTNode("CONDITIONS", children=conditions)

    def parse_values(self):
        values = []
        while self.current_token() and self.current_token().type == "VALUE":
            values.append(self.consume("VALUE"))
        return ASTNode("VALUES", children=[Token("VALUE", v.value) for v in values])

    def parse_set_clause(self):
        updates = []
        while True:
            field = self.consume("FIELD")
            relation = self.consume("RELATION")
            value = self.consume("VALUE")
            updates.append(ASTNode("SET", value=(field.value, value.value)))
            if not self.current_token() or self.current_token().type != "LOGICAL_OPERATOR":
                break
            self.consume("LOGICAL_OPERATOR")
        return ASTNode("SET_CLAUSE", children=updates)


# **代码生成器**
class CodeGenerator:
    def __init__(self, target="SQL"):
        self.target = target

    def generate(self, ast: ASTNode):
        if ast.type == "SELECT_QUERY":
            return self.generate_select(ast)
        elif ast.type == "INSERT_QUERY":
            return self.generate_insert(ast)
        elif ast.type == "UPDATE_QUERY":
            return self.generate_update(ast)
        elif ast.type == "DELETE_QUERY":
            return self.generate_delete(ast)
        else:
            raise ValueError(f"Unsupported AST node type: {ast.type}")

    def generate_select(self, ast: ASTNode):
        conditions = self.conditions_to_string(ast.children[0])
        return f"SELECT * FROM table WHERE {conditions};"

    def generate_insert(self, ast: ASTNode):
        table = ast.children[0].value
        values = ", ".join(f"'{v.value}'" for v in ast.children[1].children)
        return f"INSERT INTO {table} VALUES ({values});"

    def generate_update(self, ast: ASTNode):
        table = ast.children[0].value
        set_clause = ", ".join(f"{u.value[0]} = '{u.value[1]}'" for u in ast.children[1].children)
        conditions = self.conditions_to_string(ast.children[2])
        return f"UPDATE {table} SET {set_clause} WHERE {conditions};"

    def generate_delete(self, ast: ASTNode):
        table = ast.children[0].value
        conditions = self.conditions_to_string(ast.children[1])
        return f"DELETE FROM {table} WHERE {conditions};"

    def conditions_to_string(self, node: ASTNode):
        return " AND ".join(f"{c.value[0]} {c.value[1]} '{c.value[2]}'" for c in node.children)


# **主程序**
def main():
    file_path = "../Database/NoSQL/sampleCultureProducts.json"  # Replace with your test JSON file path

    global symbol_table, TOKEN_RULES
    symbol_table = detect_field_types(file_path)
    TOKEN_RULES = generate_token_rules(symbol_table)

    query = "select * from users where age > 30"
    tokens = lexical_analysis(query)
    parser = Parser(tokens)
    ast = parser.parse()

    code_generator = CodeGenerator("SQL")
    sql_query = code_generator.generate(ast)
    print(sql_query)


if __name__ == "__main__":
    main()
