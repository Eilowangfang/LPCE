/*
 *******************************************************************************
 *
 *	HASH FUNCTIONS
 *
 * The main purpose of hash functions in this approach is two reflect objects
 * similarity. We want similar objects to be mapped into the same hash value.
 *
 * In our approach we consider that objects are similar if their difference lies
 * only in the values of their constants. We want query_hash, clause_hash and
 * fss_hash to satisfy this property.
 *
 *******************************************************************************
 *
 * Copyright (c) 2016-2021, Postgres Professional
 *
 * IDENTIFICATION
 *	  aqo/hash.c
 *
 */
//#include "aqo.h"
#include "lpce.h"
#include "commands/extension.h"
#include "table_utils.h"
#include <stdlib.h>

static int	get_str_hash(const char *str);
static int	get_node_hash(Node *node);
static int	get_int_array_hash(int *arr, int len);
static int	get_unsorted_unsafe_int_array_hash(int *arr, int len);
static int	get_unordered_int_list_hash(List *lst);

static int	get_relidslist_hash(List *relidslist);
static int get_fss_hash(int clauses_hash, int eclasses_hash,
			 int relidslist_hash);

static char *replace_patterns(const char *str, const char *start_pattern,
				 bool (*end_pattern) (char ch));
static char *remove_consts(const char *str);
static char *remove_locations(const char *str);

static int	get_id_in_sorted_int_array(int val, int n, int *arr);
static int get_arg_eclass(int arg_hash, int nargs,
			   int *args_hash, int *eclass_hash);

static void get_clauselist_args(List *clauselist, int *nargs, int **args_hash);
static int	disjoint_set_get_parent(int *p, int v);
static void disjoint_set_merge_eclasses(int *p, int v1, int v2);
static int *perform_eclasses_join(List *clauselist, int nargs, int *args_hash);

static bool is_brace(char ch);
static bool has_consts(List *lst);
static List **get_clause_args_ptr(Expr *clause);
static bool clause_is_eq_clause(Expr *clause);


//From Fang
void get_clause_content(Expr *clause);
void get_node_content(Node *node);
void get_involved_table();
void get_involved_condiction();
void get_plan_for_LPCE();
void get_code_for_LPCE();
void call_LPCE();

//From Fang utility function
int get_table_no(char *component);
int get_column_no(char *component);
void get_filter_clause_with_table_column(int tb_no, int col_no, bool line);
void get_filter_clause_with_table_column_injoin(int tb_no, int col_no, bool line, int no);
void get_join_clause(char *str);
int find_str(char* str1,char* str2);
char *mid_str(char *dst,char *src, int n,int m);
int str_occurence(char *src, char *term);
int str_occur_pos(char *src, char *term, int no);
void get_no_component(char *str, char *res, int no);

#define STRINGSPACE 10240
char query_plan_lpce[STRINGSPACE];
char subquery_str[STRINGSPACE];
int used_table_num;
int involved_clause_num;
struct Table_tag{
    int tag;
    char name[30];
};
struct Table_tag *tb_tag;
struct Condiction_clause{
    char text[50];
};
struct Condiction_clause *condic_clause;
double code_for_LPCE[STRINGSPACE];




/*
 * Computes hash for given query.
 * Hash is supposed to be constant-insensitive.
 * XXX: Hashing depend on Oids of database objects. It is restrict usability of
 * the AQO knowledge base by current database at current Postgres instance.
 */
int
get_query_hash(Query *parse, const char *query_text)
{
	char	   *str_repr;
	int			hash;

	str_repr = remove_locations(remove_consts(nodeToString(parse)));
	hash = DatumGetInt32(hash_any((const unsigned char *) str_repr,
								  strlen(str_repr) * sizeof(*str_repr)));
	pfree(str_repr);

	return hash;
}

/*
 * For given object (clauselist, selectivities, relidslist) creates feature
 * subspace:
 *		sets nfeatures
 *		creates and computes fss_hash
 *		transforms selectivities to features
 */
