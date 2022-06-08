import sys
from glob import glob
import lark
global Dict
global strCpt 
strCpt = -16
Dict = {}
grammaire = lark.Lark("""
variables : typed_variable (","  typed_variable)*
expr :  IDENTIFIANT -> variable | NUMBER -> nombre | "'" STR "'"-> str | "malloc" "(" expr ")" -> malloc | expr ".cAt" "(" expr ")" -> cat 
| expr OP expr -> binexpr | "(" expr ")" -> parenexpr | POINTER expr -> valeur | "&" IDENTIFIANT -> adresse | "len(" expr ")" -> len 

cmd : IDENTIFIANT "=" expr ";"-> assignment | POINTER IDENTIFIANT "=" expr ";"-> assignment1 |"while" "(" expr ")" "{" bloc "}" -> while
    | "if" "(" expr ")" "{" bloc "}" -> if | "printf" "(" expr ")" ";"-> printf | typed_variable ";" -> variable | IDENTIFIANT ".setcAt(" expr "," expr ")"";" -> setcat
POINTER : /[*]+/
bloc : (cmd)*
prog : BASIC_TYPE "main" "(" variables ")" "{" bloc "return" "(" expr ")" ";" "}"
typed_variable : BASIC_TYPE  IDENTIFIANT
BASIC_TYPE : /(int|str)[*]*/
STR : /[a-zA-Z0-9]+/
NUMBER : /[0-9]+/
OP : /([+\*-]|==|!=|>=|<=|>|<)/
IDENTIFIANT : /[a-zA-Z][a-zA-Z0-9]*/
%import common.WS
%ignore WS
""", start = "prog")
cpt=iter(range(100000))
op2asm={"+":"add rax,rbx","-":"sub rax,rbx","*":"imul rax,rbx",">":"cmp rax,rbx\njg ","<":"cmp rax,rbx\njl ","==":"cmp rax,rbx\nje ","!=":"cmp rax,rbx\njne ",">=":"cmp rax,rbx\njge ","<=":"cmp rax,rbx\njle "}

def pp_variables(vars):
    return ", ".join([f"{t.children[0]} {t.children[1]}" for t in vars.children])


def pp_expr(expr):
    if expr.data in {"variable", "nombre"}:
        return expr.children[0].value
    if expr.data =="str":
        return f"'{expr.children[0].value}'"
    elif expr.data == "valeur":
        e1 = pp_expr(expr.children[0])
        return f" *{e1}"
    elif expr.data == "adresse":
        return f" &{expr.children[0].value}"
    elif expr.data == "malloc":
        e1 = pp_expr(expr.children[0])
        return f" malloc({e1})"
    elif expr.data == "cat":
        e1 = pp_expr(expr.children[1])
        return f" {expr.children[0]}.cAt({e1})"
    elif expr.data == "len":
        e1 = pp_expr(expr.children[0])
        return f"len({e1})"
    elif expr.data == "setcat":
        e1 = pp_expr(expr.children[1])
        e2 = pp_expr(expr.children[2])
        return f"{expr.children[0]}.cAt({e1},{e2})"
    elif expr.data == "binexpr":
        e1 = pp_expr(expr.children[0])
        e2 = pp_expr(expr.children[2])
        op = expr.children[1].value
        return f" {e1} {op} {e2}"
    elif expr.data == "parenexpr":
        return f"({pp_expr(expr.children[0])})"
    else:
        raise Exception("Not implemented")


def pp_cmd(cmd):
    if cmd.data=="assignment":
        lhs = cmd.children[0]
        rhs = pp_expr(cmd.children[1])
        return f" {lhs} = {rhs};\n"
    elif cmd.data=="assignment1":
        lhs=cmd.children[0]+cmd.children[1]
        rhs=pp_expr(cmd.children[2])
        return f" {lhs} = {rhs};\n"
    elif cmd.data == "printf":
        return f" printf( {pp_expr(cmd.children[0])} );\n"
    elif cmd.data in {"while", "if"}:
        e = pp_expr(cmd.children[0])
        b = pp_bloc(cmd.children[1])
        return f" {cmd.data} ({e}) {{ {b}}}"
    elif cmd.data == "variable":
        return f" {cmd.children[0].children[0]} {cmd.children[0].children[1]};"
    else:
        raise Exception("Not implemented")


