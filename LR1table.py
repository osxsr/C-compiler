from grammer import *
from itertools import groupby
from bnf import *


def CStyleTable(tableName: str, table: dict, isAction: bool) -> str:
    howToMap = [terminal for terminal, _ in groupby(sorted(table.keys(), key=lambda x: x[1]), lambda x: x[1])]
    maxState = max((state for state, _ in table.keys())) + 1

    output = [[-1 for i in range(len(howToMap))] for j in range(maxState)]
    if isAction:
        for (key, value) in table.items():
            if isinstance(value, int):
                output[key[0]][howToMap.index(key[1])] = value
            elif value == 'Accept!':
                output[key[0]][howToMap.index(key[1])] = 0
            else:
                output[key[0]][howToMap.index(key[1])] = value.Index | (1 << 8)
    else:
        for (key, value) in table.items():
            output[key[0]][howToMap.index(key[1])] = value

    for i in range(len(output)):
        output[i] = ''.join('%s, ' % (s) for s in output[i])
        output[i] = '\t{ %s},\n' % output[i]
    output = ''.join(output)

    output = '// {}\nstatic const int {}[{}][{}] = {{\n{}}};'.format(
        'how do terminals map to indices: %s' % ''.join(('%s -> %d; ' % (howToMap[i], i) for i in range(len(howToMap)))),\
        tableName, maxState, len(howToMap), output
    )
    return output

class GetTable():
    def __init__(self, filename) -> None:
        self.nts = ParseBNF(filename).Build()
        self.augmentedSymbol = '<expr\'>'
        init = LRState()
        init += Item('<expr\'>', ['<Program>',], 0, 'eof')
        self.C, self.transition = GetStates(init, self.nts, '<Program>', closureLR1)

    def get_action_table(self) -> dict():    
        actionTable = dict()
        for state in self.C:
            name = state.name
            for item in state:
                if item.name == self.augmentedSymbol and (not item.Where()):  # 
                    actionTable[(name, 'eof')] = 'Accept!'
                else:
                    next2Dot = item.Where()
                    if not next2Dot:
                        actionTable[(name, item.lookahead)] = item # an item to reduce
                    elif next2Dot and next2Dot[0] != '<':
                        to = self.transition[(name, next2Dot)]
                        actionTable[(name, next2Dot)] = to # shift to some state
        return actionTable

    def get_goto_table(self) ->dict():
        gotoTable = dict()
    
        for state in self.C:
            for symbolName in self.nts.GetName():
                key = (state.name, symbolName)
                if key in self.transition.keys():
                    gotoTable[key] = self.transition[key]
        return gotoTable


if __name__ == '__main__':
    gettable =GetTable('./grammar.txt') 

    actionTable = gettable.get_action_table()
    gotoTable = gettable.get_goto_table()

    print('ACTION TABLE:')
    for key, value in actionTable.items():
        print(key, ': ', sep=' ', end = '')
        if isinstance(value, Item):
            print('reduce ' + str(value))
        elif value == 'Accept!':
            print(value)
        else:
            print("shift ", value, sep = ' ')

    print('----------------------------------')
    print('GOTO TABLE')
    for key, value in gotoTable.items():
        print(key, ': ', value, sep=' ')


    # print(CStyleTable('LR1ActionTable', actionTable, True))
    # print(CStyleTable('LR1GotoTable', gotoTable, False))