import re
from bnf import ParseBNF, NonTerminals
from copy import deepcopy
##########################################
# Item: 存放一个带点号的产生式
##########################################
class Item():
    def __init__(self, name, rule, pos, lookahead):
        self._name = name   # name 是产生式的左部
        self._rule = rule   # rule 是产生式的右部
        self._pos = pos     # pos 是点号右边的元素在列表中的索引
        self.__lookahead = lookahead # 向后看一个字符

    # 字符形式输出
    def __str__(self) -> str:
        s = [self._name, ' ::= ']
        for i in range(len(self._rule)):
            if i == self._pos:
                s.append('• ')
            s.extend((self._rule[i], ' '))
        if self._pos == len(self._rule):
            s.append('•')
        s_str = ''.join(s)
        return ''.join([s_str, ', ', str(self.__lookahead)])
    
    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Item):
            return __o._name == self._name and __o._rule == self._rule \
               and __o._pos == self._pos and self.__lookahead == __o.lookahead
        return False

    @property
    def lookahead(self):
        return self.__lookahead

    @property
    def name(self):
        return self._name

    @property
    def Index(self):
        return self._rule.Index

    # 
    def Move(self):
        if self._pos < len(self._rule):
            moved = deepcopy(self)
            moved._pos += 1
            return moved
        return None

    def Where(self):
        if self._pos < len(self._rule):
            return self._rule[self._pos]
        return None
    
    def GetThingsRightofDot(self) -> list:
        return self._rule[self._pos + 1:]


##########################################
# LRstate:
##########################################
class LRState():
    def __init__(self) -> None:
        # 相当于教科书上的 I0、I1 等等等等
        self.__name = 0
        # items 是放 Item0 类的实例的
        self.__items = []

    @property               #xxx.name
    def name(self):
        return self.__name

    # 重写name              xxxx.name=yyy
    @name.setter
    def name(self, value):
        self.__name = value

    # 这样写就可以遍历 self.__items 里的东西了。
    def __iter__(self):
        return (item for item in self.__items)

    #获取第i个item          xxx.item[i]=yyy
    def __getitem__(self, i):
        return self.__items[i]

    # 设置第i个item         xxx.item[i]=yyy
    def __setitem__(self, i, value):
        self.__items[i] = value

    # 获取item个数          len(xxx)
    def __len__(self):
        return len(self.__items)
    
    # 增加  foo+=Item(a,b,c)
    def __iadd__(self, value):
        if value not in self.__items:
            self.__items.append(value)
        return self

    # 返回字符串形式的元素信息
    def __str__(self) -> str:
        s = [str(self.name), ':\n']
        for item in self.__items:
            s.extend(['\t', str(item), '\n'])
        return ''.join(s)
    
    # ==
    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, LRState):
            return False
        return self.__items == __o.__items



