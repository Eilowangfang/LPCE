//
// Created by wangf on 6/9/2021.
//

#include "table_utils.h"


/*
 * From Fang
 * Init table and column information
 *
 */
void init_table_column_info(){
    int total_table_num=9;

    //cast_info
    table_info=(struct Table_info*)malloc(sizeof(struct Table_info)*total_table_num);
    strcpy(table_info[0].tb_name, "cast_info");
    strcpy(table_info[0].abbr_name, "ci");
    table_info[0].column_info = (struct Column_info*)malloc(sizeof(struct Column_info)*6);
    table_info[0].col_num = 6;
    table_info[0].column_info[0].tag = 1;
    strcpy(table_info[0].column_info[0].name, "id");
    table_info[0].column_info[1].tag = 2;
    strcpy(table_info[0].column_info[1].name, "person_id");
    table_info[0].column_info[2].tag = 3;
    strcpy(table_info[0].column_info[2].name, "movie_id");
    table_info[0].column_info[3].tag = 4;
    strcpy(table_info[0].column_info[3].name, "person_role_id");
    table_info[0].column_info[4].tag = 5;
    strcpy(table_info[0].column_info[4].name, "nr_order");
    table_info[0].column_info[5].tag = 6;
    strcpy(table_info[0].column_info[5].name, "role_id");


    //keyword
    strcpy(table_info[1].tb_name, "keyword");
    strcpy(table_info[0].abbr_name, "k");
    table_info[1].column_info = (struct Column_info*)malloc(sizeof(struct Column_info)*2);
    table_info[1].col_num = 2;
    table_info[1].column_info[0].tag = 1;
    strcpy(table_info[1].column_info[0].name, "id");
    table_info[1].column_info[1].tag = 2;
    strcpy(table_info[1].column_info[1].name, "keyword");

    //movie_companies
    strcpy(table_info[2].tb_name, "movie_companies");
    strcpy(table_info[2].abbr_name, "mc");
    table_info[2].column_info = (struct Column_info*)malloc(sizeof(struct Column_info)*4);
    table_info[2].col_num = 4;
    table_info[2].column_info[0].tag = 1;
    strcpy(table_info[2].column_info[0].name, "id");
    table_info[2].column_info[1].tag = 2;
    strcpy(table_info[2].column_info[1].name, "movie_id");
    table_info[2].column_info[2].tag = 3;
    strcpy(table_info[2].column_info[2].name, "company_id");
    table_info[2].column_info[3].tag = 4;
    strcpy(table_info[2].column_info[3].name, "company_type_id");



    //movie_info
    strcpy(table_info[3].tb_name, "movie_info");
    strcpy(table_info[3].abbr_name, "mi");
    table_info[3].column_info = (struct Column_info*)malloc(sizeof(struct Column_info)*3);
    table_info[3].col_num = 3;
    table_info[3].column_info[0].tag = 1;
    strcpy(table_info[3].column_info[0].name, "id");
    table_info[3].column_info[1].tag = 2;
    strcpy(table_info[3].column_info[1].name, "movie_id");
    table_info[3].column_info[2].tag = 3;
    strcpy(table_info[3].column_info[2].name, "info_type_id");


    //movie_info_idx
    strcpy(table_info[4].tb_name, "movie_info_idx");
    strcpy(table_info[4].abbr_name, "mi_idx");
    table_info[4].column_info = (struct Column_info*)malloc(sizeof(struct Column_info)*3);
    table_info[4].col_num = 3;
    table_info[4].column_info[0].tag = 1;
    strcpy(table_info[4].column_info[0].name, "id");
    table_info[4].column_info[1].tag = 2;
    strcpy(table_info[4].column_info[1].name, "movie_id");
    table_info[4].column_info[2].tag = 3;
    strcpy(table_info[4].column_info[2].name, "info_type_id");



    //movie_keyword
    strcpy(table_info[5].tb_name, "movie_keyword");
    strcpy(table_info[5].abbr_name, "mk");
    table_info[5].column_info = (struct Column_info*)malloc(sizeof(struct Column_info)*3);
    table_info[5].col_num = 3;
    table_info[5].column_info[0].tag = 1;
    strcpy(table_info[5].column_info[0].name, "id");
    table_info[5].column_info[1].tag = 2;
    strcpy(table_info[5].column_info[1].name, "movie_id");
    table_info[5].column_info[2].tag = 3;
    strcpy(table_info[5].column_info[2].name, "keyword_id");


    //movie_link
    strcpy(table_info[6].tb_name, "movie_link");
    strcpy(table_info[6].abbr_name, "ml");
    table_info[6].column_info = (struct Column_info*)malloc(sizeof(struct Column_info)*4);
    table_info[6].col_num = 4;
    table_info[6].column_info[0].tag = 1;
    strcpy(table_info[6].column_info[0].name, "id");
    table_info[6].column_info[1].tag = 2;
    strcpy(table_info[6].column_info[1].name, "movie_id");
    table_info[6].column_info[2].tag = 3;
    strcpy(table_info[6].column_info[2].name, "linked_movie_id");
    table_info[6].column_info[3].tag = 4;
    strcpy(table_info[6].column_info[3].name, "link_type_id");

    //person_info
    strcpy(table_info[7].tb_name, "person_info");
    strcpy(table_info[7].abbr_name, "pi");
    table_info[7].column_info = (struct Column_info*)malloc(sizeof(struct Column_info)*3);
    table_info[7].col_num = 3;
    table_info[7].column_info[0].tag = 1;
    strcpy(table_info[7].column_info[0].name, "id");
    table_info[7].column_info[1].tag = 2;
    strcpy(table_info[7].column_info[1].name, "movie_id");
    table_info[7].column_info[2].tag = 3;
    strcpy(table_info[7].column_info[2].name, "info_type_id");

    //title
    strcpy(table_info[8].tb_name, "title");
    strcpy(table_info[8].abbr_name, "t");
    table_info[8].column_info = (struct Column_info*)malloc(sizeof(struct Column_info)*3);
    table_info[8].col_num = 3;
    table_info[8].column_info[0].tag = 1;
    strcpy(table_info[8].column_info[0].name, "id");
    table_info[8].column_info[1].tag = 2;
    strcpy(table_info[8].column_info[1].name, "kind_id");
    table_info[8].column_info[2].tag = 3;
    strcpy(table_info[8].column_info[2].name, "production_year");
}

