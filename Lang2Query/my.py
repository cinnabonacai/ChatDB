import re
from typing import List, Tuple, Dict, Any
import json, csv
import os

my_table_names = []

def process_table_names(file_paths):
    global my_table_names
    my_table_names = []
    for path in file_paths:
        file_name_with_ext = os.path.basename(path)
        table_name = os.path.splitext(file_name_with_ext)[0]
        my_table_names.append(table_name)
    print("Table names are: ", my_table_names)

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
    '''
    # Check for ISO 8601 datetime strings
    if isinstance(value, str):
        iso_datetime_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z?$"
        if re.match(iso_datetime_pattern, value):
            return "string"
    '''
   # Handle numeric strings
    #if isinstance(value, str):
        # Check for integer
    
    if isinstance(value, str) and value.isdigit():
        return "int32"
    if isinstance(value, str) and '.' in value and ':' not in value:
        return "double"
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
        #data = [json.loads(line) for line in f if line.strip()]
        data = json.load(f)
        #print(data)
        if isinstance(data, dict):
            # Root is a dictionary
            field_types = {}
            for field, value in data.items():
                field_types[field] = infer_nosql_type(value)
            return field_types

        elif isinstance(data, list):
            # Root is a list
            if not data:
                raise ValueError("JSON file is empty.")
            # Assuming the list contains dictionaries
            field_types = {}
            for field in data[0]:
                if field == '_id':
                    field_types[field] = "string"
                    continue
                sample_value = data[0][field]
                field_types[field] = infer_nosql_type(sample_value)
            return field_types        

        else:
            raise ValueError("Unsupported JSON structure. Expected a dictionary or a list.")
      
#symbol_table: Dict[str, str] = {} 
symbol_table: Dict[str, Dict[str, str]] = {}  # 支持多个表格的 symbol_table

def generate_separate_symbol_tables(paths: List[str]) -> str:
    """
    根据提供的路径列表生成 symbol_table，支持多个表。
    返回数据库类型：SQL 或 NoSQL。
    """
    global symbol_table
    symbol_table = {}  # 清空 symbol_table
    
    db_type = None  # 用于存储数据库类型
    for path in paths:
        print("My current path is: ", path)
        if path.endswith('.csv'):
            table_name = os.path.splitext(os.path.basename(path))[0]
            symbol_table[table_name] = detect_field_types_from_csv(path)
            db_type = "SQL" if db_type is None else db_type
        elif path.endswith('.json'):
            table_name = os.path.splitext(os.path.basename(path))[0]
            print("My current table is: ", table_name)
            symbol_table[table_name] = detect_field_types_from_json(path)
            print("My cvurrent symbol table is: ", symbol_table[table_name])
            db_type = "NoSQL" if db_type is None else db_type
        else:
            raise ValueError(f"Unsupported file format: {path}")
    
    if not symbol_table:
        raise ValueError("No valid files provided to generate symbol table.")
    
    return db_type  # 返回检测到的数据库类型

'''
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
'''

# the rules for tokens:
def generate_field_patterns(symbol_table):
    # Extract all unique field names across all tables
    unique_fields = set()
    for table_fields in symbol_table.values():
        unique_fields.update(table_fields.keys())
    # Escape the field names for regex patterns
    escaped_fields = [re.escape(field) for field in unique_fields]
    # Join the patterns with '|' to maintain the original return format
    fields_pattern = "|".join(escaped_fields)
    return fields_pattern

def generate_field_patterns2(table_selected):
    escaped_fields = [re.escape(field) for field in table_selected]
    fields_pattern = "|".join(escaped_fields)
    return fields_pattern

def insert_into_field(value):
    print("The value to be added: ", value)
    for i, rule in enumerate(TOKEN_RULES):
        if rule[0] == "FIELD":
            # 提取当前字段的正则表达式
            current_fields_pattern = rule[1]
            # 从现有正则表达式提取字段列表（假设是用 | 分隔）
            current_fields = re.findall(r"\b\w+\b", current_fields_pattern)
            # 合并现有字段和新的字段
            updated_fields = sorted(set(current_fields+[value]))
            # 重新生成正则表达式
            updated_pattern = r"\b(" + "|".join(updated_fields) + r")\b"
            # 更新规则
            TOKEN_RULES[i] = ("FIELD", updated_pattern)
            break
    

