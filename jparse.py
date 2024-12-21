UNEXPECTED_TOKEN = "Unexpected token: {}"
NEVER_CLOSED = "{} was never closed"

class JsonDecodeError(Exception):
    # costum exception class for json decoding
    def __init__(self, msg):
        super().__init__(msg)
        self.message = msg

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

def loads(json_str):
    data = {"data": None}
    tokens = tokenize(json_str) # get tokens
    if len(tokens) == 0:
        return data
    print(tokens)
    stack = [] # lexical analysis
    openers = ["{", "["]
    closers = ["}", "]"]
    if tokens[0] not in openers:
        raise JsonDecodeError(UNEXPECTED_TOKEN.format(tokens[0]))
    combination_list = []
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
            combination_list.append((opener[0], index, "ol"[openers.index(opener[1])]))
    return combination_list
