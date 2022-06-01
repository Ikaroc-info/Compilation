# Compilation
 python3 compilo.py >hum.asm
 nasm -felf64 hum.asm
 gcc -no-pie -fno-pie hum.o
 ./a.out 