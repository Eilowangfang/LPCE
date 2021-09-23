/*
 *******************************************************************************
 *
 *	QUERY EXECUTION STATISTICS COLLECTING UTILITIES
 *
 * The module which updates data in the feature space linked with executed query
 * type using obtained query execution statistics.
 * Works only if aqo_learn is on.
 *
 *******************************************************************************
 *
 * Copyright (c) 2016-2021, Postgres Professional
 *
 * IDENTIFICATION
 *	  aqo/postprocessing.c
 *
 */

//#include "aqo.h"
#include "lpce.h"
#include "ignorance.h"

#include "access/parallel.h"
#include "optimizer/optimizer.h"
#include "postgres_fdw.h"
#include "utils/queryenvironment.h"


typedef struct
{
	List *clauselist;
	List *selectivities;
	List *relidslist;
	bool learn;
} aqo_obj_stat;

static double cardinality_sum_errors;
static int	cardinality_num_objects;

/* It is needed to recognize stored Query-related aqo data in the query
 * environment field.
 */
static char *AQOPrivateData = "AQOPrivateData";
static char *PlanStateInfo = "PlanStateInfo";




/*****************************************************************************
 *
 *	QUERY EXECUTION STATISTICS COLLECTING HOOKS
 *
 *****************************************************************************/


void
print_node_explain(ExplainState *es, PlanState *ps, Plan *plan, double rows)
{
	int wrkrs = 1;
	double error = -1.;

	if (!aqo_show_details || !plan || !ps->instrument)
		goto explain_end;

	Assert(es->format == EXPLAIN_FORMAT_TEXT);

	if (ps->worker_instrument && IsParallelTuplesProcessing(plan))
	{
		int i;

		for (i = 0; i < ps->worker_instrument->num_workers; i++)
		{
			Instrumentation *instrument = &ps->worker_instrument->instrument[i];

			if (instrument->nloops <= 0)
				continue;

			wrkrs++;
		}
	}

	appendStringInfoChar(es->str, '\n');
	Assert(es->format == EXPLAIN_FORMAT_TEXT);
	if (es->str->len == 0 || es->str->data[es->str->len - 1] == '\n')
		appendStringInfoSpaces(es->str, es->indent * 2);

	if (plan->predicted_cardinality > 0.)
	{
		error = 100. * (plan->predicted_cardinality - (rows*wrkrs))
									/ plan->predicted_cardinality;
		appendStringInfo(es->str,
						 "AQO: rows=%.0lf, error=%.0lf%%",
						 plan->predicted_cardinality, error);
	}
	else
		appendStringInfo(es->str, "AQO not used");

explain_end:
	if (plan && aqo_show_hash)
		appendStringInfo(es->str, ", fss=%d", plan->fss_hash);

	if (prev_ExplainOneNode_hook)
		prev_ExplainOneNode_hook(es, ps, plan, rows);
}

/*
 * Prints if the plan was constructed with AQO.
 */
void
print_into_explain(PlannedStmt *plannedstmt, IntoClause *into,
				   ExplainState *es, const char *queryString,
				   ParamListInfo params, const instr_time *planduration,
				   QueryEnvironment *queryEnv)
{
	if (prev_ExplainOnePlan_hook)
		prev_ExplainOnePlan_hook(plannedstmt, into, es, queryString,
								 params, planduration, queryEnv);

	if (!aqo_show_details)
		return;

	/* Report to user about aqo state only in verbose mode */
	ExplainPropertyBool("Using aqo", query_context.use_aqo, es);

	switch (aqo_mode)
	{
	case AQO_MODE_INTELLIGENT:
		ExplainPropertyText("AQO mode", "INTELLIGENT", es);
		break;
	case AQO_MODE_FORCED:
		ExplainPropertyText("AQO mode", "FORCED", es);
		break;
	case AQO_MODE_CONTROLLED:
		ExplainPropertyText("AQO mode", "CONTROLLED", es);
		break;
	case AQO_MODE_LEARN:
		ExplainPropertyText("AQO mode", "LEARN", es);
		break;
	case AQO_MODE_FROZEN:
		ExplainPropertyText("AQO mode", "FROZEN", es);
		break;
	case AQO_MODE_DISABLED:
		ExplainPropertyText("AQO mode", "DISABLED", es);
		break;
	default:
		elog(ERROR, "Bad AQO state");
		break;
	}

	/*
	 * Query class provides an user the conveniently use of the AQO
	 * auxiliary functions.
	 */
	if (aqo_mode != AQO_MODE_DISABLED || force_collect_stat)
	{
		if (aqo_show_hash)
			ExplainPropertyInteger("Query hash", NULL,
									query_context.query_hash, es);
		ExplainPropertyInteger("JOINS", NULL, njoins, es);
	}
}
