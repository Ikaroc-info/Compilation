str main(int X) {
    str B;
    B = 'abcde';
    int* C;
    C = malloc(4);
    *C = 100;
    printf(B);
    B.setcAt(X,*C);

return(B); }
