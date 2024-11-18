import re
from typing import List, Tuple, Dict, Any
import json, csv

#词法分析模块
# 定义 Token 类型 [The token is defined.]
class Token:
    def __init__(self, token_type: str, value: str):
        self.type = token_type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"

def infer_sql_type(value: Any) -> str:
    # SQL Type Value

    if value is None or (isinstance(value, str) and value.strip() == ""):
        return "NULL"
    if isinstance(value, str) and value.lower() in ["true", "false"]:
        return "BOOLEAN"
    try:
        if isinstance(value, str) and value.isdigit():
            return "INTEGER"
        float(value)
        if "." in str(value):
            return "REAL"
    except ValueError:
        pass
    if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
        return "ARRAY"
    if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
        return "JSON"
    if isinstance(value, str):
        import re
        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        if re.match(date_pattern, value):
            return "DATE"
        datetime_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$"
        if re.match(datetime_pattern, value):
            return "DATETIME"
    return "TEXT"


def infer_nosql_type(value: Any) -> str:
    # NoSQL Type Value

    if value is None or (isinstance(value, str) and value.strip() == ""):
        return "null"
    if isinstance(value, str) and value.lower() in ["true", "false"]:
        return "bool"
    try:
        if isinstance(value, str) and value.isdigit():
            return "int32"
        float(value)
        if "." in str(value):
            return "double"
    except ValueError:
        pass
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "document"
    if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
        return "array"
    if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
        try:
            json.loads(value)
            return "document"
        except json.JSONDecodeError:
            pass
    if isinstance(value, str):
        import re
        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        if re.match(date_pattern, value):
            return "date"
    return "string"


def detect_field_types_from_csv(file_path: str) -> Dict[str, str]:
   # Detect Specific Field Types from CSV
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        field_types = {field: None for field in reader.fieldnames}
        first_row = next(reader, None)
        if not first_row:
            raise ValueError("CSV file is empty.")
        for field, value in first_row.items():
            field_types[field] = infer_sql_type(value)
        return field_types


def detect_field_types_from_json(file_path: str) -> Dict[str, str]:
    # Detect Specific Fields from JSON

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        field_types = {}
        for field, value in data.items():
            field_types[field] = infer_nosql_type(value)
        return field_types

symbol_table: Dict[str, str] = {} 

def generate_separate_symbol_tables(path: str) -> None:
     global symbol_table 
     if path.endswith('.csv'):
        symbol_table = detect_field_types_from_csv(path)
        return "SQL"
     elif path.endswith('.json'):
        symbol_table = detect_field_types_from_json(path)
        return "NoSQL"
     else:
        raise ValueError("Unsupported file format. Please provide a CSV or JSON file.")

# the rules for tokens:
def generate_field_patterns(table_selected):
    fields = "|".join(re.escape(field) for field in table_selected.keys())
    return rf"\b({fields})\b"

# (1) \b -> the word boundary that ensures no partial matches
TOKEN_RULES = [
    ("KEYWORD", r"\b(search for|look for|get|retrieve|find|select|query|fetch|read|access|filter|extract|look up|match)\b"),  # 动词[verbs]
    ("RELATION", r"\b(equal to|greater than|less than|is not equal to|greater than or equal to|less than or equal to|>=|<=|>|<|!=)\b"),  # 关系运算符[relational operators]
    ("FIELD", generate_field_patterns(symbol_table)),  # 字段名[fields]  # Pending: change it into the specific fields
    ("LOGICAL_OPERATOR", r"\b(and|or|nor)\b"),  # 逻辑操作符[logical operators]
    ("VALUE", r"(\d+|'.*?')"),  # 数值或字符串值[string or number]
    ("WHITESPACE", r"\s+"),  # 空格（可以跳过） [whitespace]
    ("INVALID", r".")  # 无效字符[invalid characters]
]

# the construction of lexical analysus
def lexical_analysis(input_text: str) -> List[Token]:
    # tokens array to extract each words based on the token rules defined above
    tokens = []
    
    # start at position 0
    pos = 0

    # iterate your input one by one
    while pos < len(input_text):

        # match the input text with the token rules
        match = None

        #The format of the entry at token_rules can be explained as (token type, pattern) 
        for token_type, pattern in TOKEN_RULES:

            # compile the pattern
            regex = re.compile(pattern)  # e.g. Search for, Look Up, etc.
            match = regex.match(input_text, pos) # match the input text with the pattern
            
            # If it is fitted, a total of three possibilities will be considered in advance
            if match:
                # whitespace
                if token_type == "WHITESPACE":  # whitespace
                    pos = match.end()
                    break
                # invalid
                elif token_type == "INVALID":  # Any redundant characters can be ignored
                    #print(f"Warning: Invalid character '{match.group(0)}' at position {pos}")
                    pos = match.end()
                    break
                # the rest of the scenarios
                else:
                    # The rest of the scenarios
                    token_value = match.group(0)
                    tokens.append(Token(token_type, token_value))
                    pos = match.end()
                    break
        # The position is not found
        if not match:
            raise SyntaxError(f"Illegal character at position {pos}: {input_text[pos]}")
    return tokens

