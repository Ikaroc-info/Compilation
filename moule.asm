extern printf, atoi, malloc
global main
section .data
fmt: db "%d", 10, 0
fmt1: db "%s", 10, 0
_A : dq 0
VAR_DECL

section .text
main:
  push rbp
  mov rbp, rsp
  push rdi
  push rsi

VAR_INIT
BODY
RETURN

  mov rdi, TYPE_RET
  mov rsi, rax
  xor rax, rax
  call printf
  add rsp, 16
  pop rbp
  ret
