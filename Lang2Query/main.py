import re
from typing import List, Tuple

#词法分析模块
# 定义 Token 类型
class Token:
    def __init__(self, token_type: str, value: str):
        self.type = token_type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"

# 定义词法规则
TOKEN_RULES = [
    ("KEYWORD", r"\b(search for|get|find|select)\b"),  # 动词
    ("RELATION", r"\b(equal to|greater than|less than|is not equal to|>=|<=|>|<)\b"),  # 关系运算符
    ("FIELD", r"\b(id|name|price|age)\b"),  # 字段名
    ("LOGICAL_OPERATOR", r"\b(and|or)\b"),  # 逻辑操作符
    ("VALUE", r"(\d+|'.*?')"),  # 数值或字符串值
    ("WHITESPACE", r"\s+"),  # 空格（可以跳过）
    ("INVALID", r".")  # 无效字符
]

# 构建词法分析器
def lexical_analysis(input_text: str) -> List[Token]:
    tokens = []
    pos = 0
    while pos < len(input_text):
        match = None
        for token_type, pattern in TOKEN_RULES:
            regex = re.compile(pattern)
            match = regex.match(input_text, pos)
            if match:
                if token_type == "WHITESPACE":  # 跳过空格
                    pos = match.end()
                    break
                elif token_type == "INVALID":  # 跳过 INVALID，但记录警告
                    #print(f"Warning: Invalid character '{match.group(0)}' at position {pos}")
                    pos = match.end()
                    break
                else:
                    token_value = match.group(0)
                    tokens.append(Token(token_type, token_value))
                    pos = match.end()
                    break
        if not match:
            raise SyntaxError(f"Illegal character at position {pos}: {input_text[pos]}")
    return tokens

#语法分析模块
class ASTNode:
    """抽象语法树节点"""
    def __init__(self, node_type: str, children=None, value=None):
        self.type = node_type
        self.children = children if children else []
        self.value = value

    def __repr__(self):
        if self.value:
            return f"ASTNode({self.type}, {self.value})"
        return f"ASTNode({self.type}, {self.children})"

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, expected_type=None):
        token = self.current_token()
        print(f"Test: Current Token -> {token}, Expected -> {expected_type}")
        if token is None:
            raise SyntaxError("Unexpected end of input.")
        if expected_type and token.type != expected_type:
            print(f"Debug: Current Token -> {token}, Expected -> {expected_type}")
            raise SyntaxError(f"Expected {expected_type} but got {token.type}.")
        self.pos += 1
        return token

    def parse(self):
        return self.query()

    def query(self):
        """解析 QUERY -> VERB OBJECT CONDITION"""
        verb_node = self.verb()
        #object_node = self.object()
        condition_node = self.condition()
        #return ASTNode("QUERY", [verb_node, object_node, condition_node])
        return ASTNode("QUERY", [verb_node, condition_node])

    def verb(self):
        """解析 VERB"""
        token = self.consume("KEYWORD")
        return ASTNode("VERB", value=token.value)

    def object(self):
        """解析 OBJECT"""
        token = self.consume("FIELD")
        return ASTNode("OBJECT", value=token.value)

    def condition(self):
        """解析多条件"""
        print("多条件")
        conditions = [self.single_condition()]
        while self.current_token() and self.current_token().value in ["and", "or"]:
            operator_token = self.consume()  # LOGICAL_OPERATOR
            next_condition = self.single_condition()
            conditions.append(ASTNode("LOGICAL_OPERATOR", value=operator_token.value))
            conditions.append(next_condition)
        return ASTNode("CONDITION", conditions)

    def single_condition(self):
        """解析单个条件"""
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

#语义分析模块
class SemanticError(Exception):
    """自定义语义错误"""
    pass

