str main(int x,int y){
    int** p;
    p = malloc(4);
    *p = malloc(4);
    **p = x;
    str B;
    B = 'debut';
    str C;
    C = 'a';
    while(x>y){
        B = B + C;
        x = x-1;
    }
    printf(x);
    return(B);
}
