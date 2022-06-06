import lark
global Dict
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
OP : /[+\*>-]/
IDENTIFIANT : /[a-zA-Z][a-zA-Z0-9]*/
%import common.WS
%ignore WS
""", start = "prog")
cpt=iter(range(10000))
op2asm={"+":"add rax,rbx","-":"sub rax,rbx"}

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
        code=code.replace("BODY",compile_bloc(prg.children[2]))
        code = code.replace("VAR_INIT",compile_vars(prg.children[1]))
        code=code.replace("RETURN",compile_expr(prg.children[3])[1])
        if compile_expr(prg.children[3])[0]!=prg.children[0]:
            raise Exception("Return type main mismatch")     
        return code

def compile_expr(expr):
    if expr.data == "variable":
        if expr.children[0].value not in Dict.keys():
            raise Exception(f"Variable {expr.children[0].value} not declared")
        return [Dict[expr.children[0].value], f"mov rax, [{expr.children[0].value}]"]
    elif expr.data == "nombre":
        return ["int", f"mov rax, {expr.children[0].value}"]
    elif expr.data == "binexpr":
        [type_e1,e1] = compile_expr(expr.children[0])
        [type_e2,e2] = compile_expr(expr.children[2])
        op = expr.children[1].value
        if type_e1!=type_e2:
            raise Exception("Incompatible types")
        return [type_e1,f"{e2}\npush rax\n{e1}\npop rbx\n{op2asm[op]}"]


    elif expr.data == "parenexpr":
        return compile_expr(expr.children[0])
    
    elif expr.data == "malloc":
        [type_e1,e1] = compile_expr(expr.children[0])
        return [type_e1,f"{e1}\nmov rdi, rax\ncall malloc\n"]


    else:
        raise Exception("Not implemented")

def compile_vars(ast):
    print(ast.children[0].children[1])
    s=""
    for i in range(len(ast.children)):
        s +=f"mov rbx, [rbp-0x10]\nmov rdi,[rbx+{8*(i+1)}]\ncall atoi\nmov [{ast.children[i].children[1]}], rax\n"
    return s

def compile_cmd(cmd):
    global Dict
    if cmd.data == "assignment":
        lhs = cmd.children[0].value
        type_lhs=Dict[cmd.children[0].value]
        [type_rhs,rhs] = compile_expr(cmd.children[1])
        if type_lhs != type_rhs:
            raise Exception("Type mismatch")
        return f"{rhs}\nmov [{lhs}],rax"
    if cmd.data == "assignment1":
        lhs = cmd.children[0].value
        rhs = compile_expr(cmd.children[1])
        return f"{rhs}\nmov [{lhs}],rax"
    elif cmd.data == "printf":
        return f"printf( {pp_expr(cmd.children[0])} );"
    elif cmd.data == "while":
        e = compile_expr(cmd.children[0])
        b = compile_bloc(cmd.children[1])
        index=next(cpt)
        return f"debut{index}:{e}\ncmp rax,0\njz fin{index}\n{b}\njmp debut{index}\nfin{index}:\n"
    elif cmd.data == "variable":
        if cmd.children[0].children[1].value in Dict.keys():
            raise Exception(f"Variable {cmd.children[0].children[1].value} already declared")
        Dict[cmd.children[0].children[1].value]=cmd.children[0].children[0].value
        print(Dict)
        return ""

    else:
        raise Exception("Not implemented")

def compile_bloc(bloc):
    return "\n".join([compile_cmd(t) for t in bloc.children])

prg = grammaire.parse("""int main(int X) {
    int X;
    X = X + 1;

    int Y;
    Y = malloc(2+4);
return(X); }""")
#print(prg)
#prg2 = pp_prg(prg)
#print(prg2)
print(compile(prg))
    
