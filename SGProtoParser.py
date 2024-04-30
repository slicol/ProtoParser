import logging
import chardet


########################################################################
class MTFileUtils:
    def ReadText(fileName):
        try:
            f = open(fileName, 'r',encoding="utf-8")
            text = f.read()
            f.close()
            return text
        except Exception as e:
            logging.warning(f'ReadText() {fileName} error:{e}')
            logging.warning(f'Will read by ReadTextAnyEncoding()')
            pass    
        pass
        return MTFileUtils.ReadTextAnyEncoding(fileName)


    def ReadTextAnyEncoding(fileName):
        with open(fileName, 'rb') as f:
            content = f.read()
            encoding = chardet.detect(content)['encoding']
            logging.warning(f'ReadTextAnyEncoding() encoding = {encoding}')
            return content.decode(encoding)
        pass

############################################################################################
    
class Text:
    def __init__(self, val:str) -> None:
        self.val = val
        pass

class Token:
    def __init__(self, val:str, pos:int) -> None:
        self.idx = -1
        self.pos = pos
        self.val = val
        pass

    def GetNextPos(self)->int:
        return self.pos + len(self.val)

############################################################################################

def SkipSpace(source:Text, i:int)->int:
    while i < len(source.val) and IsSpaceChar(source.val[i]) : i += 1
    return i

def SkipCommentSingleLine(source:Text, i:int)->int:
    if i >= len(source.val) - 1: return i
    if source.val[i:i+2] != '//': return i
    i += 2
    while i < len(source.val) and not IsLineBreaker(source.val[i]): i += 1
    i += 1
    return i


def SkipStringConstant(source:Text, i:int)->int:
    if not IsQuotationMarks(source.val[i]): return i
    mark = source.val[i]
    i += 1
    while i < len(source.val) and source.val[i] != mark: i += 1
    i += 1
    return i

def SkipCommentMultiLine(source:Text, i:int)->int:
    if i >= len(source.val) - 1: return i
    if source.val[i:i+2] != '/*': return i
    i += 2
    while i < len(source.val) - 1 and source.val[i:i+2] != '*/': i += 1
    i += 2
    return i

def IsSpaceChar(letter:str)->bool:
    if letter == ' ': return True
    if letter == '\t': return True
    if letter == '\n': return True
    if letter == '\r': return True    
    return False

def IsQuotationMarks(letter:str)->bool:
    if letter == '"': return True
    if letter == "'": return True
    return False

def IsLineBreaker(letter:str)->bool:
    if letter == '\n': return True
    if letter == '\r': return True
    return False

def IsWordChar(letter:str)->bool:
    if letter >= 'a' and letter <= 'z': return True
    if letter >= 'A' and letter <= 'Z': return True
    if letter >= '0' and letter <= '9': return True
    if letter == '_': return True
    return False

def IsSpecialChar(letter:str)->bool:
    return not IsWordChar(letter)

def NextToken(source:Text, i:int)->Token:
    while i < len(source.val):
        begin = i
        i = SkipSpace(source, i)
        i = SkipCommentSingleLine(source, i)
        i = SkipSpace(source, i)
        i = SkipCommentMultiLine(source, i)
        i = SkipSpace(source, i)
        if begin == i : break
    pass
    begin = i
    while i < len(source.val):
        if IsQuotationMarks(source.val[i]):
            i = SkipStringConstant(source, i)
            return Token(source.val[begin:i], begin)
        pass
        if IsSpaceChar(source.val[i]):
            return Token(source.val[begin:i], begin)
        pass
        if IsSpecialChar(source.val[i]):
            if begin == i:
                return Token(source.val[i], i)
            else:
                return Token(source.val[begin:i], begin)
            pass
        pass
        i += 1
    pass
    return None
        

def ParserTokens(source_text:str)->list:
    source = Text(source_text)
    result = []
    token = NextToken(source, 0)
    while token != None:
        token.idx = len(result)
        result.append(token)
        token = NextToken(source, token.GetNextPos())
    pass
    return result


