def parse_blk(data: str, start: int = 0) -> (dict, int):
    from enum import Enum
    from itertools import islice
    from re import findall

    class States(Enum):
        ID_NEXT = 1
        ID = 2
        BLOCK_NEXT = 3
        TYPE_NEXT = 4
        TYPE = 5
        EQUALS_NEXT = 6
        VALUE_NEXT = 7
        VALUE = 8
        STRING = 9

    def unexpected():
        raise SyntaxError(f'Unexpected character #{i}: {ch}')

    def matrix(m: str) -> list | float:
        m = m.strip()

        if not m.startswith('[') or not m.endswith(']'):
            xs = m.split(',')
            if len(xs) > 1:
                return [matrix(v) for v in xs]
            try:
                v = float(m)
                return v
            except ValueError:
                raise SyntaxError(f'Invalid matrix format {s}')

        m = m[1:-1]
        return [matrix(v) for v in findall(r'\[([^]]+)]', m)]

    state = States.ID_NEXT
    s = ''
    _id = ''
    _type = ''
    result = {}
    enum_data = iter(enumerate(data))
    next(islice(enum_data, start, start), None)
    for i, ch in enum_data:
        match state:
            case States.ID_NEXT:
                if ch.isalnum() or ch in ['_', '.']:
                    s = ch
                    state = States.ID
                elif ch.isspace():
                    pass
                elif ch == '}':
                    return result, i + 1
                else:
                    unexpected()
            case States.ID:
                if ch == ':':
                    _id = s
                    state = States.TYPE_NEXT
                elif ch.isspace():
                    _id = s
                    state = States.BLOCK_NEXT
                elif ch.isalnum() or ch in ['_', '.']:
                    s += ch
                elif ch == '{':
                    _id = s
                    result[_id], n = parse_blk(data, i + 1)
                    next(islice(enum_data, n - i - 1, n - i - 1), None)
                    state = States.ID_NEXT
                else:
                    unexpected()
            case States.BLOCK_NEXT:
                if ch == '{':
                    result[_id], n = parse_blk(data, i + 1)
                    next(islice(enum_data, n - i - 1, n - i - 1), None)
                    state = States.ID_NEXT
                elif ch.isspace():
                    pass
                else:
                    unexpected()
            case States.TYPE_NEXT:
                if ch.isalpha():
                    s = ch
                    state = States.TYPE
                elif ch.isspace():
                    pass
                else:
                    unexpected()
            case States.TYPE:
                if ch.isalnum():
                    s += ch
                elif ch == '=':
                    _type = s
                    if _type not in ['i', 'r', 't', 'b', 'm', 'p2', 'p3', 'p4']:
                        raise ValueError(f'Unknown type {_type}')
                    state = States.VALUE_NEXT
                elif ch.isspace():
                    _type = s
                    state = States.EQUALS_NEXT
                else:
                    unexpected()
            case States.EQUALS_NEXT:
                if ch == '=':
                    state = States.VALUE_NEXT
                elif ch.isspace():
                    pass
                else:
                    unexpected()
            case States.VALUE_NEXT:
                if ch == '"':
                    s = ''
                    state = States.STRING
                elif ch.isalnum() or ch in '[+-':
                    s = ch
                    state = States.VALUE
                elif ch.isspace():
                    pass
                else:
                    unexpected()
            case States.STRING:
                if ch == '"':
                    state = States.ID_NEXT
                    result[_id] = s
                else:
                    s += ch
            case States.VALUE:
                if ch in [';', '\n', '"']:
                    state = States.ID_NEXT
                    result[_id] = s
                    match _type:
                        case 'i':
                            result[_id] = int(s)
                        case 'r':
                            result[_id] = float(s)
                        case 't':
                            result[_id] = s
                        case 'b':
                            if s not in ['yes', 'true', 'no', 'false']:
                                raise ValueError(f'Unknown boolean value {s}')
                            result[_id] = s in ['yes', 'true']
                        case 'm':
                            result[_id] = matrix(s)
                        case 'p2' | 'p3' | 'p4':
                            result[_id] = tuple(float(v) for v in s.split(','))
                            if (r := len(result[_id])) != (e := int(_type[1])):
                                raise ValueError(
                                    f'Expected {e} values, got {r}')
                        case '_':
                            raise SyntaxError(f'Unknown type {_type}')
                elif ch.isalnum() or ch.isspace() or ch in '_/"[].,+-':
                    s += ch
                elif ch == '}':
                    result[_id] = s
                    return result, i + 1
                else:
                    unexpected()
            case _:
                raise SyntaxError(f'Unknown state {state}')
    return result, len(data)