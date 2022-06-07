#!/bin/bash
python3 compilo.py program.nc compile >hum.asm
nasm -felf64 hum.asm
gcc -no-pie -fno-pie hum.o
./a.out $1