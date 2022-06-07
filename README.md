# Compilation
## Membres du groupe
Julien Jeanjacquot, Joachim De Bats et Bertrand Léo
## Fonctionnalités à implémenter
Typage (façon C), chaînes de caractères et pointeur

## Syntaxe de notre langage
### Spécificités
# Compilation
Il est possible de compiler votre programme en utilisant un fichier bash fournit (compil.sh), il prend un argument correspondant à un argument voulut dans le programme écrit dans program.nc.

Si votre programme prend en entrée plusieurs arguments, il faudra effectuer la procédure suivantes dans le terminal de commande :
 
python3 compilo.py "fichier_contenant_le_programme" compil>hum.asm

nasm -felf64 hum.asm

gcc -no-pie -fno-pie hum.o

./a.out 