# the construction of lexical analysus
def lexical_analysis(input_text: str) -> List[Token]:
    # tokens array to extract each words based on the token rules defined above
    tokens = []
    # start at position 0
    pos = 0
    my_match = []
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
                elif token_type =='VALUE':
                    if tokens:
                        last = tokens[len(tokens) - 1]
                        if last.type == "GROUP_OPERATOR" and not match.group().isdigit():
                            print("Match.groups: ",match.group())
                            extracted_value = match.group().strip('"')
                            insert_into_field(extracted_value)
                            print("My updated tokens are: ", TOKEN_RULES)
                    token_value = match.group(0)
                    my_match.append(token_value)
                    tokens.append(Token(token_type, token_value))
                    pos = match.end()
                    break
                # the rest of the scenarios
                else:
                    # The rest of the scenarios
                    token_value = match.group(0)
                    my_match.append(token_value)
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
            if self.children:
                return f"ASTNode({self.type}, {self.value}, {self.children})"
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
        token = self.current_token()
        print("my current token is: ", token)
        if token is None:
            raise SyntaxError("No input to parse.")
        if token.type != "KEYWORD":
            raise SyntaxError(f"Expected a KEYWORD at the beginning, but got {token.type}")
        verb = token.value.lower()
        if verb in ['search for', 'look for', 'get', 'retrieve', 'find', 'select', 'query', 'fetch', 'read', 'access', 'filter', 'extract', 'look up', 'match']:
            return self.parse_select_query()
        elif verb in ['insert into', 'add', 'create', 'insert']:
            return self.parse_insert_query()
        elif verb in ['update', 'modify', 'set']:
            print("updated")
            return self.parse_update_query()
        elif verb in ['delete', 'delete from', 'remove', 'erase']:
            return self.parse_delete_query()
        elif verb in ['group by', 'aggregate', 'sum', 'count', 'avg', 'min', 'max', 'distinct', 'join', 'group', 'sort', 'unwind', 'project', 'limit', 'skip', 'lookup', 'collect', 'list', 'calculate']:
            return self.parse_aggregate_query()
        elif verb in ['generate']:
            print("generate in SQL")
            return self.parse_generate_query()
        else:
            raise SyntaxError(f"Unknown operation: {verb}")
    '''
    def query(self):
        """It is related to the two child nodes of the query: (1) verb[select, find, filter, ....] (2) condition [age = 20, name = 'Smith']"""
        verb_node = self.verb()
        #object_node = self.object()
        condition_node = self.condition()
        #return ASTNode("QUERY", [verb_node, object_node, condition_node])
        return ASTNode("QUERY", [verb_node, condition_node])
    '''
    
    def parse_select_query(self):
        #1 finish
        verb_node = self.verb()
        table_node = self.consume("TABLE_NAME")  # field name
        condition_node = self.condition()
        return ASTNode("SELECT_QUERY", [verb_node, table_node, condition_node])

    def parse_insert_query(self):
        #2 finish
        verb_node = self.consume("KEYWORD")  # insert into
        table_node = self.consume("TABLE_NAME")  # field name
        insert_node = self.content()
        '''
        # 可能存在 'into' 关键字
        if self.current_token() and self.current_token().value.lower() == 'into':
            self.consume("RELATION")  # Consume 'into'
        table_node = self.consume("FIELD")  # Table name
        # 可能存在 'values' 关键字
        if self.current_token() and self.current_token().value.lower() == 'values':
            self.consume("RELATION")  # Consume 'values'
        values_node = self.parse_values()
        return ASTNode("INSERT_QUERY", [verb_node, table_node, values_node])
        '''
        return ASTNode("INSERT_QUERY", [verb_node, table_node, insert_node])
        
    def parse_values(self):
        values = []
        while self.current_token() and self.current_token().type == "VALUE":
            value_node = self.consume("VALUE")
            values.append(ASTNode("VALUE", value=value_node.value))
            if self.current_token() and self.current_token().value == ',':
                self.consume()  # Consume comma
            else:
                break
        return ASTNode("VALUES", values)
    
    def parse_update_query(self):
        #3 finish
        verb_node = self.consume("KEYWORD")  # update
        table_node = self.consume("TABLE_NAME")  # field name
        print("My verb is: ", verb_node)
        print("My table is: ", table_node)
        # Expect 'set'
        if self.current_token() and self.current_token().value.lower() == 'set':
            self.consume("RELATION")  # Consume 'set'
        else:
            raise SyntaxError("Expected 'set' in update statement")
        set_clause = self.parse_set_clause()
        #不判断，直接加上condition node
        condition_node = self.condition()
        '''用where判断
        condition_node = None
        if self.current_token() and self.current_token().value.lower() == 'where':
            self.consume("RELATION")  # Consume 'where'
            condition_node = self.condition()
        print("condition node")
        print(condition_node)
        print("condition node")
        '''
        return ASTNode("UPDATE_QUERY", [verb_node, table_node, set_clause, condition_node])

    def parse_set_clause(self):
        updates = []
        while True:
            field_node = self.consume("FIELD")
            relation_node = self.consume("RELATION")  # Expect '=' or 'equal to'
            if relation_node.value not in ['=', 'equal to']:
                raise SyntaxError("Expected '=' in set clause")
            value_node = self.consume("VALUE")
            updates.append(ASTNode("UPDATE_PAIR", [field_node, value_node]))
            if self.current_token() and self.current_token().value == ',':
                self.consume()  # Consume comma
            else:
                break
        return ASTNode("SET_CLAUSE", updates)

    def parse_delete_query(self):
        #4 finish
        verb_node = self.consume("KEYWORD")  # delete from
        table_node = self.consume("TABLE_NAME")  # field name
        # 可能存在 'from' 关键字
        condition_node = self.condition()
        #if self.current_token() and self.current_token().value.lower() == 'from':
            #self.consume("RELATION")  # Consume 'from'
        #table_node = self.consume("FIELD")  # Table name
        #condition_node = None
        #if self.current_token() and self.current_token().value.lower() == 'where':
            #self.consume("RELATION")  # Consume 'where'
            #condition_node = self.condition()
        return ASTNode("DELETE_QUERY", [verb_node, table_node, condition_node])

    '''
    def parse_aggregate_query(self):
        #5
        verb_node = self.consume("KEYWORD")  # aggregate function like sum, count, etc.
        field_node = self.consume("FIELD")
        # 可能存在 'from' 关键字
        if self.current_token() and self.current_token().value.lower() == 'from':
            self.consume("RELATION")  # Consume 'from'
        table_node = self.consume("FIELD")  # Table name
        condition_node = None
        if self.current_token() and self.current_token().value.lower() == 'where':
            self.consume("RELATION")  # Consume 'where'
            condition_node = self.condition()
        return ASTNode("AGGREGATE_QUERY", [verb_node, field_node, table_node, condition_node])
    '''
    
    def parse_aggregate_query(self):
        pipeline = []
        verb_node = self.consume("KEYWORD")
        local_collection = self.consume("TABLE_NAME").value

        while self.current_token() and self.current_token().type == "AGGREGATION_OPERATOR":
            operator = self.consume("AGGREGATION_OPERATOR")
            stage = operator.value.lower()
            print("my current aggregation operator: ", operator)
            print("my stage is: ", stage)
            # SQL operation
            if stage == "join":
                foreign_collection =  self.consume("TABLE_NAME").value
                local_field = self.consume("FIELD").value
                logical_operator = self.consume("LOGICAL_OPERATOR").value
                foreign_field = self.consume("FIELD").value
                as_field = self.consume("VALUE").value
                pipeline.append({
                    "$lookup": {
                        "from": foreign_collection,
                        "localField": local_field,
                        "foreignField": foreign_field,
                        "as": as_field
                    }
                })
            elif stage == "group by":
                group_field = self.consume("FIELD").value
                pipeline.append({"$group": {"_id": f"${group_field}"}})
            elif stage == "sort":
                sort_field = self.consume("FIELD").value
                sort_order = self.consume("SORT_OPERATOR").value
                pipeline.append({"$sort": {sort_field: 1 if sort_order == "increasingly" else -1}})
            elif stage == "unwind":
                unwind_field = self.consume("FIELD").value
                pipeline.append({"$unwind": f"${unwind_field}"})
            elif stage == "limit":
                limit_value = int(self.consume("VALUE").value)
                pipeline.append({"$limit": limit_value})
            elif stage == "skip":
                skip_value = int(self.consume("VALUE").value)
                pipeline.append({"$skip": skip_value})
            elif stage == "project":
                project_list = {}
                while self.current_token() and self.current_token().type == "FIELD":
                    current_field = self.consume("FIELD").value
                    project_list[current_field]=1
                    #project_list.append(current_field)
                    #projection = {field: 1 for field in fields}
                pipeline.append({"$project": project_list})
            #NoSQL operation
            elif stage == "group":
                group_field = self.consume("FIELD").value  # Consume the FIELD token for the group stage
                group_operations = {}  # To store parsed group operations
                group_operations['_id'] = f"${group_field}"
            # Iterate until a non-group-related token or end of the stream
                while self.current_token().type == "GROUP_OPERATOR":
                    current_operator = self.consume("GROUP_OPERATOR").value  # Consume the GROUP_OPERATOR token
                    current_value = self.consume("VALUE").value  # Consume the VALUE token
                    current_field = self.consume("FIELD").value
                    if current_operator =='calculate':
                        group_operations[current_value]={'$sum':f"${current_field}"}
                    elif current_operator =='collect':
                        group_operations[current_value]={'$push':f"${current_field}"}
                    elif current_operator =='list':
                        group_operations[current_value]={'$addToSet':f"${current_field}"}
                    #group_operations.append({current_value:{current_operator: current_field}})

                pipeline.append({"$group":group_operations})

        #my_children_node = ASTNode("AGGREGATION_CHILDREN", pipeline)
        return ASTNode("AGGREGATION_PIPELINE", value=local_collection, children=pipeline)

    def parse_generate_query(self):
        print("Enter the function: ")
        pipeline = []
        verb_node = self.consume("KEYWORD")
        local_collection = self.consume("TABLE_NAME").value
        select_items = []
        pipeline.append(f"FROM {local_collection}")
        while self.current_token() and self.current_token().type == "AGGREGATION_OPERATOR":
            print("Enter the aggreation in SQL")
            operator = self.consume("AGGREGATION_OPERATOR")
            stage = operator.value.lower()
            print("my current aggregation operator: ", operator)
            print("my stage is: ", stage)
            # SQL operation
            if stage == "join":
                foreign_collection =  self.consume("TABLE_NAME").value
                local_field = self.consume("FIELD").value
                logical_operator = self.consume("LOGICAL_OPERATOR").value
                foreign_field = self.consume("FIELD").value
                pipeline.append(f"JOIN {foreign_collection} ON {local_collection}.{local_field} = {foreign_collection}.{foreign_field}")
            elif stage == "sort":
                sort_field = self.consume("FIELD").value
                sort_order = self.consume("SORT_OPERATOR").value
                sort_query=f"ORDER BY {sort_field} " + "ASC" if sort_order == "increasingly" else f"ORDER BY {sort_field} " + "DESC"
                pipeline.append(sort_query)
            elif stage == "limit":
                limit_value = int(self.consume("VALUE").value)
                pipeline.append(f"LIMIT {limit_value}")
            elif stage == "project":
                while self.current_token() and self.current_token().type == "FIELD":
                    current_field = self.consume("FIELD").value
                    current_table = self.consume("TABLE_NAME").value
                    select_items.append(current_table+"."+current_field)
                    #project_list.append(current_field)
                    #projection = {field: 1 for field in fields}
            #NoSQL operation
            elif stage == "group":
                group_field = self.consume("FIELD").value  # Consume the FIELD token for the group stage
                group_table = self.consume("TABLE_NAME").value
                pipeline.append(f"GROUP BY {group_table}.{group_field}")
                #group_operations = {}  # To store parsed group operations
                #group_operations['_id'] = f"${group_field}"
            # Iterate until a non-group-related token or end of the stream
                while self.current_token().type == "GROUP_OPERATOR":
                    current_operator = self.consume("GROUP_OPERATOR").value  # Consume the GROUP_OPERATOR token
                    current_value = self.consume("VALUE").value.strip("\"")  # Consume the VALUE token
                    current_field = self.consume("FIELD").value
                    current_table = self.consume("TABLE_NAME").value
                    if current_operator =='calculate':
                        select_items.append(f"SUM({current_table}.{current_field}) AS {current_value}")
                        #group_operations[current_value]={'$sum':f"${current_field}"}
                #pipeline.append({"$group":group_operations})
        pipeline.append(select_items)
        #my_children_node = ASTNode("AGGREGATION_CHILDREN", pipeline)
        return ASTNode("GENERATE_PIPELINE", value=local_collection, children=pipeline)

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
    
    def content(self):
        content = [self.single_content()]
        while self.current_token() and self.current_token().value in ["and", "or", "nor"]:
            operator_token = self.consume()  # LOGICAL_OPERATOR
            next_content = self.single_content() # figure out the next condition
            #contents.append(ASTNode("LOGICAL_OPERATOR", value=operator_token.value))
            content.append(next_content)
        return ASTNode("CONTENT", content)

    def single_condition(self):
        # Single condition
        field_node = self.field()
        relation_node = self.relation()
        value_node = self.value()
        return ASTNode("SINGLE_CONDITION", [field_node, relation_node, value_node])
    
    def atom_content(self):
        field_node = self.field()
        value_node = self.value()
        return ASTNode("ATOM_CONTENT", [field_node, value_node])
    
    def single_content(self):
        s_content=[]
        while self.current_token() and self.current_token().value not in ["and", "or", "nor"]:
            s_content.append(self.atom_content())
        return ASTNode("SINGLE_CONTENT", s_content)

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
        if ast.type == "QUERY" or ast.type == "SELECT_QUERY" or ast.type == "DELETE_QUERY" or ast.type == "INSERT_QUERY" or ast.type == "UPDATE_QUERY" or ast.type == "AGGREGATION_PIPELINE" or ast.type == "GENERATE_PIPELINE":
            print("It is Query.")
            return self.analyze_query(ast)
        else:
            raise SemanticError(f"Unsupported AST node type: {ast.type}")
    
    # start from the root of the AST, both verb and conditions are examined.
    def analyze_query(self, node):
        print("The node at analyze_query is: ", node)
        if node.type != "AGGREGATION_PIPELINE" and node.type != "GENERATE_PIPELINE":
            """Analyze the root query node based on SQL and NoSQL"""
            for child in node.children:
                #print("child type:", type(child))
                # only for aggregation in MongoDB
                if isinstance(child, dict):
                    continue
                # PENDING: If the type of the child is verb, we need to check whether it is valid.
                if child and child.type=="TABLE_NAME":
                    analyze_table= child.value
                # If these are conditions, it is required to analyze their conditions
                if child and child.type == "CONDITION":
                    #print("Check condition")
                    self.analyze_condition(child, analyze_table)

    # For multiple conditions, each individual condition is examined properly.
    def analyze_condition(self, node, table_name):
        print("The node at analyze_condition method is: ", node)
        """check the condition node"""
        for child in node.children:
            if child.type == "SINGLE_CONDITION":
                #print("Single Condition?")
                self.analyze_single_condition(child, table_name)
            elif child.type == "LOGICAL_OPERATOR":
                #print("Double Condition?")
                continue
            else:
                raise SemanticError(f"Unexpected node type in CONDITION: {child.type}")
    
    # Each single condition is checked precisely.
    def analyze_single_condition(self, node, table_name):
        print("The node analyzed: ", node)
        """examine multiple conditions"""
        field_node = node.children[0]
        relation_node = node.children[1]
        value_node = node.children[2]

        #print(f"output ? {field_node}, {relation_node}, {value_node}")

        # check whether the field node is empty
        field = field_node.value
      
       
        # If the field is not in the symbol table, it is required to raise an error.
        my_check=False
        for table_name, fields in symbol_table.items():
            if field in fields:
                my_check=True
                break
        if my_check==False:
            raise SemanticError(f"Field '{field}' is not defined in the symbol table.")
        #if field not in self.symbol_table:
            #raise SemanticError(f"Field '{field}' is not defined in the symbol table.")

        # check the expected type of its value -> [int, double, string, ...]
        # print(self.symbol_table)
        expected_type = self.symbol_table[table_name][field]
        #print("The expected type is: " + expected_type)

        value = value_node.value # [The corresponding value of this field]
        #print("My value is: " + value)

        # If both of them do not match, a semantic error will be raised.
        if not self.check_type_match(expected_type, value):
            raise SemanticError(f"Value '{value}' does not match the expected type '{expected_type}' for field '{field}' in '{self.target}'.")

        # relational operator
        relation = relation_node.value
        #print("My relation is: " + relation)
        # whether it uses and, or, nor, etc....
        #if not self.check_relation_valid(expected_type, relation):
            #raise SemanticError(f"Relation operator '{relation}' is not valid for field '{field}' with type '{expected_type}'.")

    def check_type_match(self, expected_type, value):
        # check whether the value is matched with the expected type
        # PENDING: Extension object, array, number, etc...
        if self.target == "SQL":
            # SQL type matching
            if expected_type == "INTEGER" and value.isdigit():
                return True
            if expected_type == "REAL" and self.is_float(value):
                return True
            if expected_type == "TEXT" and value.startswith("\"") and value.endswith("\""):
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
        if target not in ["SQL", "NoSQL"]:
            raise ValueError("Target must be 'SQL' or 'NoSQL'")
        self.target = target
     
     # It's time to generate the query based on Abstract Syntax Tree
     # PENDING: The name of the table needs to be modified based on the table name.
    def generate(self, ast):
        #print("my generate: ", ast)
        if ast.type == "QUERY" or ast.type == "SELECT_QUERY" or ast.type == "DELETE_QUERY" or ast.type == "INSERT_QUERY" or ast.type == "UPDATE_QUERY" or ast.type == "AGGREGATION_PIPELINE" or ast.type == "GENERATE_PIPELINE":
            if self.target == "SQL":
                return self.generate_sql(ast)
            elif self.target == "NoSQL":
                return self.generate_mongo(ast)
        else:
            raise ValueError(f"Unsupported AST node type: {ast.type}")
   
    def generate_sql(self, ast):
        if ast.type == "GENERATE_PIPELINE":
            
            # Select x1, x2, x3 FROM 
            # x1, x2, x3, ... ast.children[pipeline - 1]
            # string 
            my_query=f"SELECT "
            
            my_field=""
            current_fields_candidate = ast.children[len(ast.children) - 1]
            for index in range(0, len(current_fields_candidate)):
                if index != 0 and index != len(ast.children) - 1:
                   my_field += ", "
                my_field += current_fields_candidate[index]
            
            my_query += f'{my_field}'       
            
            for index in range(0, len(ast.children) - 1):
               my_query += f' {ast.children[index]}'

            return my_query + ";" 
        
        table_name=ast.children[1].value
        #condition_node = next(child for child in ast.children if child.type == "CONDITION")
        if ast.type == "SELECT_QUERY":
            #columns = kwargs.get("columns", "*")
            #joins = kwargs.get("joins", [])
            #group_by = kwargs.get("group_by")
            #having = kwargs.get("having")
            #order_by = kwargs.get("order_by")
            #sort_order = kwargs.get("sort_order", "ASC")
            
            condition_node = next(child for child in ast.children if child.type == "CONDITION")
            query = f"SELECT * FROM {table_name}"
            '''
            for join in joins:
                join_table = join.get("table")
                join_type = join.get("type", "INNER").upper()
                join_condition = join.get("on")
                if not join_table or not join_condition:
                    raise ValueError("JOIN requires 'tables' and 'on'")
                query += f"{join_type} JOIN {join_table} ON {join_condition}"

            if group_by:
                query += f" GROUP BY {group_by}"

            if having:
                query += f" HAVING {having}"
            
            if order_by:
                query += f" ORDER BY {order_by} {sort_order}"
            '''
            if condition_node:
               conditions = self.traverse_conditions(condition_node, for_sql = True)
               query += f" WHERE {' '.join(conditions)}"
            return query + ";"
        elif ast.type == "INSERT_QUERY":
            content_node = next(child for child in ast.children if child and child.type == "CONTENT")
            # finish
            # Process WHERE conditions
            query_collected = {}
            if content_node:
                contents = self.traverse_contents(content_node, for_sql=True)
                query_collected = contents
            return f"INSERT INTO {table_name} {query_collected};"
        elif ast.type == "UPDATE_QUERY":
            set_clause_node = next(child for child in ast.children if child and child.type == "SET_CLAUSE")
            condition_node = next((child for child in ast.children if child and child.type == "CONDITION"), None)

            # Process SET clause
            updates = {}
            for update_pair in set_clause_node.children:
                field_node, value_node = update_pair.children
                updates[field_node.value] = value_node.value.strip("'\"")  # Remove quotes

            # Process WHERE conditions
            
            #updates = kwargs.get("updates", {})
            #if not updates:
                #raise ValueError("UPDATE requires 'updates'")
            #set_clause = ', '.join(f'''{k}='{v.replace("'", "''")}' ''' for k, v in updates.items() if v is not None)
            #if not set_clause:
                #raise ValueError("No valid updated provided")
            
            query = f"UPDATE {table_name} SET "
            
            updates_length = len(updates)
            index=0

            for key in updates.keys():
                if index != 0 and index != updates_length - 1:
                    query += ','

                query += f'{key} = {updates[key]}'
                index += 1
                

           
            if condition_node:
                conditions = self.traverse_conditions(condition_node, for_sql = True)
                #query += f" WHERE {' '.joins(conditions[0])}"
                query += f" WHERE {' '.join(conditions)}"

            
            return query + ";"
        elif ast.type == "DELETE_QUERY":
            joins = kwargs.get("joins", [])
            query = f"DELETE FROM {table_name}"

            if joins:
                for join in joins:
                    join_table = join.get("table")
                    join_type = join.get("type", "INNER").upper()
                    join_condition = join.get("on")
                    if not join_table or not join_condition:
                        raise ValueError("JOIN requires 'table' and 'on'")
                    query += f" {join_type} JOIN {join_table} ON {join_condition}"
            
            if condition_node:
                conditions = self.traverse_conditions(condition_node, for_sql= True)
                query += f" WHERE {' '.join(conditions)}"
            
            return query + ";"
        else:
            raise ValueError(f"Unsupported operation: {operation}")


    # # Pending: implement various kinds of sql queries
    # #          Solve the question based on the SQL query
    # def generate_sql(self, condition_node, table_name):
    #     """The output of the SQL is reproduced"""
    #     conditions = self.traverse_conditions(condition_node, for_sql=True)
    #     return f"SELECT * FROM {table_name} WHERE {' '.join(conditions)};"

    # Pending: implement various kinds of NoSQL queries
    #          Solve the question based on the NoSQL query
    def generate_mongo(self, ast):
        print("my generate ast tree: ", ast)
        if ast.type == "AGGREGATION_PIPELINE":
            return f"db.{ast.value}.aggregate({ast.children});"
        
        
        table_name=ast.children[1].value
       
        if ast.type == "SELECT_QUERY":
            # finish
            conditions = self.traverse_conditions(ast, for_sql=False)
            ##projection = kwargs.get("projection")
            ##sort = kwargs.get("sort")
            ##skip = kwargs.get("skip", 0)
            ##limit = kwargs.get("limit", 0)
            query=conditions[0]
            print(f"search: {query}")
            #query = {"$and": conditions} if len(conditions) > 1 else conditions[0]
            mongo_query = f"db.{table_name}.find({query})"

            ##if projection:
                ##mongo_query += f", {projection}"
            ##mongo_query += ")"

            ##if sort:
                ##mongo_query += f".sort({sort})"
            ##if skip > 0:
                ##mongo_query += f".skip({skip})"
            ##if limit > 0:
                ##mongo_query += f".limit({limit})"
            return mongo_query + ";"
        elif ast.type == "INSERT_QUERY":
            content_node = next(child for child in ast.children if child and child.type == "CONTENT")
            # finish
            # Process WHERE conditions
            query = {}
            if content_node:
                contents = self.traverse_contents(content_node, for_sql=False)
                query = contents
            insert_query = f"db.{table_name}."
            insert_query += "insertMany" if len(query)>1 else "insertOne"
            insert_query += f"({query});"
            return insert_query
            '''
            documents = kwargs.get("documents", [])
            if not documents:
                raise ValueError("INSERT requires 'documents' to be provided")
            
            if isinstance(documents, list):
                return f"db.{table_name}.insertMany({json.dump(documents)});"
            else: 
                return f"db.{table_name}.insertOne({json.dump(documents)});"
            '''
        elif ast.type == "UPDATE_QUERY":
            # finish
            # Extract SET clause and conditions from the AST
            set_clause_node = next(child for child in ast.children if child and child.type == "SET_CLAUSE")
            condition_node = next((child for child in ast.children if child and child.type == "CONDITION"), None)

            # Process SET clause
            updates = {}
            for update_pair in set_clause_node.children:
                field_node, value_node = update_pair.children
                updates[field_node.value] = value_node.value.strip("'\"")  # Remove quotes

            # Process WHERE conditions
            query = {}
            if condition_node:
                conditions = self.traverse_conditions(condition_node, for_sql=False)
                query = conditions[0]
                #query = {"$and": conditions} if len(conditions) > 1 else conditions[0]
                #print(f"conditions: {conditions}")
                #print(f"query: {query}")

            # Generate the MongoDB update query
            #update_many = kwargs.get("update_many", False)  # Optional: control updateOne or updateMany
            update_many = True
            update_query = f"db.{table_name}."
            update_query += "updateMany" if update_many else "updateOne"
            update_query += f"({json.dumps(query)}, {json.dumps({'$set': updates})});"
            #update_query += f"({query}, {'$set': {updates}});"
            return update_query
        
        elif ast.type == "DELETE_QUERY":
            #finish
            condition_node = next((child for child in ast.children if child and child.type == "CONDITION"), None)
            print("The condition node for delete is: ", condition_node)
            query = {}
            if condition_node:
                conditions = self.traverse_conditions(condition_node, for_sql=False)
                query = conditions[0]
            print("The result for delete is: ", query)
            #delete_many = kwargs.get("delete_many", False)
            #query = {"$and": conditions} if len(conditions) > 1 else conditions[0]
            delete_query = f"db.{table_name}."
            #delete_query += "deleteMany" if delete_many else "deleteOne"
            delete_query += "deleteMany"
            delete_query += f"({json.dumps(query)};"
            return delete_query
        
        # elif ast.type == "AGGREGATE_QUERY":
        #     pipeline = []

        #     if ast:
        #         conditions = self.traverse_conditions(ast, for_sql=False)
        #         match_stage = {'$match': {'$and': conditions} if len(conditions) > 1 else conditions[0]}
        #         pipeline.append(match_stage)
            
        #     for stage in ["unwind", "group", "sort", "project", "lookup", "limit", "skip"]:
        #         if stage in kwargs:
        #             pipeline.append(f"${stage}: kwargs['${stage}]")
           
        #     return f"db.{table_name}.aggregate({json.dumps(pipeline, indent=2)});"
        else:
            raise ValueError(f"Unsupported operation: {operation}")
        

         
    def traverse_conditions(self, node, for_sql=True):
        # implement variouus conditions to resolve each type
        conditions = []
        #print(f"111   my node: {node}")
        #print(f"222   my children: {node.children}")
        #for child in node.children:
        #for i in range(len(node.children)):
        i=0
        while i<len(node.children):
            #print(f"node.children[{i}]: {node.children[i]}")
            # single condition: >, <, =, !=, >=, <=
            if node.children[i].type == "SINGLE_CONDITION":
                #print("SINGLE_CONDITION")
                field = node.children[i].children[0].value
                relation = node.children[i].children[1].value
                value = node.children[i].children[2].value
                if for_sql:
                    # If it is SQL, convert it into SQL
                    if isinstance(value, str) and not value.isdigit():
                        value = f"'{value}'"
                    sql_relation = self.map_sql_operator(relation)
                    conditions.append(f"{field} {sql_relation} {value}")
                else:
                    # If it is noSQL, convert it into noSQL
                    mongo_operator = self.map_mongo_operator(relation)
                    conditions.append({ field: { mongo_operator: value } })
            # logical operator: and, or, nor
            elif node.children[i].type == "LOGICAL_OPERATOR":
                #print("LOGICAL_OPERATOR")
                operator = node.children[i].value.lower()
                if for_sql:
                    conditions.append(node.children[i].value.upper())
                else:
                    last_condition = conditions.pop() if conditions else None
                    my_next=ASTNode("RIGHT_VALUE", [node.children[i+1]])
                    i=i+1
                    #print(f"my next: {my_next}")
                    next_conditions = self.traverse_conditions(my_next, for_sql = False)
                    #next_conditions = self.traverse_conditions(node.children[i+1], for_sql = False)
                    mongo_operator = {"and": "$and", "or": "$or", "nor": "$nor"}.get(operator)
                    if mongo_operator and last_condition:
                        #print("1")
                        #print(f"last condition{last_condition}")
                        #print(f"next condition{next_conditions}")
                        #conditions.append(last_condition)
                        conditions.append({mongo_operator: [last_condition] + next_conditions})
                        #print("append end")
                    elif mongo_operator:
                        #print("2")
                        conditions.append({mongo_operator: next_conditions})
            # multiple conditions
            elif node.children[i].type == "CONDITION":
               #print("CONDITION")
               sub_conditions = self.traverse_conditions(node.children[i], for_sql)
               #print(f"sub_conditions: {sub_conditions}")
               if for_sql:
                    conditions.append(f"({' '.join(sub_conditions[0])})")
               else:
                    conditions.append(sub_conditions[0])
                    #conditions.append({"$and": sub_conditions} if len(sub_conditions) > 1 else sub_conditions[0])
                    #if mongo_operator:
                        #conditions.append({mongo_operator: sub_conditions} if len(sub_conditions) > 1 else sub_conditions[0])
                    #else:
                        #conditions.append(sub_conditions)
            #print(f"traverse_conditions: {conditions}")
            i=i+1
        return conditions

    def traverse_contents(self, node, for_sql=False):
        sql_fields = []
        sql_values = []
        nosql_docs = []

        if node.type == "CONTENT":
            for child in node.children:
                if child.type == "SINGLE_CONTENT":
                    field_list = []
                    value_list = []
                    nosql_doc = {}
                    for atom in child.children:
                        if atom.type == "ATOM_CONTENT":
                            field = None
                            value = None
                            for attr in atom.children:
                                if attr.type == "FIELD":
                                    field = attr.value
                                elif attr.type == "VALUE":
                                    value = attr.value
                            if field and value:
                                field_list.append(field)
                                value_list.append(f"'{value}'")  # Ensure SQL values are quoted
                                nosql_doc[field] = value
                    sql_fields = field_list  # Overwritten for every content; fields are consistent
                    sql_values.append(f"({', '.join(value_list)})")
                    nosql_docs.append(nosql_doc)
        # Generate SQL statement
        sql_insert_values = f"({', '.join(sql_fields)}) VALUES {', '.join(sql_values)}"
        
        if for_sql:
            return sql_insert_values
        else:
            return nosql_docs

    def map_sql_operator(self, relation):
        return {
            "equal to": "=",
            "greater than": ">",
            "less than": "<",
            "is not equal to": "!=",
            "greater than or equal to": ">=",
            "less than or equal to": "<="
        }.get(relation.lower(), relation)

    def map_mongo_operator(self, relation):
        return {
            "equal to": "$eq",
            "greater than": "$gt",
            "less than": "$lt",
            "is not equal to": "$ne",
            "greater than or equal to": "$gte",
            "less than or equal to": "$lte"
        }.get(relation.lower(), relation)
    