int
get_fss_for_object(List *clauselist, List *selectivities, List *relidslist,
				   int *nfeatures, double **features)
{
	int			n;
	int		   *clause_hashes;
	int		   *sorted_clauses;
	int		   *idx;
	int		   *inverse_idx;
	bool	   *clause_has_consts;
	int			nargs;
	int		   *args_hash;
	int		   *eclass_hash;
	int			clauses_hash;
	int			eclasses_hash;
	int			relidslist_hash;
	List	  **args;
	ListCell   *l;
	int			i,
				j,
				k,
				m;
	int			sh = 0,
				old_sh;
	int fss_hash;

	n = list_length(clauselist);

	get_eclasses(clauselist, &nargs, &args_hash, &eclass_hash);

	clause_hashes = palloc(sizeof(*clause_hashes) * n);
	clause_has_consts = palloc(sizeof(*clause_has_consts) * n);
	sorted_clauses = palloc(sizeof(*sorted_clauses) * n);
	*features = palloc0(sizeof(**features) * n);

	i = 0;
	foreach(l, clauselist)
	{
		clause_hashes[i] = get_clause_hash(
										((RestrictInfo *) lfirst(l))->clause,
										   nargs, args_hash, eclass_hash);
		args = get_clause_args_ptr(((RestrictInfo *) lfirst(l))->clause);
		clause_has_consts[i] = (args != NULL && has_consts(*args));
		i++;
	}

	idx = argsort(clause_hashes, n, sizeof(*clause_hashes), int_cmp);
	inverse_idx = inverse_permutation(idx, n);

	i = 0;
	foreach(l, selectivities)
	{
		(*features)[inverse_idx[i]] = log(*((double *) (lfirst(l))));
		if ((*features)[inverse_idx[i]] < log_selectivity_lower_bound)
			(*features)[inverse_idx[i]] = log_selectivity_lower_bound;
		sorted_clauses[inverse_idx[i]] = clause_hashes[i];
		i++;
	}

	for (i = 0; i < n;)
	{
		k = 0;
		for (j = i; j < n && sorted_clauses[j] == sorted_clauses[i]; ++j)
			k += (int) clause_has_consts[idx[j]];
		m = j;
		old_sh = sh;
		for (j = i; j < n && sorted_clauses[j] == sorted_clauses[i]; ++j)
			if (clause_has_consts[idx[j]] || k + 1 == m - i)
			{
				(*features)[j - sh] = (*features)[j];
				sorted_clauses[j - sh] = sorted_clauses[j];
			}
			else
				sh++;
		qsort(&((*features)[i - old_sh]), j - sh - (i - old_sh),
			  sizeof(**features), double_cmp);
		i = j;
	}

	*nfeatures = n - sh;
	(*features) = repalloc(*features, (*nfeatures) * sizeof(**features));

	/*
	 * Generate feature subspace hash.
	 * XXX: Remember! that relidslist_hash isn't portable between postgres
	 * instances.
	 */
	clauses_hash = get_int_array_hash(sorted_clauses, *nfeatures);
	eclasses_hash = get_int_array_hash(eclass_hash, nargs);
	relidslist_hash = get_relidslist_hash(relidslist);
	fss_hash = get_fss_hash(clauses_hash, eclasses_hash, relidslist_hash);

	pfree(clause_hashes);
	pfree(sorted_clauses);
	pfree(idx);
	pfree(inverse_idx);
	pfree(clause_has_consts);
	pfree(args_hash);
	pfree(eclass_hash);
	return fss_hash;
}

/*
 * Computes hash for given clause.
 * Hash is supposed to be constant-insensitive.
 * Also args-order-insensitiveness for equal clause is required.
 */
int
get_clause_hash(Expr *clause, int nargs, int *args_hash, int *eclass_hash)
{
	Expr	   *cclause;
	List	  **args = get_clause_args_ptr(clause);
	int			arg_eclass;
	ListCell   *l;

	if (args == NULL)
        return get_node_hash((Node *) clause);

	cclause = copyObject(clause);
	args = get_clause_args_ptr(cclause);
	foreach(l, *args)
	{
		arg_eclass = get_arg_eclass(get_node_hash(lfirst(l)),
									nargs, args_hash, eclass_hash);
		if (arg_eclass != 0)
		{
			lfirst(l) = makeNode(Param);
			((Param *) lfirst(l))->paramid = arg_eclass;
		}
	}
	if (!clause_is_eq_clause(clause) || has_consts(*args))
		return get_node_hash((Node *) cclause);
	return get_node_hash((Node *) linitial(*args));
}

/*
 * Computes hash for given string.
 */
int
get_str_hash(const char *str)
{
	return DatumGetInt32(hash_any((const unsigned char *) str,
								  strlen(str) * sizeof(*str)));
}

/*
 * Computes hash for given node.
 */
int
get_node_hash(Node *node)
{
	char	   *str;
	int			hash;

	str = remove_locations(remove_consts(nodeToString(node)));
    //elog(INFO, "Fang aqo get_node_hash %s ", nodeToString(node));
	hash = get_str_hash(str);
	pfree(str);
	return hash;
}

/*
 * Computes hash for given array of ints.
 */
int
get_int_array_hash(int *arr, int len)
{
	return DatumGetInt32(hash_any((const unsigned char *) arr,
								  len * sizeof(*arr)));
}

/*
 * Computes hash for given unsorted array of ints.
 * Sorts given array in-place to compute hash.
 * The hash is order-insensitive.
 */
int
get_unsorted_unsafe_int_array_hash(int *arr, int len)
{
	qsort(arr, len, sizeof(*arr), int_cmp);
	return get_int_array_hash(arr, len);
}

/*
 * Returns for an integer list a hash which does not depend on the order
 * of elements.
 *
 * Copies given list into array, sorts it and then computes its hash
 * using 'hash_any'.
 * Frees allocated memory before returning hash.
 */
int
get_unordered_int_list_hash(List *lst)
{
	int			i = 0;
	int			len;
	int		   *arr;
	ListCell   *l;
	int			hash;

	len = list_length(lst);
	arr = palloc(sizeof(*arr) * len);
	foreach(l, lst)
		arr[i++] = lfirst_int(l);
	hash = get_unsorted_unsafe_int_array_hash(arr, len);
	pfree(arr);
	return hash;
}

/*
 * Returns the C-string in which the substrings of kind
 * "<start_pattern>[^<end_pattern>]*" are replaced with substring
 * "<start_pattern>".
 */
char *
replace_patterns(const char *str, const char *start_pattern,
				 bool (*end_pattern) (char ch))
{
	int			i = 0;
	int			j = 0;
	int			start_pattern_len = strlen(start_pattern);
	char	   *res = palloc0(sizeof(*res) * (strlen(str) + 1));

	for (i = 0; str[i];)
	{
		if (i >= start_pattern_len && strncmp(&str[i - start_pattern_len],
											  start_pattern,
											  start_pattern_len) == 0)
		{
			while (str[i] && !end_pattern(str[i]))
				i++;
		}
		if (str[i])
			res[j++] = str[i++];
	}

	return res;
}

/*
 * Computes hash for given feature subspace.
 * Hash is supposed to be clause-order-insensitive.
 */