#AST Type
class ASTNode:
    """The node for AST Tree"""
    """The type of AST Tree is node_type: Operators, Literals, etc."""
    """The children of AST Tree if my current node is a parent node"""
    """The value of AST Tree if it is a left node or a standalone node"""
    def __init__(self, node_type: str, children=None, value=None):
        self.type = node_type
        self.children = children if children else []
        self.value = value

    def __repr__(self):
        # The root node
        if self.value:
            return f"ASTNode({self.type}, {self.value})"
        
        # The children node
        return f"ASTNode({self.type}, {self.children})"

# define the specific parser
class Parser:

    # the token array and its corresponding position
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # analyze the current token
    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None


    def consume(self, expected_type=None):
        # access my current tokem
        token = self.current_token()

        # check the token type and its expected type
        # for instance, ("FIELD", "AGE")
        print(f"Test: Current Token -> {token}, Expected -> {expected_type}")

        # If it isn't a token, return the syntax error
        if token is None:
            raise SyntaxError("Unexpected end of input.")
        
        # If the token type is found, but its corresponding type does not match the current type
        if expected_type and token.type != expected_type:
            print(f"Debug: Current Token -> {token}, Expected -> {expected_type}")
            raise SyntaxError(f"Expected {expected_type} but got {token.type}.")
        
        # go to the next toke
        self.pos += 1
        return token


    def parse(self):
        # After all tokens are processed, it is required to return all queries.
        return self.query()

    def query(self):
        """It is related to the two child nodes of the query: (1) verb[select, find, filter, ....] (2) condition [age = 20, name = 'Smith']"""
        verb_node = self.verb()
        #object_node = self.object()
        condition_node = self.condition()
        #return ASTNode("QUERY", [verb_node, object_node, condition_node])
        return ASTNode("QUERY", [verb_node, condition_node])

    # look for all words that are related to the keyword
    def verb(self):
        """解析 VERB"""
        token = self.consume("KEYWORD")
        return ASTNode("VERB", value=token.value)


    def object(self):
        """解析 OBJECT"""
        token = self.consume("FIELD")
        return ASTNode("OBJECT", value=token.value)
    
    # look for all words that are related to the conditions
    def condition(self):
        # It is better to consider multiple conditions simultaneously.
        conditions = [self.single_condition()]
        while self.current_token() and self.current_token().value in ["and", "or", "nor"]:
            operator_token = self.consume()  # LOGICAL_OPERATOR
            next_condition = self.single_condition() # figure out the next condition
            conditions.append(ASTNode("LOGICAL_OPERATOR", value=operator_token.value))
            conditions.append(next_condition)
        return ASTNode("CONDITION", conditions)

    def single_condition(self):
        # Single condition
        field_node = self.field()
        relation_node = self.relation()
        value_node = self.value()
        return ASTNode("SINGLE_CONDITION", [field_node, relation_node, value_node])

    def field(self):
        """解析 FIELD"""
        token = self.consume("FIELD")
        return ASTNode("FIELD", value=token.value)

    def relation(self):
        """解析 RELATION"""
        token = self.consume("RELATION")
        return ASTNode("RELATION", value=token.value)

    def value(self):
        """解析 VALUE"""
        token = self.consume("VALUE")
        return ASTNode("VALUE", value=token.value)


# define semantic
class SemanticError(Exception):
    # What happen if the syntax error is incorrect.
    pass