def SkipBraceTokens(tokens:list, i:int)->int:
    if i >= len(tokens): return i
    if tokens[i].val != '{': return i
    i += 1
    stack = 1
    while i < len(tokens) :
        if tokens[i].val == '{': 
            stack += 1
        elif tokens[i].val == '}': 
            stack -= 1
            if stack == 0:
                i += 1
                break
            pass
        pass
        i += 1
    pass
    return i


def GetTextFromTokens(tokens:list)->str:
    stack = 0
    indent = ''
    i = 0
    lines = []
    line = ''
    while i < len(tokens):
        t:Token = tokens[i]
        if t.val == ';': 
            line = line.strip()
            line += t.val
            lines.append(indent + line)
            line = ''
        elif t.val == '{':
            line = line.strip()
            lines.append(indent + line)

            line = t.val
            lines.append(indent + line)
            line = ''

            stack += 1
            indent = '    ' * stack
        elif t.val == '}':
            line = line.strip()
            if line != '':
                lines.append(indent + line)
            pass

            line = t.val

            stack -= 1
            indent = '    ' * stack
            lines.append(indent + line)
            line = ''
            pass
        else:
            line += t.val
            line += ' '
        pass
        i+=1
    pass
    if line != '': lines.append(line)

    result = ''
    i = 0
    while i < len(lines) - 1:
        line = lines[i]
        result += line + "\n"
        i += 1
    pass
    if i < len(lines):
        line = lines[i]
        result += line
    pass

    return result

############################################################################################

class ASTKeyword:
    syntax = 'syntax'
    package = 'package'
    message = 'message'
    enum = 'enum'
    oneof = 'oneof'
    pass


class ASTNodeKind:
    ANK_Block = 'Block'
    ANK_Statement = 'Statement'
    ANK_Declaration = 'Declaration'
    pass

class ASTNode:
    def __init__(self, kind, parent) -> None:
        self.kind = kind
        self.tokens = []
        self.parent = parent
        self.children = []
        pass

    def GetFullText(self)->str:
        result = self.parent.GetFullText()
        result += '.' + GetTextFromTokens(self.tokens)
        return result





class ASTBlock(ASTNode):
    def __init__(self, parent:ASTNode) -> None:
        super().__init__(ASTNodeKind.ANK_Block, parent)
        self.statements = []
        pass

    def GetFullText(self) -> str:
        result = ''
        if self.parent != None:
            result = self.parent.GetFullText()
            #result += '.'
        pass
        return result
        

    def DumpAST(self, intent = ''):
        for node in self.statements:
            node:ASTStatement = node
            text = GetTextFromTokens(node.decl.tokens)
            logging.warning(f'{intent}{text}') 
            if node.impl != None:
                block:ASTBlock = node.impl
                block.DumpAST(intent + '    ')
            pass
        pass

    def DumpAllStatements(self):
        all_statements = []
        self.CollectAllStatements(all_statements)
        for node in all_statements:
            node:ASTStatement = node
            text = node.GetFullText()
            logging.warning(f'{text}')
        pass
        return
    

    def CollectAllStatements(self, result:list):
        for node in self.statements:
            node:ASTStatement = node
            result.append(node)
            if node.impl != None:
                block:ASTBlock = node.impl
                block.CollectAllStatements(result)
            pass
        pass        
        return


    def AddStatement(self, node:ASTNode):
        self.children.append(node)
        self.statements.append(node)
        node.parent = self
        pass

    def ParserTokens(self, tokens:list):
        self.tokens = tokens
        text = GetTextFromTokens(tokens)
        logging.debug(f'ASTBlock.ParserTokens() \n{text}')

        node, i = ASTBlock.NextASTStatement(self.tokens, 0)
        while node != None:
            node:ASTStatement = node
            if len(node.tokens) > 0:
                self.AddStatement(node)
            pass
            node, i = ASTBlock.NextASTStatement(self.tokens, i)
        pass
        return
    
    
    def NextASTStatement(tokens:list, i:int)->tuple:
        begin = i
        while i < len(tokens):
            t:Token = tokens[i]
            if t.val == '{':
                i = SkipBraceTokens(tokens, i)
                node = ASTStatement(None)
                node.ParserTokens(tokens[begin:i])
                return node, i
            elif t.val == ';':
                node = ASTStatement(None)
                node.ParserTokens(tokens[begin:i])
                return node, i + 1
            pass
            i += 1
        pass
        return None, i
    
        


