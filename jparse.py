UNEXPECTED_TOKEN = "Unexpected token: {}"
UNEXPECTED_TOKEN_AFTER = UNEXPECTED_TOKEN + " after {}"
NEVER_CLOSED = "{} was never closed"
SPECIAL_VALUES = {"true": True, "false": False, "null": None}

class JsonDecodeError(Exception):
    # costum exception class for json decoding
    def __init__(self, msg):
        super().__init__(msg)
        self.message = msg

def convert_to_python_string(s):
    """
    parse valid json string to standard python string
    """
    invalid_string_err = "Invalid string token: {}"
    if s[0] != "\"":
        raise JsonDecodeError(invalid_string_err.format(s))
    is_terminated = False
    is_escaped = False
    is_hex = False
    hex_string = ""
    res = ""
    for char in s[1:]:
        if is_terminated: # continued after termination
            raise JsonDecodeError(f"Unexpected character after string temination: {char}")
        
        if char in [chr(i) for i in range(32)] + [chr(127)]: #control characters
            raise JsonDecodeError(invalid_string_err.format(s))
        
        if is_hex:
            if char.lower() not in [str(x) for x in range(10)] + ["a", "b", "c", "d", "e", "f"]:
                raise JsonDecodeError(invalid_string_err.format(s))
            hex_string += char
            if len(hex_string) == 4:
                res += repr(chr(int(hex_string, 16)))
                is_hex = False
                hex_string = ""
            continue

        if char == "\\": # escape
            is_escaped = True
            continue
        
        if char == "\"": # terminator
            is_terminated = True
            continue

        if is_escaped: # escapable characters
            match char:
                case "n":
                    res += "\\n"
                case "t":
                    res += "\\t"
                case "r":
                    res += "\\r"
                case "b":
                    res += "\\b"
                case "f":
                    res += "\\f"
                case "\\":
                    res += "\\\\"
                case "\"":
                    res += "\\\""
                case "u":
                    is_hex = True
                case _:
                    raise JsonDecodeError(invalid_string_err.format(s))
            is_escaped = False
            continue
        
        res += char # other characters

    if is_escaped or is_hex: # unresolved escape
        raise JsonDecodeError(invalid_string_err.format(s))
    return res

def tokenize(json_str):
    """
    takes a json string and returns a lit of possible tokens
    """
    tokens = []
    special_characters = "{}[],:"
    whitespace_characters = "\n\t \r"
    str_len = len(json_str)
    
    i = 0 #traversal pointer
    while i < str_len:
        char = json_str[i]
        if char in whitespace_characters:
            pass # ignore valid whitespace
        elif char in special_characters: # special characters
            tokens.append(char)
        elif char == "\"": # handle strings
            tmp = ""
            while i < str_len:
                tmp += json_str[i]
                i += 1
                if json_str[i] == "\"" and json_str[i - 1] != "\\":
                    tmp += "\""
                    break
            tokens.append(tmp)
        else: # handle other
            tmp = ""
            while i < str_len and (json_str[i] not in special_characters and json_str[i] not in whitespace_characters):
                tmp += json_str[i]
                i += 1
            tokens.append(tmp)
            continue
        i += 1
    return tokens

def create_list_from_tokens(tokens, lexical_plan):
    lst = []
    i = 1 # token traversal pointer
    seen_value = False
    while i < len(tokens) - 1:
        if tokens[i] == "[": # array
            if seen_value:
                raise JsonDecodeError(UNEXPECTED_TOKEN_AFTER.format(tokens[i], tokens[i - 1]))
            list_plan = lexical_plan.pop(0) # remove blueprint form queue
            lst.append(create_list_from_tokens(tokens[list_plan[0]: list_plan[1] + 1], lexical_plan))
            seen_value = True
            i = list_plan[1]
        elif tokens[i] == "{": #object
            if seen_value:
                raise JsonDecodeError(UNEXPECTED_TOKEN_AFTER.format(tokens[i], tokens[i - 1]))
            list_plan = lexical_plan.pop(0) # remove blueprint form queue
            lst.append(create_dict_from_tokens(tokens[list_plan[0] + 1: list_plan[1] + 1], lexical_plan))
            seen_value = True
            i = list_plan[1]
        elif tokens[i] in SPECIAL_VALUES: # special values
            if seen_value:
                raise JsonDecodeError(UNEXPECTED_TOKEN_AFTER.format(tokens[i], tokens[i - 1]))
            lst.append(SPECIAL_VALUES[tokens[i]])
            seen_value = True
        elif tokens[i] == ",": # comma
            if (not seen_value):
                raise JsonDecodeError(UNEXPECTED_TOKEN_AFTER.format(tokens[i], tokens[i - 1]))
            seen_value = False
        else: #Base case FOR NOW TODO: update
            if seen_value:
                raise JsonDecodeError(UNEXPECTED_TOKEN_AFTER.format(tokens[i], tokens[i - 1]))
            seen_value = True
        i += 1
    if len(lst) > 0 and not seen_value: #check for trailing comma
        raise JsonDecodeError(UNEXPECTED_TOKEN_AFTER.format(tokens[i], tokens[i - 1]))
    return lst

def create_dict_from_tokens(tokens, lexical_plan):
    dic = {}
    return dic

def get_lexical_plan(tokens): 
    stack = [] # lexical analysis
    openers = ["{", "["]
    closers = ["}", "]"]
    if tokens[0] not in openers:
        raise JsonDecodeError(UNEXPECTED_TOKEN.format(tokens[0]))
    lexical_plan = []
    stack.append((0, tokens[0]))
    for index, token in enumerate(tokens[1:], 1):
        if token in openers:
            if len(stack) == 0:
                raise JsonDecodeError(UNEXPECTED_TOKEN.format(token))
            stack.append((index, token))
        elif token in closers:
            if len(stack) == 0:
                raise JsonDecodeError(UNEXPECTED_TOKEN.format(token))
            if stack[-1][1] != openers[closers.index(token)]:
                raise JsonDecodeError(NEVER_CLOSED.format(stack.pop()[1]))
            opener = stack.pop()
            lexical_plan.append((opener[0], index))
    if len(stack) > 0:
        raise JsonDecodeError(NEVER_CLOSED.format(stack[-1][1]))
    return lexical_plan

def loads(json_str):
    data = {"data": None}
    tokens = tokenize(json_str) # get tokens
    if len(tokens) == 0:
        return data

    lexical_plan = sorted(get_lexical_plan(tokens), key=lambda x: x[0]) # object blueprint
    if tokens[0] == "[": # outer list
        data["data"] = create_list_from_tokens(tokens, lexical_plan[1:])
    elif tokens[0] == "{": # outer obj
        data["data"] = create_dict_from_tokens(tokens, lexical_plan[1:])
    return data
