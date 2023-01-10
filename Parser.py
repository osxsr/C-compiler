from LR1table import *
from LexicalAnallyzer import *

class Parser:
    def __init__(self, goto: dict, action: dict, filename = './parse.txt'):
        self.goto = goto
        self.action = action
        self.filename = filename

    def parse(self, inp: list):
        pointer = 0
        self.tree = []
        self.root = -1
        cnt = -1
        node = []
        status = [0]
        stack = ['eof']
        node_stack = ['eof']

        while True:
            if pointer >= len(inp):
                c = 'eof'
            else:
                c = inp[pointer][1]
            stack.append(c)
            self.tree.append({'name': c, 'string': 'eof' if pointer >= len(inp) else inp[pointer][0]})
            cnt += 1
            node_stack.append(cnt)
            print(stack, status)
            try:
                value = self.action[status[-1], c]
                if isinstance(value, Item):
                    print('reduce ' + str(value))
                    self.tree.append({'name': value.name, 'children': [], 'string': 'eof' if pointer >= len(inp) else inp[pointer][0]})
                    cnt += 1
                    stack.pop()
                    node_stack.pop()
                    for i in range(len(value._rule)):
                        stack.pop()
                        status.pop()
                        self.tree[cnt]['children'].append(self.tree[node_stack.pop()])
                    stack.append(value.name)
                    status.append(self.goto[status[-1], value.name])
                    node_stack.append(cnt)
                    if value.name == '<Program>':
                        self.root = cnt
                elif value == 'Accept!':
                    print(value)
                    return
                else:
                    print('shift to status ' + str(value))
                    status.append(value)
                    pointer += 1
            except Exception as e:
                raise e

    def print_parse_tree(self, filename="./parse_tree.txt"):
        pre = [' ' for i in range(1000)]
        ffile = open(filename, 'w', encoding='utf-8')
        def print_node(node, space, line, sib: bool, start: bool):
            if start:
                if sib:
                    print("─┬─", end='', file=ffile)
                    line[space+1]='|'
                else:
                    print("───", end='', file=ffile)
            else:
                for i in range(space):
                    print(pre[i], end='', file=ffile)
                if sib:
                    print(" ├─", end='', file=ffile)
                    line[space+1]='|'
                else:
                    print(" └─", end='', file=ffile)
                    line[space+1]=' '
            space += int(3 + (len(node['name'].encode('utf-8')) - len(node['name'])) / 2 + len(node['name']))
            print(node['name'], end='', file=ffile)
            if 'children' not in node.keys():
                print('\n', end='', file=ffile)
                return
            i = len(node['children']) - 1
            if i > 0:
                print_node(node['children'][i], space, line, 1, 1)
                i -= 1
            else:
                print_node(node['children'][i], space, line, 0, 1)
                i -= 1
                return
            while i > 0:
                print_node(node['children'][i], space, line, 1, 0)
                i -= 1
            print_node(node['children'][0], space, line, 0, 0)

        print("<Program>", end='', file=ffile)
        i = len(self.tree[self.root]['children']) - 1
        if i > 0:
            print_node(self.tree[self.root]['children'][i], 9, pre, 1, 1)
            i -= 1
        else:
            print_node(self.tree[self.root]['children'][i], 9, pre, 0, 1)   
            i -= 1
        while i != 0:
            print_node(self.tree[self.root]['children'][i], 9, pre, 1, 0)
            i -= 1
        if i >= 0:
            print_node(self.tree[self.root]['children'][i], 9, pre, 0, 0)
        
        ffile.close()

if __name__ == '__main__':
    # 语法分析初始化，获得两表
    gettable =GetTable('./grammar.txt') 
    actionTable = gettable.get_action_table()
    gotoTable = gettable.get_goto_table()

    # 词法分析初始化，获得inp tokens表
    le = LexicalAnalyer()
    le.read_file('./test.c')
    le.preprocess()
    le.analyze()

    inp = le.symbol_table

    '''
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
    '''
    parser = Parser(gotoTable, actionTable)
    parser.parse(inp)
    parser.print_parse_tree()

'''
statusStack = [0]  # 状态栈
charStack = ['eof']  # 输入栈
pointer = 0
tree = []
for i in range(len(actionTable)):
    tree.append({})

root = -1
cntNode = -1
nodeStack = []  # 语法树结点 nodeStack[cntNode]["name"]="123" nodeStack[cntNode]["children"]=[1, 2, 3]
'''
'''
while True:
    c = inp[pointer]
    try:
        num = goto[statusStack[-1]][c]
        if num == 0:
            print("accepted.")
            tree[statusStack[-1]]["name"] = charStack[-1]
            root = statusStack[-1]
            break
        elif num > 0:  # 移进
            statusStack.append(num)
            # print(num, c)
            tree.append({})
            cntNode += 1
            tree[cntNode]["name"] = c
            nodeStack.append(cntNode)
            charStack.append(c)
            pointer += 1

            if c in ["identifier", "number"]:
                tree[cntNode]["children"] = [cntNode + 1]
                tree.append({})
                cntNode += 1
                nam = names.pop()
                tree[cntNode]["name"] = nam

        elif num < 0:
            item = 产生式[-num]  # 用 item 归约
            order = item["order"]
            attr = {}

            if item["right"] == []:  # 空
                charStack += [item["left"]]
                statusStack.append(goto[statusStack[-1]][item["left"]])

                tree.append({})
                cntNode += 1
                tree[cntNode]["children"] = [cntNode + 1]
                tree[cntNode]["name"] = item["left"]
                nodeStack.append(cntNode)

                tree.append({})
                cntNode += 1
                tree[cntNode]["children"] = []
                tree[cntNode]["name"] = ''

            else:
                k = len(item["right"])
                statusStack = statusStack[:-k]
                charStack = charStack[:-k] + [item["left"]]
                statusStack.append(goto[statusStack[-1]][item["left"]])
                tree.append({})
                cntNode += 1
                tree[cntNode]["children"] = []

                for i in range(k):
                    nowNode = nodeStack.pop()
                    tree[cntNode]["children"].append(nowNode)

                tree[cntNode]["children"] = tree[cntNode]["children"][::-1]
                tree[cntNode]["name"] = item["left"]
                nodeStack.append(cntNode)
    except Exception as e:
        raise e

def outp(now, blank: int):
    if not tree[now]:
        return
    print(tree[now]["name"] + '\n')

    if ("children" not in tree[now]) or (not tree[now]["children"]):
        return
    cnt = 0
    for child in tree[now]["children"]:
        if cnt == len(tree[now]["children"]) - 1:
            print(' ' * blank + "`-")
            outp(child, blank + 2)
        else:
            print(' ' * blank + "|-")
            outp(child, blank + 2)
    return

outp(cntNode, 0)
'''