class SemanticAnalyzer:

    # initialize the symbol table
    def __init__(self, symbol_table: Dict[str, str], target: str = "SQL"):
        self.symbol_table = symbol_table
        self.target = target
   
    def analyze(self, ast):
        if self.target not in ["SQL", "NoSQL"]:
            raise ValueError("Target must be 'SQL' or 'NoSQL'")
        
        # If my result type is query, then I will analyze the query.
        if ast.type == "QUERY":
            return self.analyze_query(ast)
        else:
            raise SemanticError(f"Unsupported AST node type: {ast.type}")
    
    # start from the root of the AST, both verb and conditions are examined.
    def analyze_query(self, node):
        """Analyze the root query node based on SQL and NoSQL"""
        for child in node.children:
            # PENDING: If the type of the child is verb, we need to check whether it is valid.

            # If these are conditions, it is required to analyze their conditions
            if child.type == "CONDITION":
                self.analyze_condition(child)

    # For multiple conditions, each individual condition is examined properly.
    def analyze_condition(self, node):
        """check the condition node"""
        for child in node.children:
            if child.type == "SINGLE_CONDITION":
                self.analyze_single_condition(child)
            elif child.type == "LOGICAL_OPERATOR":
                continue
            else:
                raise SemanticError(f"Unexpected node type in CONDITION: {child.type}")
    
    # Each single condition is checked precisely.
    def analyze_single_condition(self, node):
        """examine multiple conditions"""
        field_node = node.children[0]
        relation_node = node.children[1]
        value_node = node.children[2]

        # check whether the field node is empty
        field = field_node.value
       
        # If the field is not in the symbol table, it is required to raise an error.
        if field not in self.symbol_table:
            raise SemanticError(f"Field '{field}' is not defined in the symbol table.")

        # check the expected type of its value -> [int, double, string, ...]
        expected_type = self.symbol_table[field]
        value = value_node.value # [The corresponding value of this field]

        # If both of them do not match, a semantic error will be raised.
        if not self.check_type_match(expected_type, value):
            raise SemanticError(f"Value '{value}' does not match the expected type '{expected_type}' for field '{field}' in '{self.target}'.")

        # relational operator
        relation = relation_node.value
        # whether it uses and, or, nor, etc....
        if not self.check_relation_valid(expected_type, relation):
            raise SemanticError(f"Relation operator '{relation}' is not valid for field '{field}' with type '{expected_type}'.")

    def check_type_match(self, expected_type, value):
        # check whether the value is matched with the expected type
        # PENDING: Extension object, array, number, etc...
        if self.target == "SQL":
            # SQL type matching
            if expected_type == "INTEGER" and value.isdigit():
                return True
            if expected_type == "REAL" and self.is_float(value):
                return True
            if expected_type == "TEXT" and value.startswith("'") and value.endswith("'"):
                return True
            if expected_type == "DATE" and self.is_date(value):
                return True
        elif self.target == "NoSQL":
            # NoSQL type matching
            if expected_type == "int32" and value.isdigit():
                return True
            if expected_type == "double" and self.is_float(value):
                return True
            if expected_type == "string" and isinstance(value, str):
                return True
            if expected_type == "array" and value.startswith("[") and value.endswith("]"):
                return True
            if expected_type == "date" and self.is_date(value):
                return True

    def is_float(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def check_relation_valid(self, field_type, relation):
        """check whether the relational operators is valid and invalid"""
        # Numeric fields: int, float, number
        if self.target == "SQL":
            numeric_relations = ["=", ">", "<", ">=", "<=", "!="]
            string_relations = ["=", "!="]
        elif self.target == "NoSQL":
            numeric_relations = ["$eq", "$gt", "$lt", "$gte", "$lte", "$ne"]
            string_relations = ["$eq", "$ne"]

        if field_type in ["INTEGER", "REAL", "int32", "double"]:
            return relation in numeric_relations
        elif field_type in ["TEXT", "string"]:
            return relation in string_relations

        return False



# The prompt can generate the code based on two specific versions: SQL and NoSQL
# SQL
# NoSQL
class CodeGenerator:
    # determine the specific type of target, which is either SQL or NoSQL
    def __init__(self, target="SQL"):
        if target not in ["SQL", "MongoDB"]:
            raise ValueError("Target must be 'SQL' or 'MongoDB'")
        self.target = target
     
     # It's time to generate the query based on Abstract Syntax Tree
     # PENDING: The name of the table needs to be modified based on the table name.
    def generate(self, ast, table_name="items"):
        if ast.type == "QUERY":
            return self.generate_query(ast, table_name)
        else:
            raise ValueError(f"Unsupported AST node type: {ast.type}")

    # 
    def generate_query(self, node, table_name):
        # The query is produced based on the generation mentioned above.
        condition_node = next(child for child in node.children if child.type == "CONDITION")
        if self.target == "SQL":
            # If it is SQL, the query will be supposed to generate the sql
            return self.generate_sql(condition_node, table_name)
        elif self.target == "MongoDB":
            # If it is not sql, the query will be supposed to generate the noSQL
            return self.generate_mongo(condition_node, table_name)
        else:
            raise ValueError(f"Unsupported target: {self.target}")

    # Pending: implement various kinds of sql queries
    #          Solve the question based on the SQL query
    def generate_sql(self, condition_node, table_name):
        """The output of the SQL is reproduced"""
        conditions = self.traverse_conditions(condition_node, for_sql=True)
        return f"SELECT * FROM {table_name} WHERE {' '.join(conditions)};"

    # Pending: implement various kinds of NoSQL queries
    #          Solve the question based on the NoSQL query
    def generate_mongo(self, condition_node, table_name):
        """MongoDB is generated based on various conditions"""
        conditions = self.traverse_conditions(condition_node, for_sql=False)
        if len(conditions) == 1:
            query = conditions[0]
        else:
            query = { "$and": conditions }
        return f"db.{table_name}.find({query});"

    def traverse_conditions(self, node, for_sql=True):
        # implement variouus conditions to resolve each type
        conditions = []
        for child in node.children:
            # single condition
            if child.type == "SINGLE_CONDITION":
                field = child.children[0].value
                relation = child.children[1].value
                value = child.children[2].value
                if for_sql:
                    # If it is SQL, convert it into SQL
                    sql_relation = self.map_sql_operator(relation)
                    conditions.append(f"{field} {sql_relation} {value}")
                else:
                    # If it is noSQL, convert it into noSQL
                    mongo_operator = self.map_mongo_operator(relation)
                    conditions.append({ field: { mongo_operator: value } })
            # multiple conditions
            elif child.type == "LOGICAL_OPERATOR":
                if for_sql:
                    conditions.append(child.value.upper())
                #conditions.append(child.value.upper() if for_sql else None)
        return conditions

    def map_sql_operator(self, relation):
        """映射 SQL 运算符"""
        return {
            "equal to": "=",
            "greater than": ">",
            "less than": "<",
            "is not equal to": "!=",
            "greater than or equal to": ">=",
            "less than or equal to": "<="
        }.get(relation, relation)

    def map_mongo_operator(self, relation):
        """映射 MongoDB 运算符"""
        return {
            "equal to": "$eq",
            "greater than": "$gt",
            "less than": "$lt",
            "is not equal to": "$ne",
            "greater than or equal to": "$gte",
            "less than or equal to": "$lte"
        }.get(relation, relation)

# 测试语法分析器
'''
if __name__ == "__main__":

    # 测试 Token 输入
    tokens: List[Token] = [
        Token("KEYWORD", "search for"),
        Token("FIELD", "id"),
        Token("RELATION", "equal to"),
        Token("VALUE", "123"),
        Token("FIELD", "price"),
        Token("RELATION", "greater than"),
        Token("VALUE", "50")
    ]

    parser = Parser(tokens)
    ast = parser.parse()
    print(ast)
'''

# 测试输入
if __name__ == "__main__":
    '''
    print("test begin")
    tokens = [
        Token("KEYWORD", "search for"),
        Token("FIELD", "id"),
        Token("RELATION", "equal to"),
        Token("VALUE", "123"),
        Token("LOGICAL_OPERATOR", "and"),
        Token("FIELD", "price"),
        Token("RELATION", "greater than"),
        Token("VALUE", "50")
    ]
    parser = Parser(tokens)
    ast = parser.parse()
    print(ast)
    print("test end")
    '''
    #路径
    path = "items.csv"
    my_target= generate_separate_symbol_tables(path)
    #输入
    input_query = "search for items where id equal to 123 and price greater than 50"
    print("input_query:")
    print(input_query)
    #词法分析模块
    tokens = lexical_analysis(input_query)
    print("\nlexical analysis:")
    for i in tokens:
        if i.type!="INVALID":
            print(i)
    print(tokens)
    #语法分析模块
    print("\nsyntax analysis:")
    parser = Parser(tokens)
    #print(parser)
    ast = parser.parse()
    print(ast)
    #语义分析模块
    print("\nsemantic analysis:")
    analyzer = SemanticAnalyzer(symbol_table, my_target)
    try:
        analyzer.analyze(ast)
        print("Semantic analysis passed. The query is valid.")
    except SemanticError as e:
        print(f"Semantic Error: {e}")
    #代码生成模块
    print("\ncode generator")
    # 生成 SQL 查询
    sql_generator = CodeGenerator(target=my_target)
    sql_query = sql_generator.generate(ast)
    print("Generated SQL Query:")
    print(sql_query)
    # 生成 MongoDB 查询
    mongo_generator = CodeGenerator(target="MongoDB")
    mongo_query = mongo_generator.generate(ast)
    print("\nGenerated MongoDB Query:")
    print(mongo_query)