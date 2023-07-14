from collections import OrderedDict
from typing import Callable
import re
import pylint


def scream(p: str)->str:
    return p.upper()

cases = OrderedDict([
    ("flat"            , re.compile("[a-z0-9]+")),
    ("scream_flat"     , re.compile(scream("[a-z0-9]+"))),
    ("camel"           , re.compile("[a-z]+(?:[A-Z0-9]+[a-z0-9]*)*")),
    ("upper_camel"     , re.compile("([A-Z][a-z0-9]*)*")),
    ("snake"           , re.compile("[a-z0-9]+(?:_[a-z0-9]+)*")),
    ("screaming_snake" , re.compile(scream("[a-z0-9]+(?:_[a-z0-9]+)*"))),
    ("camel_snake"     , re.compile("[A-Z][a-z0-9]+(?:_[A-Z]+[a-z0-9]*)*")),
    ("kebab"           , re.compile("[a-z0-9]+(?:-[a-z0-9]+)*")),
    ("screaming_kebab" , re.compile(scream("[a-z0-9]+(?:-[a-z0-9]+)*"))),
    # ("train"           , re.compile("[A-Z][a-z0-9]+(?:-[A-Z]+[a-z0-9]*)*")),
    # ("screaming_train" , re.compile(scream("[A-Z][a-z0-9]+(?:-[A-Z]+[a-z0-9]*)*"))),
])
splits = OrderedDict([
    ("camel"           , re.compile("[a-z]+|(?:[A-Z0-9]+[a-z0-9]*)")),
    ("upper_camel"     , re.compile("([A-Z]([a-z0-9])*)")),
])


class VariableName(str):

    def __new__(cls,vname: str) :
        obj = str.__new__(cls,vname)
        obj.case = obj._getCase(vname)
        obj.parts = obj._get_parts()
        obj.parts = [p.lower() for p in obj.parts]
        return obj


    def _getCase(self, name: str):
        for case, regex in cases.items():
            matching = regex.fullmatch(name)
            if matching:
                print(f"{name} matched with {case}")
                return case
        return "N/A"
    def _separate_regex(self, regex):
        pass

    def to_case(self,new_case:str):
        if new_case == "flat":
            return "".join(self.parts).lower()
        elif new_case == "scream_flat":
            return "".join(self.parts).upper()
        elif new_case == "camel":
            ret = self.parts[0]
            for p in self.parts[1:]:
                ret += p[0].upper() + p[1:].lower()
            return ret
        elif new_case == "upper_camel":
            ret = ""
            for p in self.parts:
                ret += p[0].upper() + p[1:].lower()
            return ret
        elif new_case == "snake":
            return "_".join(self.parts).lower()
        elif new_case == "screaming_snake":
            return "_".join(self.parts).upper()
        elif new_case == "camel_snake":
            ret = ""
            for p in self.parts:
                ret += p[0].upper() + p[1:].lower() + "_"
            return ret[:-1]
        elif new_case == "kebab":
            return "-".join(self.parts).lower()
        elif new_case == "screaming_kebab":
            return "-".join(self.parts).upper()
        
        

    def _get_parts(self):
        if self.case in ["flat","scream_flat"]:
            parts = "\n"
            while "".join(parts.split()).lower() != self.lower():
                parts = input(f"Type the words of variable name '{self}' separated by spaces, or press enter if only one word.\n                                 ")
                if parts == "":
                    parts = self
            return parts.split()
        elif self.case in ["snake","screaming_snake","camel_snake"]:
            return self.split("_")
        elif self.case in ["kebab","screaming_kebab"]:
            return self.split("-")
        elif self.case in ["camel","upper_camel"]:
            matches = re.finditer(splits[self.case],self)
            # print([m for m in matches])
            return [m.group(0) for m in matches]

    # def fromLine(line: str) -> VariableName:
    #     pass

# testobject = VariableName("testvarname")
# testobject = VariableName("TestVarName")
# print(testobject.parts)
# testobject = VariableName("test-var-name")
# print(testobject.parts)
# testobject = VariableName("test_var_name")
# print(testobject.parts)
# testobject = VariableName("Test_Var_Name")
# print(testobject.parts)
# testobject = VariableName("testvarname")
# print(testobject.parts)
# testobject = VariableName("testVarN")
# print(testobject.to_case("kebab"))







# unneeded - can just use strings and funcitons...
class RegexPattern(str):
    def __init__(self,pattern,modification: Callable[[str],str] = None) -> None:
        # if modification is None:
        if isinstance(pattern,str):
            regex = pattern
        elif isinstance(pattern,RegexPattern):
            regex = pattern
        else:
            raise Exception(f"Cannot create a RegexPattern with {pattern}")
        if modification:
            regex = modification(regex)
        super().__init__(regex)