int
get_fss_hash(int clauses_hash, int eclasses_hash, int relidslist_hash)
{
	int			hashes[3];

	hashes[0] = clauses_hash;
	hashes[1] = eclasses_hash;
	hashes[2] = relidslist_hash;
	return DatumGetInt32(hash_any((const unsigned char *) hashes,
								  3 * sizeof(*hashes)));
}

/*
 * Computes hash for given list of relids.
 * Hash is supposed to be relids-order-insensitive.
 */
int
get_relidslist_hash(List *relidslist)
{
	return get_unordered_int_list_hash(relidslist);
}

/*
 * Returns the C-string in which the substrings of kind "{CONST.*}" are
 * replaced with substring "{CONST}".
 */
char *
remove_consts(const char *str)
{
	char *res;

	res = replace_patterns(str, "{CONST", is_brace);
	res = replace_patterns(res, ":stmt_len", is_brace);
	return res;
}

/*
 * Returns the C-string in which the substrings of kind " :location.*}" are
 * replaced with substring " :location}".
 */
char *
remove_locations(const char *str)
{
	return replace_patterns(str, " :location", is_brace);
}

/*
 * Returns index of given value in given sorted integer array
 * or -1 if not found.
 */
int
get_id_in_sorted_int_array(int val, int n, int *arr)
{
	int		   *i;
	int			di;

	i = bsearch(&val, arr, n, sizeof(*arr), int_cmp);
	if (i == NULL)
		return -1;

	di = (unsigned char *) i - (unsigned char *) arr;
	di /= sizeof(*i);
	return di;
}

/*
 * Returns class of equivalence for given argument hash or 0 if such hash
 * does not belong to any equivalence class.
 */
int
get_arg_eclass(int arg_hash, int nargs, int *args_hash, int *eclass_hash)
{
	int			di = get_id_in_sorted_int_array(arg_hash, nargs, args_hash);

	if (di == -1)
		return 0;
	else
		return eclass_hash[di];
}

/*
 * Builds list of non-constant arguments of equivalence clauses
 * of given clauselist.
 */
void
get_clauselist_args(List *clauselist, int *nargs, int **args_hash)
{
	RestrictInfo *rinfo;
	List	  **args;
	ListCell   *l;
	ListCell   *l2;
	int			i = 0;
	int			sh = 0;
	int			cnt = 0;

	foreach(l, clauselist)
	{
		rinfo = (RestrictInfo *) lfirst(l);
		args = get_clause_args_ptr(rinfo->clause);
		if (args != NULL && clause_is_eq_clause(rinfo->clause))
			foreach(l2, *args)
				if (!IsA(lfirst(l2), Const))
				cnt++;
	}

	*args_hash = palloc(cnt * sizeof(**args_hash));
	foreach(l, clauselist)
	{
		rinfo = (RestrictInfo *) lfirst(l);
		args = get_clause_args_ptr(rinfo->clause);
		if (args != NULL && clause_is_eq_clause(rinfo->clause))
			foreach(l2, *args)
				if (!IsA(lfirst(l2), Const))
				(*args_hash)[i++] = get_node_hash(lfirst(l2));
	}
	qsort(*args_hash, cnt, sizeof(**args_hash), int_cmp);

	for (i = 1; i < cnt; ++i)
		if ((*args_hash)[i - 1] == (*args_hash)[i])
			sh++;
		else
			(*args_hash)[i - sh] = (*args_hash)[i];

	*nargs = cnt - sh;
	*args_hash = repalloc(*args_hash, (*nargs) * sizeof(**args_hash));
}

/*
 * Returns class of an object in disjoint set.
 */
int
disjoint_set_get_parent(int *p, int v)
{
	if (p[v] == -1)
		return v;
	else
		return p[v] = disjoint_set_get_parent(p, p[v]);
}

/*
 * Merges two equivalence classes in disjoint set.
 */
void
disjoint_set_merge_eclasses(int *p, int v1, int v2)
{
	int			p1,
				p2;

	p1 = disjoint_set_get_parent(p, v1);
	p2 = disjoint_set_get_parent(p, v2);
	if (p1 != p2)
	{
		if ((v1 + v2) % 2)
			p[p1] = p2;
		else
			p[p2] = p1;
	}
}

/*
 * Constructs disjoint set on arguments.
 */
int *
perform_eclasses_join(List *clauselist, int nargs, int *args_hash)
{
	RestrictInfo *rinfo;
	int		   *p;
	ListCell   *l,
			   *l2;
	List	  **args;
	int			h2;
	int			i2,
				i3;

	p = palloc(nargs * sizeof(*p));
	memset(p, -1, nargs * sizeof(*p));

	foreach(l, clauselist)
	{
		rinfo = (RestrictInfo *) lfirst(l);
		args = get_clause_args_ptr(rinfo->clause);
		if (args != NULL && clause_is_eq_clause(rinfo->clause))
		{
			i3 = -1;
			foreach(l2, *args)
			{
				if (!IsA(lfirst(l2), Const))
				{
					h2 = get_node_hash(lfirst(l2));
					i2 = get_id_in_sorted_int_array(h2, nargs, args_hash);
					if (i3 != -1)
						disjoint_set_merge_eclasses(p, i2, i3);
					i3 = i2;
				}
			}
		}
	}

	return p;
}

/*
 * Constructs arg_hashes and arg_hash->eclass_hash mapping for all non-constant
 * arguments of equivalence clauses of given clauselist.
 */