class SemanticAnalyzer:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table

    def analyze(self, ast):
        if ast.type == "QUERY":
            return self.analyze_query(ast)
        else:
            raise SemanticError(f"Unsupported AST node type: {ast.type}")

    def analyze_query(self, node):
        """检查 QUERY 节点"""
        for child in node.children:
            if child.type == "CONDITION":
                self.analyze_condition(child)

    def analyze_condition(self, node):
        """检查 CONDITION 节点"""
        for child in node.children:
            if child.type == "SINGLE_CONDITION":
                self.analyze_single_condition(child)
            elif child.type == "LOGICAL_OPERATOR":
                # LOGICAL_OPERATOR 不需要进一步检查
                continue
            else:
                raise SemanticError(f"Unexpected node type in CONDITION: {child.type}")

    def analyze_single_condition(self, node):
        """检查单个条件"""
        field_node = node.children[0]
        relation_node = node.children[1]
        value_node = node.children[2]

        # 检查字段是否合法
        field = field_node.value
        if field not in self.symbol_table:
            raise SemanticError(f"Field '{field}' is not defined in the symbol table.")

        # 检查字段类型与值类型是否匹配
        expected_type = self.symbol_table[field]
        value = value_node.value
        if not self.check_type_match(expected_type, value):
            raise SemanticError(f"Value '{value}' does not match the expected type '{expected_type}' for field '{field}'.")

        # 检查关系运算符是否合法
        relation = relation_node.value
        if not self.check_relation_valid(expected_type, relation):
            raise SemanticError(f"Relation operator '{relation}' is not valid for field '{field}' with type '{expected_type}'.")

    def check_type_match(self, expected_type, value):
        """检查字段类型和值是否匹配"""
        if expected_type == "int" and value.isdigit():
            return True
        if expected_type == "float" and self.is_float(value):
            return True
        if expected_type == "string" and value.startswith("'") and value.endswith("'"):
            return True
        return False

    def is_float(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def check_relation_valid(self, field_type, relation):
        """检查关系运算符是否合法"""
        numeric_relations = ["equal to", "greater than", "less than", ">=", "<=", ">", "<"]
        if field_type in ["int", "float"] and relation in numeric_relations:
            return True
        string_relations = ["equal to", "is not equal to"]
        if field_type == "string" and relation in string_relations:
            return True
        return False
#符号表
symbol_table = {
        "id": "int",
        "name": "string",
        "price": "float",
        "age": "int"
    }
#代码生成模块
class CodeGenerator:
    def __init__(self, target="SQL"):
        self.target = target

    def generate(self, ast, table_name="items"):
        if ast.type == "QUERY":
            return self.generate_query(ast, table_name)
        else:
            raise ValueError(f"Unsupported AST node type: {ast.type}")

    def generate_query(self, node, table_name):
        """生成查询语句"""
        condition_node = next(child for child in node.children if child.type == "CONDITION")
        if self.target == "SQL":
            return self.generate_sql(condition_node, table_name)
        elif self.target == "MongoDB":
            return self.generate_mongo(condition_node, table_name)
        else:
            raise ValueError(f"Unsupported target: {self.target}")

    def generate_sql(self, condition_node, table_name):
        """生成 SQL 查询"""
        conditions = self.traverse_conditions(condition_node, for_sql=True)
        return f"SELECT * FROM {table_name} WHERE {' '.join(conditions)};"

    def generate_mongo(self, condition_node, table_name):
        """生成 MongoDB 查询"""
        conditions = self.traverse_conditions(condition_node, for_sql=False)
        if len(conditions) == 1:
            query = conditions[0]
        else:
            query = { "$and": conditions }
        return f"db.{table_name}.find({query});"

    def traverse_conditions(self, node, for_sql=True):
        """遍历条件节点并生成条件"""
        conditions = []
        for child in node.children:
            if child.type == "SINGLE_CONDITION":
                field = child.children[0].value
                relation = child.children[1].value
                value = child.children[2].value
                if for_sql:
                    sql_relation = self.map_sql_operator(relation)
                    conditions.append(f"{field} {sql_relation} {value}")
                else:
                    mongo_operator = self.map_mongo_operator(relation)
                    conditions.append({ field: { mongo_operator: value } })
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
    analyzer = SemanticAnalyzer(symbol_table)
    try:
        analyzer.analyze(ast)
        print("Semantic analysis passed. The query is valid.")
    except SemanticError as e:
        print(f"Semantic Error: {e}")
    #代码生成模块
    print("\ncode generator")
    # 生成 SQL 查询
    sql_generator = CodeGenerator(target="SQL")
    sql_query = sql_generator.generate(ast)
    print("Generated SQL Query:")
    print(sql_query)
    # 生成 MongoDB 查询
    mongo_generator = CodeGenerator(target="MongoDB")
    mongo_query = mongo_generator.generate(ast)
    print("\nGenerated MongoDB Query:")
    print(mongo_query)

