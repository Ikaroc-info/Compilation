extern printf, atoi, malloc
global main
section .data
fmt: db "%d", 10, 0
_A : dq 0
X : dq 0
B : dq 0
C : dq 0

section .text
main:
  push rbp
  mov rbp, rsp
  push rdi
  push rsi

mov rbx, [rbp-0x10]
mov rdi,[rbx+8]
call atoi
mov [X], rax


mov rdi, 3
call malloc
mov byte [rax +0], 97 
mov byte [rax +1], 98 
mov byte [rax + 2 ], 0

mov [B],rax

mov rdi, 25
call malloc
mov byte [rax +0], 99 
mov byte [rax +1], 100 
mov byte [rax +2], 101 
mov byte [rax +3], 102 
mov byte [rax +4], 103 
mov byte [rax +5], 104 
mov byte [rax +6], 105 
mov byte [rax +7], 106 
mov byte [rax +8], 107 
mov byte [rax +9], 108 
mov byte [rax +10], 109 
mov byte [rax +11], 110 
mov byte [rax +12], 111 
mov byte [rax +13], 112 
mov byte [rax +14], 113 
mov byte [rax +15], 114 
mov byte [rax +16], 115 
mov byte [rax +17], 116 
mov byte [rax +18], 117 
mov byte [rax +19], 118 
mov byte [rax +20], 119 
mov byte [rax +21], 120 
mov byte [rax +22], 121 
mov byte [rax +23], 122 
mov byte [rax + 24 ], 0

mov [C],rax
mov rax, 1
mov rbx,rax
mov rax, [C]
 add rbx,rax
 mov rax, 104
 mov [rbx], al

mov rax, [X]
mov rbx,rax
mov rax, [C]
add rbx,rax
 movzx eax, BYTE [rbx]
 movsx eax, al
mov DWORD [_A], eax
mov rax, [_A]
mov [X],rax
mov rax, [X]

  mov rdi, fmt
  mov rsi, rax
  xor rax, rax
  call printf
  add rsp, 16
  pop rbp
  ret