void
get_eclasses(List *clauselist, int *nargs, int **args_hash, int **eclass_hash)
{
	int		   *p;
	List	  **lsts;
	int			i,
				v;
	int		   *e_hashes;

	get_clauselist_args(clauselist, nargs, args_hash);

	p = perform_eclasses_join(clauselist, *nargs, *args_hash);

	lsts = palloc((*nargs) * sizeof(*lsts));
	e_hashes = palloc((*nargs) * sizeof(*e_hashes));
	for (i = 0; i < *nargs; ++i)
		lsts[i] = NIL;

	for (i = 0; i < *nargs; ++i)
	{
		v = disjoint_set_get_parent(p, i);
		lsts[v] = lappend_int(lsts[v], (*args_hash)[i]);
	}
	for (i = 0; i < *nargs; ++i)
		e_hashes[i] = get_unordered_int_list_hash(lsts[i]);

	*eclass_hash = palloc((*nargs) * sizeof(**eclass_hash));
	for (i = 0; i < *nargs; ++i)
		(*eclass_hash)[i] = e_hashes[disjoint_set_get_parent(p, i)];

	for (i = 0; i < *nargs; ++i)
		list_free(lsts[i]);
	pfree(lsts);
	pfree(p);
	pfree(e_hashes);
}

/*
 * Checks whether the given char is brace, i. e. '{' or '}'.
 */
bool
is_brace(char ch)
{
	return ch == '{' || ch == '}';
}

/*
 * Returns whether arguments list contain constants.
 */
bool
has_consts(List *lst)
{
	ListCell   *l;

	foreach(l, lst)
		if (IsA(lfirst(l), Const))
		return true;
	return false;
}

/*
 * Returns pointer on the args list in clause or NULL.
 */
List **
get_clause_args_ptr(Expr *clause)
{
	switch (clause->type)
	{
		case T_OpExpr:
			return &(((OpExpr *) clause)->args);
			break;
		case T_DistinctExpr:
			return &(((DistinctExpr *) clause)->args);
			break;
		case T_NullIfExpr:
			return &(((NullIfExpr *) clause)->args);
			break;
		case T_ScalarArrayOpExpr:
			return &(((ScalarArrayOpExpr *) clause)->args);
			break;
		default:
			return NULL;
			break;
	}
}

/*
 * Returns whether the clause is an equivalence clause.
 */
bool
clause_is_eq_clause(Expr *clause)
{
	/* TODO: fix this horrible mess */
	return (
			clause->type == T_OpExpr ||
			clause->type == T_DistinctExpr ||
			clause->type == T_NullIfExpr ||
			clause->type == T_ScalarArrayOpExpr
		) && (
			  ((OpExpr *) clause)->opno == Int4EqualOperator ||
			  ((OpExpr *) clause)->opno == BooleanEqualOperator ||
			  ((OpExpr *) clause)->opno == TextEqualOperator ||
			  ((OpExpr *) clause)->opno == TIDEqualOperator ||
			  ((OpExpr *) clause)->opno == ARRAY_EQ_OP ||
			  ((OpExpr *) clause)->opno == RECORD_EQ_OP ||
			  ((OpExpr *) clause)->opno == 15 ||
			  ((OpExpr *) clause)->opno == 92 ||
			  ((OpExpr *) clause)->opno == 93 ||
			  ((OpExpr *) clause)->opno == 94 ||
			  ((OpExpr *) clause)->opno == 352 ||
			  ((OpExpr *) clause)->opno == 353 ||
			  ((OpExpr *) clause)->opno == 385 ||
			  ((OpExpr *) clause)->opno == 386 ||
			  ((OpExpr *) clause)->opno == 410 ||
			  ((OpExpr *) clause)->opno == 416 ||
			  ((OpExpr *) clause)->opno == 503 ||
			  ((OpExpr *) clause)->opno == 532 ||
			  ((OpExpr *) clause)->opno == 533 ||
			  ((OpExpr *) clause)->opno == 560 ||
			  ((OpExpr *) clause)->opno == 566 ||
			  ((OpExpr *) clause)->opno == 607 ||
			  ((OpExpr *) clause)->opno == 649 ||
			  ((OpExpr *) clause)->opno == 620 ||
			  ((OpExpr *) clause)->opno == 670 ||
			  ((OpExpr *) clause)->opno == 792 ||
			  ((OpExpr *) clause)->opno == 811 ||
			  ((OpExpr *) clause)->opno == 900 ||
			  ((OpExpr *) clause)->opno == 1093 ||
			  ((OpExpr *) clause)->opno == 1108 ||
			  ((OpExpr *) clause)->opno == 1550 ||
			  ((OpExpr *) clause)->opno == 1120 ||
			  ((OpExpr *) clause)->opno == 1130 ||
			  ((OpExpr *) clause)->opno == 1320 ||
			  ((OpExpr *) clause)->opno == 1330 ||
			  ((OpExpr *) clause)->opno == 1500 ||
			  ((OpExpr *) clause)->opno == 1535 ||
			  ((OpExpr *) clause)->opno == 1616 ||
			  ((OpExpr *) clause)->opno == 1220 ||
			  ((OpExpr *) clause)->opno == 1201 ||
			  ((OpExpr *) clause)->opno == 1752 ||
			  ((OpExpr *) clause)->opno == 1784 ||
			  ((OpExpr *) clause)->opno == 1804 ||
			  ((OpExpr *) clause)->opno == 1862 ||
			  ((OpExpr *) clause)->opno == 1868 ||
			  ((OpExpr *) clause)->opno == 1955 ||
			  ((OpExpr *) clause)->opno == 2060 ||
			  ((OpExpr *) clause)->opno == 2542 ||
			  ((OpExpr *) clause)->opno == 2972 ||
			  ((OpExpr *) clause)->opno == 3222 ||
			  ((OpExpr *) clause)->opno == 3516 ||
			  ((OpExpr *) clause)->opno == 3629 ||
			  ((OpExpr *) clause)->opno == 3676 ||
			  ((OpExpr *) clause)->opno == 3882 ||
			  ((OpExpr *) clause)->opno == 3240 ||
			  ((OpExpr *) clause)->opno == 3240
		);
}