##########################################
# First
##########################################
class First():
    def __init__(self) -> None:
        self.length = None
        self.first = dict()
        self.first['eof'] = ['eof']

    # 嵌套的函数——检查字典 d 中集合的长度是否发生变化。
    def changing(self, d: dict) -> bool:
        # 第一次来，直接并初始化+返回1
        if not self.length:
            self.length = dict()
            for k in d.keys():
                self.length[k] = len(d[k])
            return True

        # 以后来，进行扫描
        isChanging = False
        for k in d.keys():
            isChanging |= (self.length[k] != len(d[k]))
            self.length[k] = len(d[k])
        return isChanging

    def Build(self, nts: dict, ts: list) -> None:
        # ts：终结符列表。终结符用 str 表示。
        # nts：非终结符及其对应的若干产生式体。
        # 这个字典的键为 str，表示具体的非终结符。
        # 值为列表的列表，存放对应的产生式体。

        # 初始化
        for (name, rules) in nts:
            self.first[name] = set()
        for terminal in ts:
            self.first[terminal] = {terminal}

        while self.changing(self.first):
            # 这两层 for 循环的作用是遍历所有产生式
            for (name, rules) in nts:
                for rule in rules:
                    if rule != ['""',]:
                        rhs = set(deepcopy(self.first[rule[0]])) # rhs 是“right hand side”的缩写
                        # 尝试删除空串，没有也不会报错
                        rhs.discard('""')
                        # 先拷贝产生式箭头右侧第一个符号的 FIRST 集
                        # 之后遍历产生式右侧的所有符号
                        for i in range(0, len(rule) - 1):
                            if '""' not in self.first[rule[i]]: # 如果某个非终结符可以推出空串就继续循环
                                break
                            rhs |= self.first[rule[i + 1]]
                            rhs.discard('""')
                        else: # 如果上面的 for 循环正常终止就会跳到这里
                            if '""' in self.first[rule[-1]]:
                                rhs.add('""')
                    else:
                        rhs = {'""'}
                    # 最后，把本轮循环求出来的终结符集合和
                    # 产生式头对应的 FIRST 集合合并到一起
                    self.first[name] |= rhs
    
    def find(self, s : list) -> list:
        rhs = deepcopy(self.first[s[0]])
        rhs = set(rhs)
        rhs.discard('""')
        # 扫描后续列表 如果有空串，就继续往后扫 
        # 最后一个元素一定会提前跳出，因为是终结符
        for i in range(len(s)):
            if '""' not in self.first[s[i]]:
                break
            rhs |= self.first[s[i + 1]]
        rhs.discard('""')
        return rhs


def closureLR1(items: LRState, nts: NonTerminals, firstset):
    old = 0

    # closure 还在变
    while len(items) != old:
        old = len(items)

        for item in items:                  # 让 items 变得可以遍历是 __iter__ 的作用
            name = item.Where()             # 点号右边是什么？
            if name and name[0] == '<':     # 点以后的符号是非终结符 
                for rule in nts[name]:      # 遍历这个非终结符对应的所有产生式右部
                    remain = item.GetThingsRightofDot()
                    remain.append(item.lookahead)           # 添加保底
                    firstSetOfRemains = firstset.find(remain)  # (remain, nts)
                    for terminal in firstSetOfRemains:
                        items += Item(name, rule, 0, terminal)


def goto(items: LRState, symbol: str, nts: NonTerminals, findclosure, firstset):
    gotoset = LRState()
    for item in items:
        name = item.Where()
        if name == symbol:
            gotoset += item.Move()
        
    if len(gotoset) != 0:
        findclosure(gotoset, nts, firstset)
        return gotoset
    return None


def GetStates(init: LRState, nts: NonTerminals, startSymbol: str, findclosure):
    firstset = First()
    firstset.Build(nts, nts.GetTermName())
    transition = dict()
    statenumber = 1

    findclosure(init, nts, firstset)
    C = [init,]
    symbols = nts.GetName()
    symbols.extend(nts.GetTermName())

    old = 0
    while len(C) != old:
        old = len(C)

        for i in range(old):
            for symbol in symbols:
                newstate = goto(C[i], symbol, nts, findclosure, firstset)
                if newstate and (newstate not in C):
                    newstate.name = statenumber
                    transition[(C[i].name, symbol)] = statenumber
                    statenumber += 1
                    C.append(newstate)
                elif newstate and newstate in C:
                    index = C.index(newstate)
                    transition[(C[i].name, symbol)] = C[index].name

    stateBeforeAccept = transition[(0, startSymbol)]
    transition[(stateBeforeAccept, 'eof')] = 'Accept!'
    return C, transition


if __name__ == '__main__':
    nts = ParseBNF('./grammar.txt').Build()
    
    print(nts)
    init = LRState()
    # init += Item('<expr\'>', ['<expr>',], 0, 'eof')
    # c, transition = GetStates(init, nts, '<expr>', closureLR1)
    init += Item('<expr\'>', ['<Program>',], 0, 'eof')
    c, transition = GetStates(init, nts, '<Program>', closureLR1)
    
    for state in c:
        print(state)
    for (key, value) in transition.items():
        print(key, ':', value, sep=' ')
