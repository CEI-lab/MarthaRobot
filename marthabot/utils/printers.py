"""
A series of functions to pretty print various objects
"""


import pprint
import typing

INEDENTATION_INCREMENT = 3


def pretty_list(l: list) -> str:
    lens = [len(i) for i in l]
    if str(l) < 80:
        return str(l)
    elif all([(s < 40) for s in lens]):
        col = "["
        for el in l:
            col += str(el) + "\n"
        col += "]"
    else:
        pass
    pass


def pretty_nested(it: typing.Iterable, indent: int = 0):
    raw = pretty_print(it).split("\n")
    indented = [(" " * indent * INEDENTATION_INCREMENT) + line for line in raw]
    return indented


def pretty_dict(d: dict) -> str:
    col = ""
    for k, v in d:
        col += str(k) + ": " + pretty_print(v) + "\n"
    return "{" + pretty_nested(col, 1) + "}"


mapping = {list: pretty_list, dict: pretty_dict}


def pretty_print(o: object) -> str:
    t = type(o)
    if t in mapping:
        return mapping[t]


pp = pprint.PrettyPrinter(
    indent=3,
    sort_dicts=False,
)


testdict = {"a": "aval", "b": "bval"}
testlist = [1, 2, 3, 4, 5]
testlist = ["a", "b", "c", "d"]
testlist = [
    "a very long piece of texta very long piece of texta very long piece of texta very long piece of texta very long piece of texta very long piece of texta very long piece of texta very long piece of texta very long piece of texta very long piece of texta very long piece of text",
    "a short piece of text",
    "a very long piece of texta very long piece of texta very long piece of texta very long piece of texta very long piece of texta very long piece of text",
]
jsontest = {
    "clientIPAddress": "10.49.29.86",
    "cmd": "SetSpeedCommand",
    "id": 1686586559,
    "leftSpeed": 0,
    "priority": 1,
    "receivingPort": 28200,
    "response": "SUCCESS",
    "rightSpeed": 0,
}

pp.pprint(jsontest)