def pp_bloc(bloc):
    return "\n".join([pp_cmd(t) for t in bloc.children])


def pp_prg(prog):
    type_fct=prog.children[0]
    vars = pp_variables(prog.children[1])
    bloc = pp_bloc(prog.children[2])
    ret = pp_expr(prog.children[3])
    return f"{type_fct} main ({vars}){{\n{bloc} return ({ret});\n}}"

def var_list(ast):
    if isinstance(ast, lark.Token):
        if ast.type == "IDENTIFIANT":
            return {ast.value}
        else:
            return set()
    s = set()
    for c in ast.children:
        s.update(var_list(c))
    return s

def compile(prg):
    with open("moule.asm") as f:
        code=f.read()
        var_decl="\n".join([f"{x} : dq 0" for x in var_list(prg)])
        code=code.replace("VAR_DECL",var_decl)
        code = code.replace("VAR_INIT",compile_vars(prg.children[1]))
        code=code.replace("BODY",compile_bloc(prg.children[2]))
        code = code.replace("VAR_INIT",compile_vars(prg.children[1]))
        code=code.replace("RETURN",compile_expr(prg.children[3])[1])
        type_ret = "fmt"
        if(compile_expr(prg.children[3])[0] =="str"):
            type_ret += "1"
        code = code.replace("TYPE_RET",type_ret)
        if symb_type(compile_expr(prg.children[3])[0])!=symb_type(prg.children[0]):
            raise Exception("Return type main mismatch")     
        return code

