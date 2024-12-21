class JsonDecodeError(Exception):
    # costum exception class for json decoding
    def __init__(self, msg):
        super().__init__(msg)
        self.message = msg

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

    # check outer container
    if json_str[i] not in container_openers:
        raise JsonDecodeError(f"Invalid starting character {json_str[i]}")
    
    # traverse the string
    while i < str_len:
        if json_str[i] in container_openers: # add container to stack
            stack.append(json_str[i])
        elif json_str[i] in container_closers:
            if stack[-1] != container_openers[container_closers.index(json_str[i])]:
                raise JsonDecodeError(f"{stack.pop()} was never closed")
            stack.pop()
        i += 1
    
    # check valid encapsulation
    if len(stack) > 0:
        raise JsonDecodeError(f"{stack.pop()} was never closed")

    return data
