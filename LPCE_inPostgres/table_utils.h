//
// Created by wangf on 6/9/2021.
//

#ifndef POSTGRE_TABLE_UTILS_H
#define POSTGRE_TABLE_UTILS_H

//#include "aqo.h"
#include "lpce.h"

struct Column_info{
    int tag;
    char name[50];
};
struct Table_info{
    char tb_name[50];
    char abbr_name[50];
    int col_num;
    struct Column_info *column_info;
};
struct Table_info *table_info;

void init_table_column_info();
#endif //POSTGRE_TABLE_UTILS_H