def compile_expr(expr):
    global Dict
    global strCpt
    if expr.data == "variable":
        if expr.children[0].value not in Dict.keys():
            raise Exception(f"Variable {expr.children[0].value} not declared")
        return [Dict[expr.children[0].value]["type"], f"mov rax, [{expr.children[0].value}]"]
    elif expr.data == "nombre":
        return ["int", f"mov rax, {expr.children[0].value}"]

    elif expr.data == "valeur":
        if expr.children[1].children[0].value not in Dict.keys():
            raise Exception(f"Variable {expr.children[1].children[0].value} not declared")
        rtn = f"mov rdx, [{expr.children[1].children[0].value}]\n"
        nb = str(expr.children[0].value).count("*")
        for i in range(nb-1):
            rtn += f"mov rbx, [rbx]\n"
        rtn += "mov rax, [rbx]"
        j=0
        type_calcul=Dict[expr.children[1].children[0].value]["type"]
        while "*" in type_calcul and j<nb:
            type_calcul=type_calcul[:-1]
            j+=1
        if type_calcul=="str" and j<nb:
            raise Exception(f"str type not supported as a pointer")
        return [type_calcul,rtn]


    elif expr.data == "adresse":
        return ["int", f"lea rax, [{expr.children[0].value}]"]

    elif expr.data == "binexpr":
        [type_e1,e1] = compile_expr(expr.children[0])
        [type_e2,e2] = compile_expr(expr.children[2])
        op = expr.children[1].value
        if symb_type(type_e1)!=symb_type(type_e2):
            raise Exception("Incompatible types")  
        if type_e1=="int":
            if op in "+-*/":
                return [type_e1,f"{e2}\npush rax\n{e1}\npop rbx\n{op2asm[op]}"]
            elif op in {"<",">","<=",">=","==","!="}:
                index=next(cpt)
                return [type_e1,f"{e2}\npush rax\n{e1}\npop rbx\n{op2asm[op]}"+f"conditionv{index}\nmov rax,0\njmp fincond{index}\nconditionv{index} :mov rax,1\nfincond{index} : cmp rax,rax"]
        elif type_e1=="str":

            if op == "+":
                index = next(cpt)
                index = next(cpt)
                index = next(cpt)
                index = next(cpt)
                return [type_e1,f"{e1}\n mov rbx ,0\ndebut{index-1}:\n cmp byte [rax+rbx],0\n je fin{index-1}\n inc rbx\n jmp debut{index-1}\n fin{index-1}:\n mov rax,rbx\npush rax\n{e2}\n mov rbx ,0\ndebut{index}:\n cmp byte [rax+rbx],0\n je fin{index}\n inc rbx\n jmp debut{index}\n fin{index}:\n mov rax,rbx\npop rbx\nadd rax,rbx\ninc rax\nmov rdi,rax\ncall malloc\nmov rdx,rax\n push rax\n\
                {e1}\n mov rbx ,0\ndebut{index-2}:\n cmp byte [rax+rbx],0\n je fin{index-2}\nmov rcx,[rax+rbx]\nmov [rdx+rbx],rcx \ninc rbx\n jmp debut{index-2}\n fin{index-2}:\nadd rdx,rbx\
                    \n{e2}\n mov rbx ,0\ndebut{index-3}:\n cmp byte [rax+rbx],0\n je fin{index-3}\nmov rcx,[rax+rbx]\nmov [rbx+rdx],rcx \ninc rbx\n jmp debut{index-3}\n fin{index-3}:\nmov rcx,[rax+rbx+1]\nmov [rdx + rbx+1],rcx\npop rax\n"]
            elif op == "==":
                index = next(cpt)
                index = next(cpt)
                index = next(cpt)
                return ["int",f"{e1}\nmov rbx, rax\n{e2}\nmov rcx, 0\ndebut{index}:\nmov rdx, [rax+rcx]\ncmp [rbx+rcx], rdx\njne fin{index-1}\ncmp byte [rbx+rcx],0\nje fin{index}\ninc rcx\njmp debut{index}\nfin{index}:\nmov rax, 1\njmp fin{index-2}\nfin{index-1}:\nmov rax, 0\nfin{index-2}:\n"]
            else:
                raise Exception("Invalid operator (only + and == for type str)")

    elif expr.data == "cat":
        [type_e1,e1] = compile_expr(expr.children[0])
        [type_e2,e2] = compile_expr(expr.children[1])
        if symb_type(type_e1) != "str":
            raise Exception(f".cAt() take only str as argument, not {type_e1}")
        if symb_type(type_e2) != "int":
            raise Exception(f".cAt() take only int as argument, not {type_e2}")
        return ["int",f"{e2}\nmov rbx,rax\n{e1}\nadd rbx,rax\n movzx eax, BYTE [rbx]\n movsx eax, al\nmov DWORD [_A], eax\nmov rax, [_A]"]


    elif expr.data == "parenexpr":
        return compile_expr(expr.children[0])
    
    elif expr.data == "malloc":
        [type_e1,e1] = compile_expr(expr.children[0])
        if symb_type(type_e1)!="int":
            raise Exception(f"malloc() take only int as argument, not {type_e1}")
        return ["int",f"{e1}\nmov rdi, rax\ncall malloc\n"]


    elif expr.data == "str":
        s = f"mov rdi, {len(expr.children[0].value)+1}\ncall malloc\n"
        for i in range(len(expr.children[0].value)):
            s += f"mov byte [rax +{i}], {ord(expr.children[0].value[i])} \n"
        s += f"mov byte [rax + {len(expr.children[0].value)} ], 0\n"
        return ["str",s]

    elif expr.data == "len":
        [type_e1,e1] = compile_expr(expr.children[0])
        if type_e1 != "str":
            raise Exception(f"len() takes only str as argument, not{type_e1}")
        index = next(cpt)
        return ["int",f"{e1}\n mov rbx ,0\ndebut{index}:\n cmp byte [rax+rbx],0\n je fin{index}\n inc rbx\n jmp debut{index}\n fin{index}:\n mov rax,rbx\n"]
    
    else:
        raise Exception("Not implemented")

