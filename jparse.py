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
#TODO implement from_string
