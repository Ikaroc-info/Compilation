from glob import glob
import lark
global Dict
global strCpt 
strCpt = -16
Dict = {}
grammaire = lark.Lark("""
variables : typed_variable (","  typed_variable)*
expr :  IDENTIFIANT -> variable | NUMBER -> nombre | "'" STR "'"-> str | "malloc" "(" expr ")" -> malloc | IDENTIFIANT ".cAt" "(" expr ")" -> cat 
| expr OP expr -> binexpr | "(" expr ")" -> parenexpr | POINTER expr -> valeur | "&" IDENTIFIANT -> adresse | "len(" expr ")" -> len

cmd : IDENTIFIANT "=" expr ";"-> assignment | POINTER IDENTIFIANT "=" expr ";"-> assignment1 |"while" "(" expr ")" "{" bloc "}" -> while
    | "if" "(" expr ")" "{" bloc "}" -> if | "printf" "(" expr ")" ";"-> printf | typed_variable ";" -> variable
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
        return f"*{e1}"
    elif expr.data == "adresse":
        return f"&{expr.children[0].value}"
    elif expr.data == "malloc":
        e1 = pp_expr(expr.children[0])
        return f"malloc({e1})"
    elif expr.data == "cat":
        e1 = pp_expr(expr.children[1])
        return f"{expr.children[0]}.cAt({e1})"
    elif expr.data == "len":
        e1 = pp_expr(expr.children[0])
        return f"len({e1})"
    elif expr.data == "binexpr":
        e1 = pp_expr(expr.children[0])
        e2 = pp_expr(expr.children[2])
        op = expr.children[1].value
        return f"{e1} {op} {e2}"
    elif expr.data == "parenexpr":
        return f"({pp_expr(expr.children[0])})"
    else:
        raise Exception("Not implemented")


def pp_cmd(cmd):
    if cmd.data=="assignment":
        lhs = cmd.children[0]
        rhs = pp_expr(cmd.children[1])
        return f"{lhs} = {rhs};\n"
    elif cmd.data=="assignment1":
        lhs=cmd.children[0]+cmd.children[1]
        rhs=pp_expr(cmd.children[2])
        return f"{lhs} = {rhs};\n"
    elif cmd.data == "printf":
        return f"printf( {pp_expr(cmd.children[0])} );\n"
    elif cmd.data in {"while", "if"}:
        e = pp_expr(cmd.children[0])
        b = pp_bloc(cmd.children[1])
        return f"{cmd.data} ({e}) {{ {b}}}"
    elif cmd.data == "variable":
        return f"{cmd.children[0].children[0]} {cmd.children[0].children[1]};"
    else:
        raise Exception("Not implemented")


def pp_bloc(bloc):
    return "\n".join([pp_cmd(t) for t in bloc.children])


def pp_prg(prog):
    type_fct=prog.children[0]
    vars = pp_variables(prog.children[1])
    bloc = pp_bloc(prog.children[2])
    ret = pp_expr(prog.children[3])
    return f"{type_fct} main ({vars}){{\n {bloc} return ({ret});\n}}"

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
        rtn = f"mov rbx, [{expr.children[1].children[0].value}]\n"
        nb = str(expr.children[0].value).count("*")
        for i in range(nb-1):
            rtn += f"mov rbx, [rbx]\n"
        rtn += "mov rax, [rbx]"
        return [Dict[expr.children[1].children[0].value]["type"],rtn]

    elif expr.data == "adresse":
        return ["int", f"lea rax, [{expr.children[0].value}]"]

    elif expr.data == "binexpr":
        [type_e1,e1] = compile_expr(expr.children[0])
        [type_e2,e2] = compile_expr(expr.children[2])
        op = expr.children[1].value
        if symb_type(type_e1)!=symb_type(type_e2):
            raise Exception("Incompatible types")
        if op in "+-*/":
            return [type_e1,f"{e2}\npush rax\n{e1}\npop rbx\n{op2asm[op]}"]
        elif op in {"<",">","<=",">=","==","!="}:
            index=next(cpt)
            return [type_e1,f"{e2}\npush rax\n{e1}\npop rbx\n{op2asm[op]}"+f"conditionv{index}\nmov rax,0\njmp fincond{index}\nconditionv{index} :mov rax,1\nfincond{index} : cmp rax,rax"]

    elif expr.data == "cat":
        [type_e2,e2] = compile_expr(expr.children[1])
        if type_e2 != "int":
            raise Exception("Incompatible types")
            
        a=Dict[expr.children[0].value]["pos"]
        return ["int",f"{e2}\nmov rbx,{a}\n sub rbx,rax\nmov rcx,rbp\n add rcx , rbx\n movzx eax, BYTE [rcx]\n movsx eax, al\nmov DWORD [B], eax\nmov rax, [B]"]

    elif expr.data == "parenexpr":
        return compile_expr(expr.children[0])
    
    elif expr.data == "malloc":
        [type_e1,e1] = compile_expr(expr.children[0])
        if type_e1!="int":
            raise Exception("Incompatible type, needs int")
        return ["int",f"{e1}\nmov rdi, rax\ncall malloc\n"]


    elif expr.data == "str":
        strCpt -= 1
        posStr = strCpt
        s = ""
        for i in range(len(expr.children[0].value)):
            s += "mov byte [rbp "+str(strCpt)+"], "+ str(ord(expr.children[0].value[i])) +"\n"
            strCpt -= 1
        return ["str",{"type":"str","len":len(expr.children[0].value), "pos":posStr},s]
    
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
    if cmd.data == "assignment" and symb_type(Dict[cmd.children[0].value]["type"])=="int":
        lhs = cmd.children[0].value
        type_lhs=Dict[cmd.children[0].value]["type"]
        [type_rhs,rhs] = compile_expr(cmd.children[1])
        if type_rhs != "int" and "*" not in type_rhs:
            raise Exception("Type mismatch")
        return f"{rhs}\nmov [{lhs}],rax"

    elif cmd.data == "assignment" and Dict[cmd.children[0].value]["type"]=="str":
        lhs = cmd.children[0].value
        [type_rhs,rhs,rtn] = compile_expr(cmd.children[1])
        if "str" != type_rhs:
            raise Exception("Type mismatch")
        Dict[cmd.children[0].value] = rhs
        return rtn
      
    if cmd.data == "assignment1":
        lhs = cmd.children[1].value
        [type_rhs,rhs] = compile_expr(cmd.children[2])
        rtn = f"{rhs}\nmov rbx, [{lhs}]\n"
        nb = str(cmd.children[0].value).count("*")
        for i in range(nb-1):
            rtn += f"mov rbx, [rbx]\n"
        rtn += f"mov [rbx], rax\n"
        return rtn

    elif cmd.data == "printf":
        return f"{compile_expr(cmd.children[0])[1]}\nmov rdi, fmt\nmov rsi,rax\nxor rax,rax\ncall printf"

    elif cmd.data == "while":
        e = compile_expr(cmd.children[0])
        b = compile_bloc(cmd.children[1])
        index=next(cpt)
        return f"debut{index}:{e}\ncmp rax,0\njz fin{index}\n{b}\njmp debut{index}\nfin{index}:\n"
    elif cmd.data == "variable":
        if cmd.children[0].children[1].value in Dict.keys():
            raise Exception(f"Variable {cmd.children[0].children[1].value} already declared")
        Dict[cmd.children[0].children[1].value]={"type":cmd.children[0].children[0].value}
        return ""

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
        raise Exception("Not implemented")

prg = grammaire.parse("""int main(int X) {
    int A;
    int B;
    B=3;
    printf(1==1);
    printf(0==1);
    printf(2>=1);
    printf(0>=1);
    printf(3<4);
    printf(0>1);
return(A); }""")

#print(prg)
#prg2 = pp_prg(prg)
#print(prg2)
print(compile(prg))
