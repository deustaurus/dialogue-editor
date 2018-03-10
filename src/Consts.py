from enum import Enum

nameblacklistcsharp = [
    'abstract', 'add', 'as', 'ascending', 'async',
    'await', 'base', 'bool', 'break', 'by', 'byte',	 
    'case', 'catch', 'char', 'checked', 'class',
    'const', 'continue', 'decimal', 'default',
    'delegate', 'descending', 'do', 'double', 'dynamic', 
    'else', 'enum', 'equals', 'explicit', 'extern', 
    'false', 'finally', 'fixed', 'float', 'for', 
    'foreach', 'from', 'get', 'global',	'goto',
    'group', 'if', 'implicit', 'in', 'int', 'interface',	 
    'internal', 'into', 'is', 'join', 'let', 'lock',
    'long', 'namespace', 'new', 'null', 'object',	 
    'on', 'operator', 'orderby', 'out', 'override',	 
    'params', 'partial', 'private', 'protected',	 
    'public', 'readonly', 'ref', 'remove', 'return',	 
    'sbyte', 'sealed', 'select', 'set', 'short',
    'sizeof', 'stackalloc', 'static', 'string',
    'struct', 'switch', 'this', 'throw', 'true', 
    'try', 'typeof', 'uint', 'ulong', 'unchecked', 
    'unsafe', 'ushort', 'using', 'value', 'var', 
    'virtual', 'void', 'volatile', 'where', 'while', 'yield',
]

def validateName(name):
    if len(name) < 1:
        return ValidateResult.LENGTH
    if name.lower() in nameblacklistcsharp:
        return ValidateResult.RESERVED_NAME
    return ValidateResult.SUCCESS

class ValidateResult(Enum):
    SUCCESS = 0
    NAME_CONFLICT = 1
    RESERVED_NAME = 2
    LENGTH = 3

class EntryColors(Enum):
    RED = 'Red',
    BLUE = 'Blue',
    GREEN = 'Green',