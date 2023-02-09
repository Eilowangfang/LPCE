#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "postgres.h"
#include "miscadmin.h"

void generate_cardinality();

double get_cardinality(int total_relids);

void generate_cardinality(){
    char* command_part_1 = "python3  /home/dbgroup/lpce/LPCE/LPCE-I/estimator.py \"";
    char* command_part_2 = query_text;

    if(card_type==2){
        char* command_part_3 = "\"";
        char* command = (char *) malloc(strlen(command_part_1) + strlen(command_part_2) + strlen(command_part_3));
        sprintf(command, "%s%s%s", command_part_1, command_part_2, command_part_3);
        FILE * fp = fopen("/home/dbgroup/postgres/pg_log.txt", "a+");
        fprintf(fp, "%s\n", command);
        fclose(fp);
        system(command);
    }

    //load estimated cardinalities
    FILE *fp = fopen("/home/dbgroup/lpce/LPCE/LPCE-I/est_cards.txt", "r");
    int relid, card, b=1;
    card_num = 0;
    while((b = fscanf(fp, "%d,%d\n", &relid, &card) != -1)){
        card_num += 1;
    }
    fclose(fp);

    cardinalities = (int*)malloc(card_num * 2 * sizeof(int));
    int index = 0;
    fp = fopen("/home/dbgroup/lpce/LPCE/LPCE-I/est_cards.txt", "r");
    while((b = fscanf(fp, "%d,%d\n", &relid, &card)!=-1)){
        cardinalities[index*2] = relid;
        cardinalities[index*2+1] = card;
        index += 1;
    }
    fclose(fp);
}

double get_cardinality(int total_relids){
    if(cardinalities==NULL){
        generate_cardinality();
    }

    for(int i=0; i<card_num; i++){
        if(cardinalities[i*2]==total_relids){
            return (double)cardinalities[i*2+1];
        }
    }

    // no estimated cardinality for this relids, return a big number
    return -1;
}