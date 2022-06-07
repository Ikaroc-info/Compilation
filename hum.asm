extern printf, atoi, malloc
global main
section .data
fmt: db "%d", 10, 0
_A : dq 0
C : dq 0
B : dq 0
X : dq 0

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

mov rdi, 4
call malloc
mov byte [rax +0], 99 
mov byte [rax +1], 100 
mov byte [rax +2], 101 
mov byte [rax + 3 ], 0

mov [C],rax
mov rax, [B]
 mov rbx ,0
debut2:
 cmp byte [rax+rbx],0
 je fin2
 inc rbx
 jmp debut2
 fin2:
 mov rax,rbx
push rax
mov rax, [C]
 mov rbx ,0
debut3:
 cmp byte [rax+rbx],0
 je fin3
 inc rbx
 jmp debut3
 fin3:
 mov rax,rbx
pop rbx
add rax,rbx
inc rax
mov rdi,rax
call malloc
mov rdx,rax
 push rax
            mov rax, [B]
 mov rbx ,0
debut1:
 cmp byte [rax+rbx],0
 je fin1
mov rcx,[rax+rbx]
mov [rdx+rbx],rcx 
inc rbx
 jmp debut1
 fin1:
add rdx,rbx                
mov rax, [C]
 mov rbx ,0
debut0:
 cmp byte [rax+rbx],0
 je fin0
mov rcx,[rax+rbx]
mov [rbx+rdx],rcx 
inc rbx
 jmp debut0
 fin0:
mov rcx,[rax+rbx+1]
mov [rdx + rbx+1],rcx
pop rax

mov [B],rax
mov rax, [X]
mov rbx,rax
mov rax, [B]
add rbx,rax
 movzx eax, BYTE [rbx]
 movsx eax, al
mov DWORD [_A], eax
mov rax, [_A]
mov [X],rax
mov rax, 1
push rax
mov rax, 1
pop rbx
cmp rax,rbx
je conditionv4
mov rax,0
jmp fincond4
conditionv4 :mov rax,1
fincond4 : cmp rax,rax
mov rdi, fmt
mov rsi,rax
xor rax,rax
call printf
mov rax, 1
push rax
mov rax, 0
pop rbx
cmp rax,rbx
je conditionv5
mov rax,0
jmp fincond5
conditionv5 :mov rax,1
fincond5 : cmp rax,rax
mov rdi, fmt
mov rsi,rax
xor rax,rax
call printf
mov rax, 1
push rax
mov rax, 2
pop rbx
cmp rax,rbx
jge conditionv6
mov rax,0
jmp fincond6
conditionv6 :mov rax,1
fincond6 : cmp rax,rax
mov rdi, fmt
mov rsi,rax
xor rax,rax
call printf
mov rax, 1
push rax
mov rax, 0
pop rbx
cmp rax,rbx
jge conditionv7
mov rax,0
jmp fincond7
conditionv7 :mov rax,1
fincond7 : cmp rax,rax
mov rdi, fmt
mov rsi,rax
xor rax,rax
call printf
mov rax, 4
push rax
mov rax, 3
pop rbx
cmp rax,rbx
jl conditionv8
mov rax,0
jmp fincond8
conditionv8 :mov rax,1
fincond8 : cmp rax,rax
mov rdi, fmt
mov rsi,rax
xor rax,rax
call printf
mov rax, 1
push rax
mov rax, 0
pop rbx
cmp rax,rbx
jg conditionv9
mov rax,0
jmp fincond9
conditionv9 :mov rax,1
fincond9 : cmp rax,rax
mov rdi, fmt
mov rsi,rax
xor rax,rax
call printf
mov rax, [X]

  mov rdi, fmt
  mov rsi, rax
  xor rax, rax
  call printf
  add rsp, 16
  pop rbp
  ret