/*
 * From Fang
 * For given object (clauselist, selectivities, relidslist) get path content
 * e.g., select count(*) from movie_info_idx mi_idx,movie_keyword mk where mk.movie_id=mi_idx.movie_id AND mk.keyword_id=788;
 * one node at the path might be "base relation scan with  restriction mk.keyword_id=788"
 *
 */
int
get_path_content(List *clauselist, List *selectivities, List *relidslist,
                   int *nfeatures, double **features)
{
    int			n;
    int		   *clause_hashes;
    int		   *sorted_clauses;
    int		   *idx;
    int		   *inverse_idx;
    bool	   *clause_has_consts;
    int			nargs;
    int		   *args_hash;
    int		   *eclass_hash;
    int			clauses_hash;
    int			eclasses_hash;
    int			relidslist_hash;
    List	  **args;
    ListCell   *l;
    int			i,
            j,
            k,
            m;
    int			sh = 0,
            old_sh;
    int fss_hash;

    n = list_length(clauselist);

    get_eclasses(clauselist, &nargs, &args_hash, &eclass_hash);

    clause_hashes = palloc(sizeof(*clause_hashes) * n);
    clause_has_consts = palloc(sizeof(*clause_has_consts) * n);
    sorted_clauses = palloc(sizeof(*sorted_clauses) * n);
    *features = palloc0(sizeof(**features) * n);


    elog(INFO, "\n\nFang print one subquery content");
    elog(INFO, "  Fang AQO Query String %s", query_text);
    elog(INFO, "  --->Fang Used Tables:");
    init_table_column_info();
    get_involved_table();
    elog(INFO, "  --->Fang Involved conditions:");
    get_involved_condiction();

    memset(subquery_str,'\0',sizeof(subquery_str));
    foreach(l, clauselist){
        //elog(INFO, "    Fang subquery one node info component:");
        strcat(subquery_str, "Fang subquery one node info component:\n");
        get_clause_content(
                ((RestrictInfo *) lfirst(l))->clause);
    }
    elog(INFO, "  --->Fang one subquery for estimation:\n%s", subquery_str);

    memset(query_plan_lpce,'\0',sizeof(query_plan_lpce));
    get_plan_for_LPCE();
    elog(INFO, "  --->Fang one subquery translate to code:");
    get_code_for_LPCE();
    call_LPCE();
    return n;
}


/*
 * From Fang
 * Translate execution plan into code to feed into LPCE
 * LPCE estimate the cardinality according to feature code
 * For example: to estimate "where A_col1 = B_col2 AND A_col2 = 10"
 * One execution plan should be:
 * root node: A_col = B_col2
 * next level (right/left) node: A_col = 10
 * next level (right/left) node: B_col2
 * We translate the plan into feature code:
 * vector 1: 0 0 0 1...
 * vector 2: 0 1 0 ....
 * vector 3: 1 0 0 ....
 */
void get_code_for_LPCE(){
    int num = str_occurence(query_plan_lpce, "\n");
    elog(INFO, "      ===> node vector num: %d", num);

    //join code generator
    //filter code generator
}





/*Pass by List: Transform an C Array to Python List*/
void call_LPCE(){
    FILE *f;
    char s[1024];
    int ret;
    f = popen("python3 /home/csfwang/pytest.py", "r");
    while((ret=fread(s,1,1024,f))>0) {
        fwrite(s,1,ret,stdout);
    }
    elog(INFO, "      ===> python result: %s", s);

    fclose(f);
    return 0;
}

/*
 * From Fang
 * Obtain execution plan to feed into LPCE
 * LPCE estimate the cardinality according to exeuction plan
 * For example: to estimate "where A_col1 = B_col2 AND A_col2 = 10"
 * One execution plan should be:
 * root node: A_col = B_col2
 * next level (right/left) node: A_col = 10
 * next level (right/left) node: B_col2
 * We output the nodes according to DFS order.
 */
get_plan_for_LPCE(){

    bool final_node_is_join = false;
    bool final_node_is_filter_twopred = false;
    bool final_node_is_filter_onepred = false;

    int begin=str_occur_pos(subquery_str,"info component",1);
    int end=str_occur_pos(subquery_str,"info component",2);
    if(begin>=0 && end>=0) {
        char tmp[STRINGSPACE] = {""};
        strncpy(tmp, subquery_str + begin, end - begin);
        if(str_occurence(tmp, "===>{VAR :") > 1) {
            elog(INFO, "  --->Fang this node is hash join");
            final_node_is_join=true;
        }
    }



    if(!final_node_is_join){
        if (str_occurence(subquery_str, "info component:") > 2){
            elog(INFO, "  --->Fang this node is filter with >2 predicates, not supported");
        }else if(str_occurence(subquery_str, "info component:") > 1) {
            final_node_is_filter_twopred=true;
            elog(INFO, "  --->Fang this node is filter with two predicates");
        }else{
            final_node_is_filter_onepred=true;
            elog(INFO, "  --->Fang this node is filter with one predicate");
        }
    }

    //extract filter node
    //extract table
    //extract column
    if(final_node_is_filter_onepred){
        int tb_no = get_table_no(subquery_str);
        int col_no = get_column_no(subquery_str);
        get_filter_clause_with_table_column(tb_no, col_no, true);
    }
    if(final_node_is_filter_twopred){
        char tmp[STRINGSPACE]={""};
        get_no_component(subquery_str,tmp,1);
        int tb_no = get_table_no(tmp);
        int col_no = get_column_no(tmp);
        get_filter_clause_with_table_column(tb_no, col_no, true);
        get_no_component(subquery_str,tmp,2);
        tb_no = get_table_no(tmp);
        col_no = get_column_no(tmp);
        get_filter_clause_with_table_column(tb_no, col_no, false);
    }

    //extract join node
    //how many joins

    //how many filter
    if(final_node_is_join){
        int total_clause=str_occurence(subquery_str, "info component");

        int pre, pre_tb;
        for(int i=1; i<=total_clause; ++i){
            char tmp[STRINGSPACE]={""};
            get_no_component(subquery_str,tmp,i);


            //join clause
            if(str_occurence(tmp, "===>{VAR :") > 1){

                char change[STRINGSPACE]={""};
                int now=strlen(query_plan_lpce);
                get_join_clause(tmp);
                strncpy(change,query_plan_lpce+now,strlen(query_plan_lpce)-now);
                //elog(INFO, "      ===> join %d ===> ===> %s", i, change);

            }else{
                char change[STRINGSPACE]={""};
                int now=strlen(query_plan_lpce);

                int tb_no = get_table_no(tmp);
                int col_no = get_column_no(tmp);
                bool line=true;
                if(i==(pre+1) && tb_no==pre_tb)
                    line=false;
                get_filter_clause_with_table_column(tb_no, col_no, line);
                strncpy(change,query_plan_lpce+now,strlen(query_plan_lpce)-now);
                //elog(INFO, "      ===> filter %d ===> ===> %s  ---> %d %d", i, change, tb_no, col_no);

                pre=i;
                pre_tb=tb_no;
            }
        }
    }
    elog(INFO, "      ===> node feed LPCE: %s", query_plan_lpce);
}






