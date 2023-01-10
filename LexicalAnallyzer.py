import re
#from openpyxl import Workbook

class LexicalAnalyer:
    pos = 0
    # 将源文件整体读入字符串
    in_str = ''

	# 符号表(符号-符号类型)
    symbol_table = []

    # 符号类型
    symbol_types = [
			'keyword',
			'operator',
			'delimiter',
			'separator',
			'left_bracket',
			'right_bracket',
			'left_brace',
			'right_brace',
			'float_literal',
			'int_literal',
			'identifier'
    ]

    # 关键字
    _keywords = ['int','long long','short','char','bool',\
                 'float','long double','double',\
                 'void',\
                 'const','extern','static','auto','register',\
                 'if','else if','else',\
                 'switch','case','defult',\
                 'for','while','do',\
                 'break','continue',\
                 'return']
    
    # 运算符
    _operators = ['++','--',
			      '<<=','>>=','<<','>>',
			      '<=','<','>=','>','==','!=',
			      '&&','||','!',
			      '+=','-=','*=','/=','%=','&=','|=','=',
			      '+','-','*','/','%','&','|','~',
			      '?',':']

    # 界符
    _delimiters = [ ';' ]

    # 分隔符
    _separators = [ ',' ]

    # 括号
    _brackets = '(){}'

    # 浮点、整型字面量的正则表达式
    float_pattern = re.compile('(\d+(\.\d*)?|\.\d+)e[+-]?\d+[fFL]?|(\d+\.\d*|\.\d+)[FfL]?')
    int_pattern = re.compile('\d+[Uu]?[Ll]{0,2}')


    # 标识符的正则表达式(模式串)
    identifier_pattern = re.compile('[A-Za-z_]\\w*')

    # 预处理
    def preprocess(self):
        # 删除注释

        del_note = re.compile(r'//.*')
        self.in_str = re.sub(del_note, ' ', self.in_str)
        # self.in_str = del_note.sub(self.in_str,' ')
        del_note = re.compile(r'/\*(.|\r|\n)*?\*/')
        self.in_str = re.sub(del_note, ' ', self.in_str)
	    # 压缩空白字符
        del_space = re.compile(r'\s+')
        self.in_str = re.sub(del_space, ' ', self.in_str)

    # 词法分析
    def analyze(self):
# SCAN:
        while (self.pos < len(self.in_str)):
		    # 忽略空格
            if (self.in_str[self.pos] == ' '):
                self.pos += 1
                continue

            # 依次匹配可能的关键字、运算符、界符、分隔符，匹配到则继续匹配后续字符
            vsp = {'keyword' : self._keywords, 
                'operators' : self._operators, 
                'delimiters' : self._delimiters, 
                'separators' : self._separators}
            flag = 0
            for i in vsp.keys():
                for s in vsp[i]:
                    if (self.in_str[self.pos:self.pos+len(s)] == s):
                        if (i == 'keyword'):
                            end_pos = self.pos + len(s)
                            if end_pos < len(self.in_str) and (self.in_str[end_pos].isalnum() or self.in_str[end_pos] == '_'):
                                continue # 如果匹配到关键字，需要向后展望1个字符，判断其是否实际为标识符
                        if i == 'operators':
                            if s == '>':
                                i = 'gt'
                            elif s == '<':
                                i = 'lt'
                            elif s == '>=':
                                i = 'geq'
                            elif s == '<=':
                                i = 'leq'
                            elif s == '==':
                                i = 'eq'
                            elif s == '!=':
                                i = 'neq'
                            else:
                                i = s
                        if i == 'keyword':
                            i = s
                        self.symbol_table.append((s, i));
                        self.pos += len(s)
                        flag = 1
                        break
                if flag == 1:
                    break

            if flag == 1:
                continue

            # 依次匹配可能的(、)、{、}，匹配到则继续匹配后续字符
            flag = 0
            LEFT_BRACKET = 4
            for i in range(len(self._brackets)):
                if self.in_str[self.pos] == self._brackets[i]:
                    self.symbol_table.append((self._brackets[i], self.symbol_types[LEFT_BRACKET + i]))
                    self.pos+=1
                    flag = 1
                    break
            if flag == 1:
                continue

            # 依次匹配浮点、整型字面量、标识符的正则表达式(模式串)，匹配不到则报错
            flag = 0
            sp = { 'float_literal' : self.float_pattern,
                   'int_literal': self.int_pattern,
                   'identifier' : self.identifier_pattern };
            for i in sp.keys() :
                info = re.match(sp[i], self.in_str[self.pos:])
                if info != None:
                    self.symbol_table.append((self.in_str[self.pos : self.pos+info.end()], i))
                    self.pos += info.end()
                    flag=1
                    break
            
            if flag==1:
                continue
            print("Lexical analyzing error. Stop analyzing.")
            exit(-1)

    # 读文件
    def read_file(self, file_name):
        with open(file=file_name, mode="r",encoding="utf-8") as f:
            self.in_str = f.read()

	# debug 输出
    def display(self):
        print(self.symbol_table)
	
    
    # 到excel
    def to_excel(self, excel_name):
        wb = Workbook()
        sheet = wb.create_sheet('词法分析表', 0)
        sheet.append(['str','symbol'])
        for i in self.symbol_table:
            sheet.append(i)
        wb.save(excel_name)

    def to_string(self):
        lx_str = ""
        for item in self.symbol_table:
            lx_str += item[1]
            lx_str += '\n'
        return lx_str

if __name__ == '__main__':
    le = LexicalAnalyer()
    le.read_file('./test.c')
    le.preprocess()
    le.analyze()
    le.display()
    le.to_excel('result.xlsx')


