class JsonDecodeError(Exception):
    # costum exception class for json decoding
    def __init__(self, msg):
        super().__init__(msg)
        self.message = msg

def tokenize(json_str):
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
    container_openers = ["{", "["]
    container_closers = ["}", "]"]
    stack = [] # container checking
    i = 0 # traversal index
    str_len = len(json_str)

    while i < str_len and json_str[i].isspace(): # neglect starting white space
        i += 1
   
    # no data
    if i >= str_len:
        return data
    
    # 0 for dict, 1 for array, -1 out of bounds
    state = -1

    # check outer container
    if json_str[i] not in container_openers:
        raise JsonDecodeError(f"Invalid starting character {json_str[i]}")
    
    # traverse the string
    while i < str_len:
        if json_str[i] in container_openers: # add container to stack
            if state >= 0 and len(stack) <= 0:
                raise JsonDecodeError(f"Unexpected character {json_str[i]}")
            stack.append(json_str[i])
            state = container_openers.index(json_str[i])
        elif json_str[i] in container_closers: # close container
            if len(stack) < 1:
                raise JsonDecodeError(f"Unexpected character {json_str[i]}")
            elif stack[-1] != container_openers[container_closers.index(json_str[i])]:
                raise JsonDecodeError(f"{stack.pop()} was never closed")
            stack.pop()
        i += 1
    
    # check valid encapsulation
    if len(stack) > 0:
        raise JsonDecodeError(f"{stack.pop()} was never closed")

    return data