void get_join_clause(char *str){
    //identify table name
    int total_VAR=str_occurence(str, "===>{VAR");

    if(total_VAR>2){
        elog(INFO, " Error: join clause has more than 2 columns");
        return;
    }

    char tmp[STRINGSPACE]={""};
    int pos = str_occur_pos(str, "===>{VAR", 1);
    int pos_next = str_occur_pos(str, "===>{VAR", 2);
    strncpy(tmp, str+pos, pos_next-pos);
    int tb_no_left=get_table_no(tmp);
    int col_no_left=get_column_no(tmp);

    memset(tmp,'\0', sizeof(tmp));
    strncpy(tmp, str+pos_next, strlen(str)-pos);
    int tb_no_right=get_table_no(tmp);
    int col_no_right=get_column_no(tmp);

    int used_tb_left=0;
    int used_tb_right=0;
    for(int i = 0; i < used_table_num; ++i){
        if(tb_tag[i].tag == tb_no_left){
            used_tb_left=i;
        }
        if(tb_tag[i].tag == tb_no_right){
            used_tb_right=i;
        }
    }


    int tb_real_no_left = -1;
    for(int i=0; i<9; ++i){
        int start = strcmp(tb_tag[used_tb_left].name, table_info[i].tb_name);
        if(start==0){
            tb_real_no_left=i;
        }
    }

    int tb_real_no_right = -1;
    for(int i=0; i<9; ++i){
        int start = strcmp(tb_tag[used_tb_right].name, table_info[i].tb_name);
        if(start==0){
            tb_real_no_right=i;
        }
    }

    char table[9][20]={"ci", "k", "mc", "mi", "mi_idx", "mk", "ml", "pi","t"};
    char left_col[STRINGSPACE]={""};
    char right_col[STRINGSPACE]={""};
    strcpy(left_col, table[tb_real_no_left]);
    strcat(left_col, ".");
    strcat(left_col, table_info[tb_real_no_left].column_info[col_no_left-1].name);
    strcpy(right_col, table[tb_real_no_right]);
    strcat(right_col, ".");
    strcat(right_col, table_info[tb_real_no_right].column_info[col_no_right-1].name);
    //elog(INFO, "      ===> node feed: %s %s", left_col, right_col);

    bool found=false;
    for(int i=0; i<involved_clause_num; ++i){
        int find_left=find_str(condic_clause[i].text, left_col);
        int find_right=find_str(condic_clause[i].text, right_col);
        if(find_left>=0 && find_right>=0){
            strcat(query_plan_lpce, condic_clause[i].text);
            strcat(query_plan_lpce, "\n");
            found=true;
        }
    }

    if(!found){
        strcat(query_plan_lpce, left_col);
        strcat(query_plan_lpce, "=");
        strcat(query_plan_lpce, right_col);
        strcat(query_plan_lpce, "\n");
    }

}


void get_filter_clause_with_table_column(int tb_no, int col_no, bool line){
    //identify table name

    int used_tb=0;
    for(int i = 0; i < used_table_num; ++i){
        if(tb_tag[i].tag == tb_no){
            elog(INFO, "                        @@@@> table %s\n", tb_tag[i].name);
            used_tb=i;
            break;
        }
    }
    //identify table no
    int tb_real_no = -1;
    for(int i=0; i<9; ++i){
        int start = strcmp(tb_tag[used_tb].name, table_info[i].tb_name);
        if(start==0){
            tb_real_no=i;
        }
    }

    //identify clause with table and column no
    for(int i=0; i<involved_clause_num; ++i){
        int find=find_str(condic_clause[i].text, table_info[tb_real_no].column_info[col_no-1].name);
        int find_n=find_str(condic_clause[i].text, table_info[tb_real_no].abbr_name);
        int find_filter=str_occurence(condic_clause[i].text, ".");
        if(find>=0 && find_n>=0  && find_filter==1){
            if(!line){
                char tmp[STRINGSPACE]={""};
                strncpy(tmp,query_plan_lpce,strlen(query_plan_lpce)-1);
                memset(query_plan_lpce, '\0',strlen(query_plan_lpce));
                strcat(query_plan_lpce, tmp);
                strcat(query_plan_lpce, " AND ");
            }
            strcat(query_plan_lpce, condic_clause[i].text);
            strcat(query_plan_lpce, "\n");
            break;
        }
    }

}










