from copy import deepcopy
from typing import *
import re
    
# 规则元素 rule =  ['xxx', 'yyy', 'zzz']
class Rule:
    def __init__(self, i, c) -> None:
        self.__index = i
        self.__content = c

    @property
    def Index(self):
        return self.__index

    def __str__(self) -> str:
        return str(self.__content)

    def __len__(self) -> int:
        return len(self.__content)
    
    def __getitem__(self, i: int):
        return self.__content[i]

    def __iter__(self):
        return (ele for ele in self.__content)

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, list):
            return self.__content == __o
        elif not isinstance(__o, Rule):
            return False
        return self.Index == __o.Index

    def append(self, ele):
        self.__content.append(ele)


# 规则集元素 rules = [rule1 = [], rule2 = [], ...]
class Rules:
    # 构造函数—— __content 中存储的是字符串列表，比如 ['<expr>', "+", '<term>']
    # 为了方便后面区分，处理原始的文法时其中的尖括号之类不会被去掉
    def __init__(self) -> None:
        self.__content = []

    def __str__(self) -> str:
        strrule = []
        for rule in self.__content:
            strrule.append(''.join([('%s ' % s) for s in rule]))
        return ''.join([('  %s\n') % s for s in strrule])

    def __iter__(self):
        return (ele for ele in self.__content)

    def __len__(self) -> int:
        return len(self.__content)

    def __getitem__(self, i: int) -> list:
        return self.__content[i]

    def __delitem__(self, i: int) -> None:
        self.__content.pop(i)

    def __set__(self):
        return set(self.__content)

    def __iadd__(self, ele):
        self.__content.append(ele)
        return self

    def Append(self, ele: list):
        self.__content.append(ele)

    @classmethod
    def FromList(cls, lst):
        r = Rules()
        r.__content = deepcopy(lst)
        return r


# NonTerminals 类表示非终结符及其对应的若干产生式的集合
# 字典 __nts 里，键总是非终结符，
#               值是这个非终结符对应的 Rules
class NonTerminals:
    def __init__(self) -> None:
        self.__nts = dict()

    def __len__(self) -> int:
        return len(self.__nts)

    def __iter__(self):
        return iter(self.__nts.items())

    def __getitem__(self, s: str) -> Rules:
        return self.__nts[s]

    def __setitem__(self, i: str, value):
        self.__nts[i] = value

    def __str__(self):
        nts = []
        for (name, rules) in self.__nts.items():
            nts.append('%s:\n%s\n' % (str(name), str(rules)))
        return ''.join(nts)

    def GetName(self) -> list:
        return list(self.__nts.keys())

    def GetTermName(self) -> list:
        terminals = set()
        for rules in self.__nts.values():
            for rule in rules:
                for ele in rule:
                    if ele[0] != '<':
                        terminals.add(ele)
        return list(terminals)


# 获取BNF文件，并拆解为NonTerminals格式
class ParseBNF:
    def __init__(self, name: str) -> None:
        self.file = open(name, 'r', encoding='utf-8')
        self.line = re.findall('\\S+', self.file.readline())
        # 从文件读一行， 以空白符做分割， 获取一个元素list
        self.__index = 0

    def __del__(self) -> None:
        self.file.close()

    # 将新的一行转换为list
    def __nextLine(self) -> bool:
        line = self.file.readline()
        if not line:
            self.line = None
            return False
        self.line = re.findall('\\S+', line)
        return True
        
    # 从line中获取一个新的rule 并返回 如：[ expr, + , expr]
    def __nextRule(self):
        start = 0
        try:
            start = self.line.index('::=')
        except:
            start = self.line.index('|')
        
        rule = Rule(self.__index, self.line[start + 1:])
        self.__index += 1
        return rule

    # 创建一个新的 非终结符元组 (name , rules())
    # rules() 通过__nextrule()不断增长
    # 直到读到了下一个非终结符，或者换行/结尾
    def __nextNonTerminal(self):
        if not self.line or self.line[0][0] != '<':
            while self.__nextLine():
                if self.line[0][0] == '<':
                    break
            else:
                return None
        name = str(self.line[0])
        r = Rules()
        r += self.__nextRule()

        while True:
            self.__nextLine()
            if (not self.line) or self.line[0][0] == '<' or self.line[0][0] == '\n':
                break
            r += self.__nextRule()
        return (name, r)

    # 建立终结符集合 ，存放在NonTerminals中
    def Build(self) -> NonTerminals:
        nts = NonTerminals()
        while True:
            pack = self.__nextNonTerminal()
            if not pack:
                break
            nts[pack[0]] = pack[1]

        return nts


