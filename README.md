# Compilation
## Membres du groupe
Julien Jeanjacquot, Joachim De Bats et Bertrand Léo
## Fonctionnalités à implémenter
Typage (façon C), chaînes de caractères et pointeur

## Syntaxe de notre langage

Types supportés :
int, str, int*,str*

Les variables doivent toutes être initialisées avant de leur attribuer une valeur

``` 
int A;
A=1;
```

<u>Pour les ints :</u>


Opérateur supportés : + ; - ; * ; == ; != ; < ; <= ; > ; >= ;

Fonction supportées : printf ;

<u>Pour les strings :</u>

`Pour attribuer un string à une variable, on utilise la syntaxe suivante :`
```
str var;
var = 'string';
```
`On ne pourra attribuer uniquement des chaînes de caractères commençant par une lettre et contenant des lettres et des chiffres`

Opérateur supportés : + ; == ;

Fonction supportées :  cAt ; len ; setcAt ;

Exemple d'utilisation :

```
str A;
A='abc';
printf(A.cAt(2));
printf(len(A));
printf(A.setcAt(2,'d'));
```


# Compilation

## Manuelle

Afin de compiler les programmes désirés, vous pourrez exécuter les commandes suivantes (les modes disponibles sont `cp` pour compiler et `pp` pour le pretty printer :

``` 
python3 compilo.py <mode> <fichier_a_compiler> > hum.asm
nasm -felf64 hum.asm
gcc -o sortie -no-pie -fno-pie hum.o 
./sortie <arguments>
```

## Automatique

Il est possible de compiler votre programme en utilisant un fichier bash fournit compil.sh, son premier argument correspond au nom du fichier à compiler, et son second argument correspond au nom du fichier exécutable en sortie.

`./compil.sh <nom_fichier_a_compiler> <nom_executable_en_sortie>`

Si vous souhaitez afficher le pretty-print de votre programme, il est possible de l'afficher en utilisant le fichier pretty-print.sh, son premier argument correspond au nom du fichier à compiler, et son second argument correspond au nom du fichier résultant.

`./pretty-print.sh <nom_fichier_a_compiler> <nom_executable_en_sortie>`
 
