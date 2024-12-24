from re import fullmatch

UNEXPECTED_TOKEN = "Unexpected token: {}"
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

def is_valid_json_number(token):
    return fullmatch(r'^-?(0|[1-9]\d*)(\.\d+)?([eE][-+]?\d+)?$', token) is not None

def convert_to_python_number(token):
    try: # integer
        return int(token)
    except ValueError:
        pass
    try: # float
        return float(token)
    except ValueError:
        pass
    try: # complex
        return complex(token)
    except ValueError:
        pass
    return None

def create_list_from_tokens(tokens):
    lst = []
    stack = [] # lexical state
    
    seen_value = False

    for idx, tkn in enumerate(tokens, 0):
        if tkn == "[" or tkn == "{": # opening token
            stack.append((tkn, idx))
        elif tkn == "]": # list
            if len(stack) == 0:
                raise JsonDecodeError(UNEXPECTED_TOKEN.format(tkn))
            start_tkn = stack.pop()
            if start_tkn[0] == "[":
                if len(stack) == 0:
                    seen_value = True
                    lst.append(create_list_from_tokens(tokens[start_tkn[1] + 1: idx]))
            else:
                raise JsonDecodeError(NEVER_CLOSED.format(start_tkn[0]))
        elif tkn == "}": # dict
            if len(stack) == 0:
                raise JsonDecodeError(UNEXPECTED_TOKEN.format(tkn))
            start_tkn = stack.pop()
            if start_tkn[0] == "{":
                if len(stack) == 0:
                    seen_value = True
                    lst.append(create_dict_from_tokens(tokens[start_tkn[1] + 1: idx]))
            else:
                raise JsonDecodeError(NEVER_CLOSED.format(start_tkn[0]))
        elif len(stack) == 0:
            if tkn == ",": # comma
                if not seen_value:
                    raise JsonDecodeError(UNEXPECTED_TOKEN.format(tkn))
                seen_value = False
            elif tkn in SPECIAL_VALUES:
                if seen_value:
                    raise JsonDecodeError(UNEXPECTED_TOKEN.format(tkn))
                seen_value = True
                lst.append(SPECIAL_VALUES[tkn])
            elif is_valid_json_number(tkn):
                if seen_value:
                    raise JsonDecodeError(UNEXPECTED_TOKEN.format(tkn))
                seen_value = True
                lst.append(convert_to_python_number(tkn))
            else:
                if seen_value:
                    raise JsonDecodeError(UNEXPECTED_TOKEN.format(tkn))
                seen_value = True
                lst.append(convert_to_python_string(tkn))

    if len(stack) > 0:
        raise JsonDecodeError(NEVER_CLOSED.format(stack.pop()[0]))
    
    if len(lst) > 0 and not seen_value:
        raise JsonDecodeError("Unexpected trailing ,")

    return lst

def create_dict_from_tokens(tokens):
    #TODO: make this for dict
    dic = {}
    stack = [] # lexical state

    for idx, tkn in enumerate(tokens, 0):
        if tkn == "[" or tkn == "{": # opening token
            stack.append((tkn, idx))
        elif tkn == "]": # append list
            if len(stack) == 0:
                raise JsonDecodeError(UNEXPECTED_TOKEN.format(tkn))
            start_tkn = stack.pop()
            if start_tkn[0] == "[":
                if len(stack) == 0:
                    lst.append(create_list_from_tokens(tokens[start_tkn[1] + 1: idx]))
            else:
                raise JsonDecodeError(NEVER_CLOSED.format(start_tkn[0]))
        elif tkn == "}": # append dict
            if len(stack) == 0:
                raise JsonDecodeError(UNEXPECTED_TOKEN.format(tkn))
            start_tkn = stack.pop()
            if start_tkn[0] == "{":
                if len(stack) == 0:
                    lst.append(create_dict_from_tokens(tokens[start_tkn[1] + 1: idx]))
            else:
                raise JsonDecodeError(NEVER_CLOSED.format(start_tkn[0]))
    if len(stack) > 0:
        raise JsonDecodeError(NEVER_CLOSED.format(stack.pop()[0]))
    
    return dic

def loads(string):
    data = {"data": None, "type": None}
    
    tokens = tokenize(string)
    if len(tokens) == 0: # no tokens
        return data
    
    if tokens[0] == "[":
        if tokens[-1] == "]":
            data["data"] = create_list_from_tokens(tokens[1:-1])
            data["type"] = "list"
        else:
            raise JsonDecodeError(NEVER_CLOSED.format(tokens[0]))
    elif tokens[0] == "{":
        if tokens[-1] == "}":
            data["data"] = create_dict_from_tokens(tokens[1:-1])
            data["type"] = "dict"
        else:
            raise JsonDecodeError(NEVER_CLOSED.format(tokens[0]))
    else:
        raise JsonDecodeError(UNEXPECTED_TOKEN.format(tokens[0]))

    return data