void get_no_component(char *str, char *res, int no){
    int total_occ=str_occurence(str, "info component");
    char tmp[STRINGSPACE]={""};

    if(no > total_occ) {
        elog(INFO, "  Error: exceed the maximum length str");
    }else if(no == total_occ){
        int pos = str_occur_pos(str, "info component", no);
        strncpy(tmp, str+pos, strlen(str)-pos);
    }else{
        int pos = str_occur_pos(str, "info component", no);
        int pos_next = str_occur_pos(str, "info component", no+1);
        strncpy(tmp, str+pos, pos_next-pos);
    }
    memset(res, '\0', sizeof(res));
    strcpy(res,tmp);
}






int get_table_no(char *component){
    int table_no = 0;
    int start = find_str(component, "varno ");
    int len = strlen("varno ");
    if(start>=0){
        char no[STRINGSPACE]={""};

        char c = *(component+start + len + 1);
        if(c == ' '){
            strncpy(no, component+start+len,1);
            table_no = atoi (no);
        }else{
            strncpy(no, component+start+len,2);
            table_no += atoi (no);
        }
    }
    return table_no;
}


int get_column_no(char *component){
    int colu_no = 0;
    int start = find_str(component, "varattno ");
    int len = strlen("varattno ");
    if(start>=0){
        char no[STRINGSPACE]={""};

        char c = *(component+start + len + 1);
        if(c == ' '){
            strncpy(no, component+start+len,1);
            colu_no = atoi (no);
        }else{
            strncpy(no, component+start+len,2);
            colu_no += atoi (no);
        }
    }
    return colu_no;
}





/*
 * From Fang
 * Obtain involved table from query text
 * Keep the tables in structure list tb_tag
 * For example: select count(*) from title t,movie_info mi where...;
 * The tables are t, mi
 */

void get_involved_table(){

    //all tables
    int start = find_str(query_text, "from");
    if(start < 0)
        start = find_str(query_text, "FROM");
    if(start < 0)
        start = find_str(query_text, "From");
    if(start < 0){
        elog(INFO, "Error: wrong sql query grammar (i.e., from)");
    }

    int end = find_str(query_text, "where");
    if(end < 0)
        end = find_str(query_text, "WHERE");
    if(end < 0)
        end = find_str(query_text, "Where");
    if(end < 0){
        elog(INFO, "Error: wrong sql query grammar (i.e., where)");
    }

    char table[9][20] = {"cast_info ci", "keyword k", "movie_companies mc", "movie_info mi",
                      "movie_info_idx mi_i", "movie_keyword mk", "movie_link ml", "person_info pi",
                      "title t"};

    char table_simp[9][20] = {"cast_info", "keyword", "movie_companies", "movie_info",
                         "movie_info_idx", "movie_keyword", "movie_link", "person_info",
                         "title"};

    int tb_num = 0;
    for(int i=0; i<9; ++i){
        int tmp = find_str(query_text, table[i]);
        if(tmp < end && tmp > start) {
            if(tmp > 0){
                tb_num++;
            }
        }
    }

    char query_tmp[STRINGSPACE]={""};
    strncpy(query_tmp,query_text+start,end-(start));



    tb_tag = (struct Table_tag*)malloc(sizeof(struct Table_tag) * tb_num);
    char delims[] = ",";
    char *result = NULL;
    char dest[STRINGSPACE];
    memset(dest,'\0',sizeof(dest));
    strcpy(dest, query_tmp);
    result = strtok(dest, delims);
    tb_num=0;
    while (result!= NULL){
        for(int i=0; i<9; ++i){
            int tmp = find_str(result, table[i]);
            if(tmp>=0 && tmp<strlen(result)) {
                tb_tag[tb_num].tag = tb_num+1;
                strcpy(tb_tag[tb_num].name, table_simp[i]);
                tb_num++;
                break;
            }
        }
        result = strtok(NULL, delims);
    }

    used_table_num = tb_num;
    for(int i=0; i<tb_num; ++i){
        elog(INFO, "    Fang Table %d %s ", tb_tag[i].tag, tb_tag[i].name);
    }

};





/*
 * From Fang
 * Obtain involved table from query text
 * Keep the tables in structure list condic_clause
 * For example: select count(*) from ... where mi.movie_id=t.id AND mi.info_type_id=7;
 * Condition clause 1) mi.movie_id=t.id 2)mi.info_type_id=7
 */
