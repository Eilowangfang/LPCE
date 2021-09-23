#include "lpce.h"
#include "optimizer/optimizer.h"
#include <stdlib.h>
#include <dlfcn.h>

double card_value[];
int find_str_pos(char* str1,char* str2);//find the frist pos of str2 at str1

void call_learncard(){
    FILE *f;
    char src[10240]={""};
    int ret;
    char query_stm[10240]={""};
    strcat(query_stm, "\"");
    strcat(query_stm, query_text);
    strcat(query_stm, "\"");
    //Call LPCE
    //You can also call your estimator here
    char cmd[10240] = "python3 /YOUR/PATH/TO/LPCE/parser.py ";
    strcat(cmd,query_stm);
    f = popen(cmd, "r");
    while((ret=fread(src,1,10240,f))>0) {
        fwrite(src,1,ret,stdout);
    }
    pclose(f);

    int pos=find_str_pos(src, "Learned estimator outputs cardinality:\n[");
    if(pos>=0){

        char estimat_card[409600]={""};
        int  len=strlen("Learned estimator outputs cardinality:\n[");
        strncpy(estimat_card, src+pos+len, strlen(src)-(+pos+len)-2);

        elog(INFO, "  ===>Fang prev count: \n ##%s## \n",estimat_card);
        int count = 0,i = 0;
        elog(INFO, "  ===>Fang prev count: %ld  %ld",count,strlen(estimat_card));


        while(*(estimat_card+i)){
            if(estimat_card[i] == ',')
                ++count;
            ++i;
        }

        count+=1;
        card_value[count];
        elog(INFO, "  ===>Fang count: %ld",count);


        char delims[]=",";
        char *result = NULL;
        int no=0;
        result = strtok(estimat_card, delims);
        while(result != NULL){
            card_value[no]=atof(result);
            no++;
            result = strtok( NULL, delims );
        }

        for(int i=0; i<count; i++){
            elog(INFO, "      ===> estimate card: %lf %ld", card_value[i], count);
        }

    }else{
        elog(INFO, "  ===>Fang LPCE Send Card Format Error");
    }
    return 0;
}




/*
 * General method for prediction the cardinality of given relation.
 */
double predict_for_relation_learnedmodel(){
    int		nfeatures;
    double	*matrix[aqo_K];
    double	targets[aqo_K];
    double	*features;
    double	result;
    int		rows;
    int		i;
    //int n = get_path_content(restrict_clauses, selectivities, relids,&nfeatures, &features);
    if(card_num==1)
        call_learncard();

    result = card_value[card_num-1];
    if (result < 0)
        return -1;
    else
        return result;
}


/*
 * General method for prediction the cardinality of given relation.
 */
double
predict_for_relation(List *restrict_clauses, List *selectivities,
					 List *relids, int *fss_hash)
{
	int		nfeatures;
	double	*matrix[aqo_K];
	double	targets[aqo_K];
	double	*features;
	double	result;
	int		rows;
	int		i;

    /*手动加载指定位置的so动态库*/
//    void* handle = dlopen("/home/hive/workspace/fang_workspace/postgre/postgresql-13.0/contrib/aqo/libtest.so", RTLD_LAZY);
//
//    int (*adapter_start_cpp)(int a);
//    adapter_start_cpp=dlsym(handle, "adapter_start_cpp");
//    elog(INFO, "  ===>Fang tru to call C++: %d \n", adapter_start_cpp(200));

	*fss_hash = get_fss_for_object(restrict_clauses, selectivities, relids,
														&nfeatures, &features);

	if (nfeatures > 0)
		for (i = 0; i < aqo_K; ++i)
			matrix[i] = palloc0(sizeof(**matrix) * nfeatures);

	if (load_fss(query_context.fspace_hash, *fss_hash, nfeatures, matrix,
				 targets, &rows))
		//result = OkNNr_predict(rows, nfeatures, matrix, targets, features);
	    result = -1;
	else
	{
		/*
		 * Due to planning optimizer tries to build many alternate paths. Many
		 * of these not used in final query execution path. Consequently, only
		 * small part of paths was used for AQO learning and fetch into the AQO
		 * knowledge base.
		 */
		result = -1;
	}

	pfree(features);
	if (nfeatures > 0)
	{
		for (i = 0; i < aqo_K; ++i)
			pfree(matrix[i]);
	}
	if (result < 0)
		return -1;
	else
		return clamp_row_est(exp(result));
}


int find_str_pos(char* str1,char* str2){
    int i,j,flag=-1;
    for(i=0,j=0;str1[i]!=NULL;i++){
        while(str1[i]==str2[j]&&str1[i]&&str2[j]){
            i++;
            j++;
            if(str2[j]==NULL){
                flag=i-j;
                return flag;
            }
        }
        j=0;
    }
    return flag;
}