# The main function
def main():
    # Step 1: Input data for testing
    sql_file_paths = [
        "../Database/SQL/data/Manufacturer_data.csv",
        "../Database/SQL/data/Product_data.csv",
        "../Database/SQL/data/Reviewer_data.csv",
        "../Database/SQL/data/Warehouse_data.csv",
        "../Database/SQL/data/Vendor_data.csv",
        "../Database/SQL/data/Relationship_product_manufacturer_data.csv"
    ]
    nosql_file_paths = [
        "../Database/NoSQL/city-mongodb.json",  # 示例文件 1
        "../Database/NoSQL/country-mongodb.json",                 # 示例文件 2
        "../Database/NoSQL/countrylanguage-mongodb.json",             # 示例文件 3
        "../Database/NoSQL/sampleCultureProducts.json"
    ]
    my_file_paths = sql_file_paths
    #nosql_file_path = "../Database/NoSQL/sampleCultureProducts.json"  # Replace with your test JSON file path
    # 提取文件名（包括扩展名）
    ## process_table_names(nosql_file_paths)
    process_table_names(my_file_paths)
    '''
    file_name_with_ext = os.path.basename(nosql_file_paths)  # 输出: sampleCultureProducts.json
    global my_table_name
    # 去掉扩展名
    my_table_name = os.path.splitext(file_name_with_ext)[0]  # 输出: sampleCultureProducts
    print("table name is: "+my_table_name)
    '''

    # Step 2: Load the symbol table and select SQL or NoSQL
    try:
        ##target = generate_separate_symbol_tables(nosql_file_paths)
        target = generate_separate_symbol_tables(my_file_paths)                
        print(f"Target detected: {target}")
        print(f"Symbol Table: {symbol_table}")
    except ValueError as e:
        print(f"Error loading symbol table: {e}")
        return
    
    global TOKEN_RULES
    TOKEN_RULES = [
    ("KEYWORD", r"\b(search for|find|select|insert|add|append|create|put|write|store|include|populate|update|modify|edit|change|alter|refresh|adjust|correct|revise|replace|delete|remove|erase|clear|drop|destroy|truncate|discard|sum|count|avg|min|max|aggregate|generate)\b"),
    ("RELATION", r"\b(equal to|greater than|less than|not equal to|greater than or equal to|less than or equal to|set|>=|<=|>|<|!=)\b"),  # 关系运算符[relational operators]
    ("FIELD", generate_field_patterns(symbol_table)),  # 字段名[fields]  # Pending: change it into the specific fields
    #("FIELD", r"\b(_id|shopifyId|title|descriptionHTML|handle|vendor|productType|tags|options|variants|images|createdAt|updatedAt|publishedAt)\b"),
    ("LOGICAL_OPERATOR", r"\b(and|or|nor)\b"),  # 逻辑操作符[logical operators]
    #("VALUE", r"(\d+|'.*?')"),  # 数值或字符串值[string or number]
    #("AS", r"\b(as)\b"),
    ("VALUE", r"(\d+|'.*?'|\".*?\")"),
    ("AGGREGATION_OPERATOR", r"\b(join|group|sort|unwind|project|limit|skip|lookup)\b"),
    ("GROUP_OPERATOR", r"\b(calculate|collect|list)\b"),
    ("SORT_OPERATOR", r"\b(decreasingly|increasingly)\b"),
    ("TABLE_NAME", generate_field_patterns2(my_table_names)),
    ("WHITESPACE", r"\s+"),  # 空格（可以跳过） [whitespace]
    ("INVALID", r".")  # 无效字符[invalid characters]
]
    print("token roles")
    print(TOKEN_RULES)
    print("symbol_table")
    print(symbol_table)
    # Step 3: Lexical analysis
    #nosql
    #select:(ok)
    #input_query = "aaa want to search for product from sampleCultureProducts table whose shopifyId is equal to \"aaa\" and vendor is equal to \"High-End Boutique Shops\""
    #update:(ok)
    #input_query = "I want to update the sampleCultureProducts table to set title equal to \"Handcrafted Indian Pashmina Shawl\" where shopifyId is equal to  \"HandCrafted-Pashmina-Shawl-One\" and handle is equal to \"HPS\"."
    #delete:(ok)
    #input_query = "I want to delete products from sampleCultureProducts table whose shopifyId is equal to \"aaa\" and vendor is equal to \"High-End Boutique Shops\""
    #insert one:(ok)
    #input_query = "insert one user records into sampleCultureProducts table: shopifyId \"USC-1\" title \"University of Southern California\", with the handle \"USC\""
    #insert many:(ok)
    #input_query = "insert two user records into sampleCultureProducts table: shopifyId \"USC-1\" title \"University of Southern California\", with the handle \"USC\" and shopifyId \"DSCI551-1\" title \" Data Management \", with the handle \"DSCI551\""
    #aggregate:
    #input_query = "I want to aggregate a query in MongoDB on the city-mongodb including the following stages: join the country-mongodb collection on CountryCode and code, aliasing the results as \"Country_and_City\". Later, join the countrylanguage-mongodb collection on CountryCode and CountryCode, aliasing the results as \"Country_and_Language\", group the documents by CountryCode to calculate \"totalPopulation\" as the values of total Population, collect \"cities\" as the values of Name, list \"languages\" as the values of unique Language, then sort by totalPopulation decreasingly, unwind cities, skip the first 10 results, limit to 5 results, last finally project only the CountryCode, totalPopulation, cities, languages."
    
    #sql
    #select
    #input_query = "aaa want to search for product from Product_data table whose length is greater than 70 and material is equal to \"Wood\"."
    #insert one:(ok)
    #input_query = "insert one reviewer records into Reviewer_data table: id 101 country \"United States\" age 30 gender \"Female\" phone_number \"123-456-789\" email \"aaa@gmail.com\" introduction \"I'm Echo.\""
    #insert many:(ok)
    #input_query = "insert two user records into Reviewer_data table: id 101 country \"United States\" age 30 gender \"Female\" phone_number \"123-456-789\" email \"aaa@gmail.com\" introduction \"I'm Echo.\" and id 102 country \"China\" age 16 gender \"Male\" phone_number \"213-456-999\" email \"bbb@outlook.com\" introduction \"I'm Tom.\""
    #update:(ok)
    #input_query = "I want to update the Vendor_data table to set address equal to \"NULL\" where is_operated is equal to 0 and year is less than 1970."
    #delete
    #generate:
    #input_query = "I want to generate a query in Mysql on the Product_data including the following steps: join the Relationship_product_manufacturer_data table on id and product_id. Later, join the Manufacturer_data table on id and manufacturer_id."
    input_query = "I want to generate a query in Mysql on the Product_data including the following steps: join the Relationship_product_manufacturer_data table on id and product_id. Later, join the Manufacturer_data table on id and manufacturer_id, group the table by origin in Product_data table to calculate \"totalPrice\" as the values of total price in Product_data table, then sort by totalPrice decreasingly, limit to 5 results, last finally project only the id in Product_data, name in Product_data, image in Product_data, totalPrice in Product_data."

    tokens = lexical_analysis(input_query)
    print(input_query)

    print(f"Tokens: {tokens}")

    # Step 4: Parsing
    parser = Parser(tokens)
    try:
        ast = parser.parse()
        print(f"Abstract Syntax Tree (AST): {ast}")
    except SyntaxError as e:
        print(f"Parsing error: {e}")
        return

    # Step 5: Semantic analysis
    semantic_analyzer = SemanticAnalyzer(symbol_table, target)
    try:
        semantic_analyzer.analyze(ast)
        print("Semantic analysis passed.")
    except SemanticError as e:
        print(f"Semantic analysis error: {e}")
        return

    # Step 6: Query generation
    code_generator = CodeGenerator(target)
    try:
        if target == "SQL":
            sql_query = code_generator.generate(ast)
            print(f"Generated SQL Query: {sql_query}")
        elif target == "NoSQL":
            mongo_query = code_generator.generate(ast)
            print(f"Generated NoSQL Query: {mongo_query}")
    except ValueError as e:
        print(f"Query generation error: {e}")
        return

if __name__ == "__main__":
    main()