def compile_vars(ast):
    s=""
    for i in range(len(ast.children)):
        Dict[ast.children[i].children[1].value] = {"type":ast.children[i].children[0].value}
        s +=f"mov rbx, [rbp-0x10]\nmov rdi,[rbx+{8*(i+1)}]\ncall atoi\nmov [{ast.children[i].children[1]}], rax\n"
    return s

def compile_cmd(cmd):
    global Dict
    global strCpt
    if cmd.data == "assignment":
        lhs = cmd.children[0].value
        type_lhs=Dict[cmd.children[0].value]["type"]
        [type_rhs,rhs] = compile_expr(cmd.children[1])
        if symb_type(type_lhs)!=symb_type(type_rhs):
            raise Exception(f"Incompatible types in assignment, {type_lhs} and {type_rhs} are not assignable")
        return f"{rhs}\nmov [{lhs}],rax"
      
    if cmd.data == "assignment1":
        lhs = cmd.children[1].value
        type_lhs=Dict[cmd.children[1]]["type"]
        [type_rhs,rhs] = compile_expr(cmd.children[2])
        rtn = f"{rhs}\nmov rbx, [{lhs}]\n"
        nb = str(cmd.children[0].value).count("*")
        if symb_type(type_lhs)!=symb_type(type_rhs):
            raise Exception(f"Incompatible types in assignment, {type_lhs} and {type_rhs} are not assignable")
        for i in range(nb-1):
            rtn += f"mov rbx, [rbx]\n"
        rtn += f"mov [rbx], rax\n"
        return rtn

    elif cmd.data == "printf":
        if symb_type(compile_expr(cmd.children[0])[0]) == "int":
            return f"{compile_expr(cmd.children[0])[1]}\nmov rdi, fmt\nmov rsi,rax\nxor rax,rax\ncall printf"
        elif symb_type(compile_expr(cmd.children[0])[0]) == "str":
            return f"{compile_expr(cmd.children[0])[1]}\nmov rdi, fmt1\nmov rsi,rax\nxor rax,rax\ncall printf"

    elif cmd.data == "while":
        [type_e1,e1] = compile_expr(cmd.children[0])
        e2 = compile_bloc(cmd.children[1])
        index=next(cpt)
        return f"debut{index}:{e1}\ncmp rax,0\njz fin{index}\n{e2}\njmp debut{index}\nfin{index}:\n"
    elif cmd.data == "variable":
        if cmd.children[0].children[1].value in Dict.keys():
            raise Exception(f"Variable {cmd.children[0].children[1].value} already declared")
        Dict[cmd.children[0].children[1].value]={"type":cmd.children[0].children[0].value}
        return ""

    elif cmd.data == "setcat":
        [type_e1,e1] = compile_expr(cmd.children[1])
        [type_e2,e2] = compile_expr(cmd.children[2])
        if symb_type(type_e2) != "int" or symb_type(type_e1) != "int":
            raise Exception("Incompatible types, needs int")
        return f"{e1}\nmov rbx,rax\nmov rax, [{cmd.children[0]}]\n add rbx,rax\n {e2}\n mov [rbx], al\n"
        

    else:
        raise Exception("Not implemented")

def compile_bloc(bloc):
    return "\n".join([compile_cmd(t) for t in bloc.children])

def symb_type(type_):
    if type_ == "int" or "*" in type_:
        return "int"
    elif type_ == "str":
        return "str"
    else:
        raise Exception(f"Type {type_} not implemented")


fichier_source=sys.argv[2]
mod=sys.argv[1]
filin = open(fichier_source, "r")
lignes = filin.readlines()
filin.close()
code=""
for ligne in lignes:
    code += ligne
prg = grammaire.parse(code)

if mod == "cp":
    print(compile(prg))
elif mod ==  "pp":
    print(pp_prg(prg))