void get_involved_condiction(){

    int where_p = find_str(query_text, "where");
    if(where_p < 0)
        where_p = find_str(query_text, "WHERE");
    if(where_p < 0)
        where_p = find_str(query_text, "Where");
    if(where_p < 0){
        elog(INFO, "Error: wrong sql query grammar (i.e., where)");
    }


    char condi_text[1024]={""};
    strncpy(condi_text, query_text+where_p, strlen(query_text)-where_p);
    //elog(INFO, "        Fang: condi_text %s ", condi_text);


    int condi_num = 0;
    if(where_p >= 0){ //condiction after 'where'
        condi_num = 1;
    }

    int and_p = find_str(query_text, "AND ");
    if(and_p < 0)
        and_p = find_str(query_text, "And ");
    if(and_p < 0)
        and_p = find_str(query_text, "and ");
    if(and_p>=0){
        char remain[1024]={""};
        int start = find_str(condi_text, "AND");
        strncpy(remain, condi_text+start+3, strlen(condi_text)-start);
        condi_num++;
        //count number of condiction clauses
        int index = start;
        while(index < strlen(condi_text)){
            start = find_str(remain, "AND");
            if(start > 0){
                char tmp[1024]={""};
                strcpy(tmp, remain);
                memset(remain, '\0', sizeof(remain));
                strncpy(remain, tmp+start+3, strlen(tmp)-(start+3));
                index += start+3;
                condi_num++;
            }else{
                break;
            }
        }
    }


    condic_clause = (struct Condiction_clause*)malloc(sizeof(struct Condiction_clause)*condi_num);
    involved_clause_num = condi_num;
    if(condi_num == 1){
        //extract condition after where
        char clause[1024]={""};
        strncpy(clause, condi_text+6, strlen(condi_text)-7);
        strcpy(condic_clause[0].text, clause);
    }else if(condi_num > 1){

        char clause[1024]={""};
        int start = find_str(condi_text, "AND");
        strncpy(clause, condi_text+6, start-7);
        strcpy(condic_clause[0].text, clause);

        char remain[1024]={""};
        strncpy(remain, condi_text+start+4, strlen(condi_text)-start);
        for(int i=1; i<condi_num; ++i){
            if(i < condi_num-1)
                start = find_str(remain, "AND");
            else
                start = find_str(remain, ";");
            if(start > 0) {
                if(i < condi_num-1) {
                    char clause[1024]={""};
                    strncpy(clause, remain,  start-1);
                    strcpy(condic_clause[i].text, clause);
                    char tmp[1024] = {""};
                    strcpy(tmp, remain);
                    memset(remain, '\0', sizeof(remain));
                    strncpy(remain, tmp+start+4, strlen(tmp)-(start + 4));
                }else{
                    char clause[1024]={""};
                    strncpy(clause, remain,  start);
                    strcpy(condic_clause[i].text, clause);
                }
            }
        }
    }else{
        elog(INFO, "        Fang: no condition clause ");
    }

    for(int i=0; i<condi_num; ++i){
        elog(INFO, "           ##%s##", condic_clause[i].text);
    }
}







/*
 * From Fang
 * get clause content
 *
 */
void get_clause_content(Expr *clause)
{

    Expr	   *cclause;
    List	  **args = get_clause_args_ptr(clause);
    ListCell   *l;

    if (args == NULL)
        elog(INFO, "Blank node content");

    cclause = copyObject(clause);
    args = get_clause_args_ptr(cclause);
    foreach(l, *args){
        get_node_content(lfirst(l));
        //nodeToString(lfirst(l));
        strcat(subquery_str, "      ===>");
        strcat(subquery_str, nodeToString(lfirst(l)));
        strcat(subquery_str, "\n");
    }

    if (!clause_is_eq_clause(clause) || has_consts(*args)) {
        get_node_content((Node *) cclause);
        strcat(subquery_str, "      ===>");
        strcat(subquery_str, nodeToString((Node *) cclause));
        strcat(subquery_str, "\n");
    }
}




/*
 * From Fang
 * get clause content
 *
 */
void get_node_content(Node *node){
    char *str;
    str = remove_locations(remove_consts(nodeToString(node)));
    pfree(str);
    //elog(INFO, "        ===> %s", nodeToString(node));
}










/*
 * From Fang
 * utility function
 *
 */

int find_str(char* str1,char* str2){
    int i,j,flag=-1;
    for(i=0,j=0;str1[i]!=NULL;i++)
    {
        while(str1[i]==str2[j]&&str1[i]&&str2[j])
        {
            i++;
            j++;
            if(str2[j]==NULL)
            {
                flag=i-j;
                return flag;
            }
        }
        j=0;
    }
    return flag;
}


char *mid_str(char *dst,char *src, int n,int m){
    char *p = src;
    char *q = dst;
    int len = strlen(src);
    if(n>len) n = len-m;    /*从第m个到最后*/
    if(m<0) m=0;    /*从第一个开始*/
    if(m>len) return NULL;
    p += m;
    while(n--) *(q++) = *(p++);
    *(q++)='\0'; /*有必要吗？很有必要*/
    return dst;
}


int str_occurence(char *src, char *term){
    int occur = 0;
    int start = find_str(src, term);
    int len = strlen(term);
    if(start >=0) {
        char remain[STRINGSPACE] = {""};
        strncpy(remain, src + start + len, strlen(src) - start);
        occur++;
        //count number of condiction clauses
        int index = start;
        while (index < strlen(src)) {
            start = find_str(remain, term);
            if (start > 0) {
                char tmp[STRINGSPACE] = {""};
                strcpy(tmp, remain);
                memset(remain, '\0', sizeof(remain));
                strncpy(remain, tmp + start + len, strlen(tmp) - (start + len));
                index += start + len;
                occur++;
            } else {
                break;
            }
        }
    }
    return occur;
}




//Return position of no. no occurance
int str_occur_pos(char *src, char *term, int no){
    int pos = -1;
    int occur = 0;
    int start = find_str(src, term);
    int len = strlen(term);
    if(start >=0) {
        char remain[STRINGSPACE] = {""};
        strcpy(remain, src);
        //count number of condiction clauses
        int index = 0;
        while (index < strlen(src)) {
            start = find_str(remain, term);
            if (start > 0) {
                occur++;
                if(occur==no){
                    pos = index+start;
                    return pos;
                }
                char tmp[STRINGSPACE] = {""};
                strcpy(tmp, remain);
                memset(remain, '\0', sizeof(remain));
                strncpy(remain, tmp + start + len, strlen(tmp) - (start + len));
                index += start + len;
            } else {
                break;
            }
        }
    }
    return pos;
}