class ASTStatement(ASTNode):
    def __init__(self, parent:ASTNode) -> None:
        super().__init__(ASTNodeKind.ANK_Statement, parent)
        self.decl = None # Decl, required
        self.impl = None # Block, optional
        pass

    def GetFullText(self)->str:
        result = self.parent.GetFullText()
        result += '.' + GetTextFromTokens(self.decl.tokens)
        return result


    def ParserTokens(self, tokens:list):
        self.tokens = tokens
        text = GetTextFromTokens(tokens)
        logging.debug(f'ASTStatement.ParserTokens() \n{text}')
        
        i = 0
        while i < len(tokens) and tokens[i].val != '{' and tokens[i].val != ';': i += 1

        # parser decl
        self.decl = ASTDeclaration(self)
        self.decl.ParserTokens(tokens[0:i])
        self.children.append(self.decl)
        
        # parser impl
        if i < len(tokens):
            self.impl = ASTBlock(self)
            self.impl.ParserTokens(tokens[i+1:-1])
            self.children.append(self.impl)
        pass
        return


class ASTDeclType:
    Unkown = 'Unkown'
    Syntax = 'Syntas'
    Package = 'Package'
    Message = 'Message'
    Enum = 'Enum'
    EnumField = 'EnumField'
    MessageField = 'MessageField'
    pass

class ASTDeclaration(ASTNode):
    def __init__(self, parent:ASTNode) -> None:
        super().__init__(ASTNodeKind.ANK_Declaration, parent)
        self.type = ASTDeclType.Unkown
        self.name = ''
        self.value = None
        self.decoration = ''
        pass

    def ParserTokens(self, tokens:list):
        self.tokens = tokens
        text = GetTextFromTokens(tokens)
        logging.debug(f'ASTDeclaration.ParserTokens() \n{text}')
        # todo
        return
    
    



class ASTDiffResult:
    def __init__(self) -> None:
        self.additions = set()
        self.deletions = set()
        pass


class ASTModule(ASTBlock):
    def __init__(self, name:str) -> None:
        super().__init__(None)
        self.name = name
        pass

    def DumpAST(self, intent=''):
        logging.warning('--------------------------------------------------------------------------------------------')
        logging.warning('ASTModule.DumpAST()')
        logging.warning('--------------------------------------------------------------------------------------------')
        super().DumpAST(intent)
        logging.warning('--------------------------------------------------------------------------------------------')
    
    def DumpAllStatements(self):
        logging.warning('--------------------------------------------------------------------------------------------')
        logging.warning('ASTModule.DumpAllStatements()')
        logging.warning('--------------------------------------------------------------------------------------------')
        super().DumpAllStatements()
        logging.warning('--------------------------------------------------------------------------------------------')

    def DiffTo(self, base)->ASTDiffResult:
        base:ASTModule = base
        result = ASTDiffResult()

        base_statements = []
        base.CollectAllStatements(base_statements)
        base_statements_text = set()
        for node in base_statements:
            node:ASTStatement = node
            base_statements_text.add(node.GetFullText())
        pass

        self_statements = []
        self.CollectAllStatements(self_statements)
        self_statements_text = set()
        for node in self_statements:
            node:ASTStatement = node
            self_statements_text.add(node.GetFullText())
        pass        

        result.additions = self_statements_text.difference(base_statements_text)
        result.deletions = base_statements_text.difference(self_statements_text)

        return result



############################################################################################

def ParserAST(mod_name:str, tokens:list)->ASTModule:
    module = ASTModule(mod_name)
    module.ParserTokens(tokens)
    return module

############################################################################################

def ProtoParser(filepath:str)->ASTModule:
    logging.info(f'ProtoParser() filepath = {filepath}')
    text:str = MTFileUtils.ReadText(filepath)
    tokens = ParserTokens(text)
    module = ParserAST('test', tokens)
    return module

############################################################################################

def ProtoDiff(currfile:str, basefile:str)->ASTDiffResult:
    logging.info(f'ProtoParser() currfile = {currfile}, basefile = {basefile}')
    base = ProtoParser(basefile)
    curr = ProtoParser(currfile)
    return curr.DiffTo(base)

############################################################################################
