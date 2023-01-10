from LR1table import GetTable
from LexicalAnallyzer import LexicalAnalyer
from Parser import Parser


class Intermediate:
    def __init__(self, decl_filename='./decl.txt', emit_filename='./emit.txt'):
        self.declfile = open(decl_filename, 'w', encoding='utf-8')
        self.emitfile = open(emit_filename, 'w', encoding='utf-8')
        self.domain = 0
        self.last_domain = []
        self.nxt_domain = 1
        self.addr = 0
        self.tmp = 0
        self.vars = []
        self.funcs = []
        self.output = []
        self.funcs_startat = []

    def makelist(self, i):
        return i

    def merge(self, p1, p2):  
        if p1 > 0:
            t_p1 = p1
            while self.output[p1][4]:
                p1 = self.output[p1][4]
            self.output[p1][4] = p2
            return t_p1
        return p2
    
    def backpatch(self, p, t):
        if p > 0:
            while self.output[p][4]:
                np = self.output[p][4]
                self.output[p][4] = t
                p = np
            self.output[p][4] = t

    # 从var中寻找id项 = id的
    def find_var(self, id: str):
        for var in self.vars:
            if var['id'] == id and var['domain'] <= self.domain:
                return var
        return False

    # 从funcs中寻找id项 = id的 
    def find_func(self, id: str):
        for func in self.funcs:
            if func['id'] == id:
                return func
        return False

    # 将list 中的四元式输出到文件
    def to_file(self):
        for i in range(len(self.output)):
            # 函数名，不计入四元式 但输出
            for func in self.funcs_startat:
                if func['addr'] == i:
                    print("function: %s" % func['id'], file=self.emitfile)
            # 四元式
            item = self.output[i]
            print("%d, %s, %s, %s, %s" % (item[0], item[1], item[2], item[3], item[4]), file=self.emitfile)

    # 声明/内部变量声明
    def decl_handler(self, tree_node):
        if tree_node['name'] == '<内部变量声明>':
            type = tree_node['children'][-1]['children'][0]['name']
            id = tree_node['children'][-2]['children'][0]['string']
            print("新变量 %s, 作用域 %d, 类型 %s" % (id, self.domain, type) ,file=self.declfile)
            if self.find_var(id) is not False and self.find_var(id)['domain'] == self.domain:
                print("Redefinition of var %s" % (id))
                exit(0)
            self.vars.append({'id': id, 'type': type, 'domain': self.domain})
            assign = len(tree_node['children']) == 4
            if assign:
                rhs = tree_node['children'][0]['val']
                self.output.append([self.addr, '=', rhs, '-', id])
                # print("%d, =, %s, -, %s" % (self.addr, rhs, id), file=self.emitfile)
                self.addr += 1
            return

        type = tree_node['children'][-1]['children'][0]['name']
        id = tree_node['children'][-2]['children'][0]['string']
        assign = len(tree_node['children'][0]['children'][0]['children']) == 3
        is_var = tree_node['children'][0]['children'][0]['name'] == '<变量声明>'
        if self.find_var(id) is not False:
            print("Redefinition of var %s" % (id))
            exit(0)
        if self.find_func(id) is not False:
            print("Redefinition of function %s" % (id))
            exit(0)
        if is_var:
            if assign:
                rhs = tree_node['children'][0]['children'][0]['children'][-2]['val']
                self.output.append([self.addr, '=', rhs, '-', id])
                # print("%d, =, %s, -, %s" % (self.addr, rhs, id), file=self.emitfile)
                self.addr += 1

            print("新变量 %s, 作用域 %d, 类型 %s" % (id, self.domain, type) ,file=self.declfile)
            self.vars.append({'id': id, 'type': type, 'domain': self.domain})
        else:
            if tree_node['children'][0]['children'][0]['children'][-2]['children'][0]['name'] == 'void':
                params_num = 0
                params_type = ['void']
            else:
                params = tree_node['children'][0]['children'][0]['children'][-2]['children'][0]['children'][0]
                params_num = params['number']
                params_type = params['types']
            print("新函数 %s, 作用域 %d, 返回类型 %s, 参数个数 %s" % (id, self.domain, type, params_num) ,file=self.declfile, end=' ')
            print("参数类型:", file=self.declfile, end=' ')
            for i in params_type:
                print(i, end=' ', file=self.declfile)
            print(file=self.declfile)
            self.funcs.append({'id': id, 'type': type, 'domain': self.domain, 'params_num': params_num, 'params_type': params_type})

    # 参数
    def param_handler(self, tree_node):
        if len(tree_node['children']) == 3:
            tree_node['number'] = tree_node['children'][0]['number'] + 1
            tree_node['types'] = tree_node['children'][0]['types']
            tree_node['types'].append(tree_node['children'][-1]['children'][-1]['children'][0]['name'])
            return
        else:
            tree_node['number'] = 1
            tree_node['types'] = []
            type = tree_node['children'][-1]['children'][0]['name']
            id = tree_node['children'][-2]['children'][0]['string']

        tree_node['types'].append(type)

        print("新变量(函数参数) %s, 作用域 %d, 类型 %s" % (id, self.domain, type) ,file=self.declfile)
        self.vars.append({'id': id, 'type': type, 'domain': self.domain})

    # 算术表达式
    def caculate_handler(self, tree_node):
        if len(tree_node['children']) == 2:
            call = tree_node['children'][0]['children'][0]['children'][1]['params']
            id = tree_node['children'][1]['val']
            for i in call[::-1]:
                self.output.append([self.addr, 'param', '-', '-', i])
                self.addr += 1
            tmp = 'tmp' + str(self.tmp)
            tree_node['val'] = tmp
            self.output.append([self.addr, 'call', id, '-', tmp])
            if self.find_func(id) is False:
                print('Unknown function ', id)
                exit(0)
            self.tmp += 1
            self.addr += 1
        elif len(tree_node['children']) == 3:
            if tree_node['children'][0]['name'] == 'right_bracket':
                val = tree_node['children'][-2]
                tree_node['name'] = val['name']
                if 'val' in val.keys():
                    tree_node['val'] = val['val']
                else:
                    tree_node['val'] = val['string']
            else:
                rhs = tree_node['children'][0]['val']
                lhs = tree_node['children'][2]['val']
                r_type = tree_node['children'][0]['name']
                l_type = tree_node['children'][2]['name']
                if r_type == 'identifier' and l_type == 'identifier' \
                    and self.find_var(lhs)['type'] != self.find_var(rhs)['type']:
                    print('Can\'t match type',': [' , lhs, ':', self.find_var(lhs)['type'],'], [',\
                            rhs, ':', self.find_var(rhs)['type'], ']', sep='')
                    exit(0)

                op = tree_node['children'][1]
                if tree_node['children'][1]['name'] == '<比较运算符>' and tree_node['j'] == True:
                    tree_node['truelist'] = self.makelist(self.addr)
                    tree_node['falselist'] = self.makelist(self.addr+1)
                    op = op['children'][0]['string'] 
                    self.output.append([self.addr, 'j'+op, lhs, rhs, 0])
                    self.addr+=1
                    self.output.append([self.addr, 'j', '-', '-', 0])
                    self.addr+=1
                    return
                elif op['name'] == '<比较运算符>':
                    op = op['children'][0]['string']
                else:
                    op = op['name']
                tmp = 'tmp' + str(self.tmp)
                tree_node['val'] = tmp
                self.output.append([self.addr, op, lhs, rhs, tmp])
                self.tmp += 1
                self.addr += 1
        else:
            val = tree_node['children'][-1]
            tree_node['name'] = val['name']
            if 'val' in val.keys():
                tree_node['val'] = val['val']
            else:
                tree_node['val'] = val['string']

    # 赋值语句
    def assign_handler(self, tree_node):
        id = tree_node['children'][-1]['val']
        rhs = tree_node['children'][-3]['val']
        r_type = tree_node['children'][-3]['name']
        op = tree_node['children'][-2]['children'][0]['string']
        if self.find_var(id) is False:
            print('Unknown variable', id)
            exit(0)
        if r_type == 'identifier' and self.find_var(rhs) is False and rhs.find('tmp') == -1:
            print('Unknown variable', rhs)
            exit(0)
        if r_type == 'identifier' and self.find_var(id)['type'] != self.find_var(rhs)['type']:
            print('Can\'t match type',': [' , id, ':', self.find_var(id)['type'],'], [',\
                    rhs, ':', self.find_var(rhs)['type'], ']', sep='')
            exit(0)
        self.output.append([self.addr, op, rhs, '-', id])
        self.addr += 1

    # return
    def return_handler(self, tree_node):
        ret = tree_node['children'][-2]['val']
        self.output.append([self.addr, 'ret', '-', '-', ret])
        # print('%d, ret, -, -, %s' % (self.addr, ret), file=self.emitfile)
        self.addr += 1

    # 实参列表
    def call_param_handler(self, tree_node):
        if len(tree_node['children']) == 3:
            tree_node['params'] = tree_node['children'][0]['params']
        else:
            tree_node['params'] = []
        tree_node['params'].append(tree_node['children'][-1]['val'])

    def if_handler(self, tree_node):
        tree_node['EndAt'] = tree_node['children'][0]['EndAt'] 
        if 'nextlist' not in tree_node['children'][0]:
            tree_node['children'][0]['nextlist'] = 0
        if len(tree_node['children']) == 5: # if then
            self.backpatch(tree_node['children'][-3]['truelist'], tree_node['children'][0]['StartAt'])
            tree_node['nextlist'] = self.merge(tree_node['children'][-3]['falselist'], tree_node['children'][0]['nextlist'])
        else:   
            # print(tree_node['children'][2]['StartAt'],tree_node['children'][0]['StartAt'],file=self.emitfile)                            # if-else
            self.backpatch(tree_node['children'][-3]['truelist'], tree_node['children'][2]['StartAt'])
            self.backpatch(tree_node['children'][-3]['falselist'], tree_node['children'][0]['StartAt'])
            if 'nextlist' not in tree_node['children'][2]:
                tree_node['children'][2]['nextlist'] = 0
            tree_node['nextlist'] = self.merge(tree_node['children'][2]['nextlist'], tree_node['children'][0]['nextlist'])

    def while_handler(self, tree_node):
        tree_node['EndAt'] = self.addr+1 
        if 'nextlist' in tree_node['children'][0]:
            self.backpatch(tree_node['children'][0]['nextlist'], self.addr)
        self.backpatch(tree_node['children'][-3]['truelist'], tree_node['children'][0]['StartAt'])
        self.backpatch(tree_node['children'][-3]['falselist'], self.addr+1)
        self.output.append([self.addr, 'j', '-', '-', tree_node['children'][-3]['StartAt']])
        self.addr+=1


    def intermediate(self, tree_node):
        def intermediate_handler(tree_node):
            '''if tree_node['name'] == 'left_bracket':
                self.domain = self.nxt_domain
            elif tree_node['name'] == 'right_bracket':
                self.domain = 0
            el'''
            if tree_node['name'] == 'left_brace' or tree_node['name'] == 'left_bracket':
                self.last_domain.append(self.domain)
                self.domain = self.nxt_domain
                self.nxt_domain += 1
            elif tree_node['name'] == 'right_brace':
                self.domain = self.last_domain[-1]
                self.last_domain.pop()
            elif tree_node['name'] == '<声明>' and tree_node['children'][0]['children'][0]['name'] != '<变量声明>':
                id = tree_node['children'][-2]['children'][0]['string']
                self.funcs_startat.append({'id':id, 'addr':self.addr})
            elif tree_node['name'] == '<语句块>':
                tree_node['StartAt'] = self.addr
            elif tree_node['name'] == '<if语句>' or tree_node['name'] == '<while语句>':
                tree_node['children'][-3]['StartAt'] = self.addr
                tree_node['children'][-3]['j'] = True

            
            if 'children' in tree_node.keys():
                for i in tree_node['children'][::-1]:
                    intermediate_handler(i)
            if tree_node['name'] == '<声明>' or tree_node['name'] == '<内部变量声明>':
                self.decl_handler(tree_node)
            elif tree_node['name'] == '<参数>':
                self.param_handler(tree_node)
            elif tree_node['name'] == '<加法表达式>' or tree_node['name'] == '<项>' or tree_node['name'] == '<因子>' or tree_node['name'] == '<ID>' or tree_node['name'] == '<表达式>':
                self.caculate_handler(tree_node)
            elif tree_node['name'] == '<赋值语句>':
                self.assign_handler(tree_node)
            elif tree_node['name'] == '<return语句>':
                self.return_handler(tree_node)
            elif tree_node['name'] == '<实参列表>':
                self.call_param_handler(tree_node)
            elif tree_node['name'] == '<语句块>':
                tree_node['EndAt'] = self.addr
                if 'nextlist' in tree_node['children'][1]:  #同样是传递
                    tree_node['nextlist'] = tree_node['children'][1]['nextlist']
            elif tree_node['name'] == '<语句>':
                if 'nextlist' in tree_node['children'][-1]: # 一次传递，无意义
                    tree_node['nextlist'] = tree_node['children'][-1]['nextlist']
                if 'EndAt' in tree_node['children'][-1]: # 一次传递，无意义
                    tree_node['EndAt'] = tree_node['children'][-1]['EndAt']
            elif tree_node['name'] == '<语句串>' and 'nextlist' in tree_node['children'][-1]: # 回填上方的语句
                if len(tree_node['children']) > 1:
                    self.backpatch(tree_node['children'][-1]['nextlist'], tree_node['children'][-1]['EndAt'])
                if 'nextlist' in tree_node['children'][0]:
                    tree_node['nextlist'] = tree_node['children'][0]['nextlist']
            elif tree_node['name'] == '<if语句>':
                self.if_handler(tree_node)
            elif tree_node['name'] == '<while语句>':
                self.while_handler(tree_node)
        intermediate_handler(tree_node)
        self.to_file()

if __name__ == '__main__':
    # 语法分析初始化，获得两表
    gettable = GetTable('./grammar.txt') 
    actionTable = gettable.get_action_table()
    gotoTable = gettable.get_goto_table()

    # 词法分析初始化，获得inp tokens表
    le = LexicalAnalyer()
    le.read_file('./test1.c')
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
    # parser.print_parse_tree()

    intermediate = Intermediate()
    intermediate.intermediate(parser.tree[parser.root])