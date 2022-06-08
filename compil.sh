#!/bin/bash
python3 compilo.py cp $1  >hum.asm
nasm -felf64 hum.asm
gcc -no-pie -fno-pie hum.o -o $2
