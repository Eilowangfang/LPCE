/*-------------------------------------------------------------------------
 *
 * nodeSort.c
 *	  Routines to handle sorting of relations.
 *
 * Portions Copyright (c) 1996-2020, PostgreSQL Global Development Group
 * Portions Copyright (c) 1994, Regents of the University of California
 *
 *
 * IDENTIFICATION
 *	  src/backend/executor/nodeSort.c
 *
 *-------------------------------------------------------------------------
 */

#include "postgres.h"

#include "access/parallel.h"
#include "executor/execdebug.h"
#include "executor/nodeSort.h"
#include "miscadmin.h"
#include "utils/tuplesort.h"
#include "nodes/print.h"

//LPCE
struct SortNode_id_tuple *sortNode_RunLog;

/* ----------------------------------------------------------------
 *		ExecSort
 *
 *		Sorts tuples from the outer subtree of the node using tuplesort,
 *		which saves the results in a temporary file or memory. After the
 *		initial call, returns a tuple from the file with each call.
 *
 *		Conditions:
 *		  -- none.
 *
 *		Initial States:
 *		  -- the outer child is prepared to return the first tuple.
 * ----------------------------------------------------------------
 */
static TupleTableSlot *
ExecSort(PlanState *pstate)
{
	SortState  *node = castNode(SortState, pstate);
	EState	   *estate;
	ScanDirection dir;
	Tuplesortstate *tuplesortstate;
	TupleTableSlot *slot;

	CHECK_FOR_INTERRUPTS();

    double outerNode_tuple_counter = 0;

	/*
	 * get state info from node
	 */
	SO1_printf("ExecSort: %s\n",
			   "entering routine");

	estate = node->ss.ps.state;
	dir = estate->es_direction;
	tuplesortstate = (Tuplesortstate *) node->tuplesortstate;

	/*
	 * If first time through, read all tuples from outer plan and pass them to
	 * tuplesort.c. Subsequent calls just fetch tuples from tuplesort.
	 */

	if (!node->sort_Done)
	{
		Sort	   *plannode = (Sort *) node->ss.ps.plan;
		PlanState  *outerNode;
		TupleDesc	tupDesc;

		SO1_printf("ExecSort: %s\n",
				   "sorting subplan");

		/*
		 * Want to scan subplan in the forward direction while creating the
		 * sorted data.
		 */
		estate->es_direction = ForwardScanDirection;

		/*
		 * Initialize tuplesort module.
		 */
		SO1_printf("ExecSort: %s\n",
				   "calling tuplesort_begin");

		outerNode = outerPlanState(node);
		tupDesc = ExecGetResultType(outerNode);

		tuplesortstate = tuplesort_begin_heap(tupDesc,
											  plannode->numCols,
											  plannode->sortColIdx,
											  plannode->sortOperators,
											  plannode->collations,
											  plannode->nullsFirst,
											  work_mem,
											  NULL,
											  node->randomAccess);
		if (node->bounded)
			tuplesort_set_bound(tuplesortstate, node->bound);
		node->tuplesortstate = (void *) tuplesortstate;

		/*
		 * Scan the subplan and feed all the tuples to tuplesort.
		 */

		for (;;)
		{
            outerNode_tuple_counter++;

            slot = ExecProcNode(outerNode);

			if (TupIsNull(slot))
				break;

			tuplesort_puttupleslot(tuplesortstate, slot);
		}

		/*
		 * Complete the sort.
		 */
		tuplesort_performsort(tuplesortstate);

		/*
		 * restore to user specified direction
		 */
		estate->es_direction = dir;

		/*
		 * finally set the sorted flag to true
		 */
		node->sort_Done = true;
		node->bounded_Done = node->bounded;
		node->bound_Done = node->bound;
		if (node->shared_info && node->am_worker)
		{
			TuplesortInstrumentation *si;

			Assert(IsParallelWorker());
			Assert(ParallelWorkerNumber <= node->shared_info->num_workers);
			si = &node->shared_info->sinstrument[ParallelWorkerNumber];
			tuplesort_get_stats(tuplesortstate, si);
		}
		SO1_printf("ExecSort: %s\n", "sorting done");

		//LPCE
		//count the sort node total num
        outerNode_tuple_counter--;

        elog(INFO, "     ------> LPCE SORT NODE id: %ld  card: %lf", node->ss.ps.plan->plan_node_id, outerNode_tuple_counter);
        //When the current node terminate update its child node, info.
        card_runLog[node->ss.ps.plan->plan_node_id].node_card = outerNode_tuple_counter;
        card_runLog[node->ss.ps.plan->plan_node_id].done_subplan = true; //the sort node belongs to executed subplan
        //update its child (only outer) node
        int outerNode_id                       = outerPlanState(node)->plan->plan_node_id;
        card_runLog[outerNode_id].node_card    = outerNode_tuple_counter;
        card_runLog[outerNode_id].done_subplan = true;  //the child node belong to executed subplan


        if(LPCECheck && !LPCERerun){
            if(outerNode_tuple_counter < 1.0)
                outerNode_tuple_counter = 1.0;
            if(card_runLog[outerNode_id].estimate_card < 1.0)
                card_runLog[outerNode_id].estimate_card = 1.0;

            if(node->ss.ps.plan->plan_node_id >= 4 &&
                    ((outerNode_tuple_counter / card_runLog[outerNode_id].estimate_card) > 50 || (card_runLog[outerNode_id].estimate_card / outerNode_tuple_counter) > 50)){
                elog(INFO, "     +++++++>++++++> LPCE ExecSort Trigger Re-optimization Point: %d ", node->ss.ps.plan->plan_node_id);
                LPCERerun = true;
                LPCEEarlyStop = true;
                //the child node of sort is done
                //int outerNode_id = outerPlanState(node)->plan->plan_node_id;
                card_runLog[node->ss.ps.plan->plan_node_id].done_work = true;
            }
        }
    }

	SO1_printf("ExecSort: %s\n",
			   "retrieving tuple from tuplesort");

	/*
	 * Get the first or next tuple from tuplesort. Returns NULL if no more
	 * tuples.  Note that we only rely on slot tuple remaining valid until the
	 * next fetch from the tuplesort.
	 */
	slot = node->ss.ps.ps_ResultTupleSlot;
	(void) tuplesort_gettupleslot(tuplesortstate,
								  ScanDirectionIsForward(dir),
								  false, slot, NULL);

    //LPCE stop early
	if (LPCEEarlyStop){
	    //elog(INFO, "     ------> LPCE ExecSort node id %ld terminate with time %lf", node->ss.ps.plan->plan_node_id, (double)(clock() - lpce_cuptime)/CLOCKS_PER_SEC);
        return NULL;
    }
	return slot;
}

/* ----------------------------------------------------------------
 *		ExecInitSort
 *
 *		Creates the run-time state information for the sort node
 *		produced by the planner and initializes its outer subtree.
 * ----------------------------------------------------------------
 */
SortState *
ExecInitSort(Sort *node, EState *estate, int eflags)
{
	SortState  *sortstate;

	SO1_printf("ExecInitSort: %s\n",
			   "initializing sort node");

	/*
	 * create state structure
	 */
	sortstate = makeNode(SortState);
	sortstate->ss.ps.plan = (Plan *) node;
	sortstate->ss.ps.state = estate;
	sortstate->ss.ps.ExecProcNode = ExecSort;

    elog(INFO, "     ------> LPCE ExecInitSort at node %ld estimate tuples %.0f  %ld", sortstate->ss.ps.plan->plan_node_id, sortstate->ss.ps.plan->plan_rows,
         sortstate->ss.ps.plan->outer_relids);

	/*
	 * We must have random access to the sort output to do backward scan or
	 * mark/restore.  We also prefer to materialize the sort output if we
	 * might be called on to rewind and replay it many times.
	 */
	sortstate->randomAccess = (eflags & (EXEC_FLAG_REWIND |
										 EXEC_FLAG_BACKWARD |
										 EXEC_FLAG_MARK)) != 0;

	sortstate->bounded = false;
	sortstate->sort_Done = false;
	sortstate->tuplesortstate = NULL;

	/*
	 * Miscellaneous initialization
	 *
	 * Sort nodes don't initialize their ExprContexts because they never call
	 * ExecQual or ExecProject.
	 */

	/*
	 * initialize child nodes
	 *
	 * We shield the child node from the need to support REWIND, BACKWARD, or
	 * MARK/RESTORE.
	 */
	eflags &= ~(EXEC_FLAG_REWIND | EXEC_FLAG_BACKWARD | EXEC_FLAG_MARK);

	outerPlanState(sortstate) = ExecInitNode(outerPlan(node), estate, eflags);

	/*
	 * Initialize scan slot and type.
	 */
	ExecCreateScanSlotFromOuterPlan(estate, &sortstate->ss, &TTSOpsVirtual);

	/*
	 * Initialize return slot and type. No need to initialize projection info
	 * because this node doesn't do projections.
	 */
	ExecInitResultTupleSlotTL(&sortstate->ss.ps, &TTSOpsMinimalTuple);
	sortstate->ss.ps.ps_ProjInfo = NULL;

	SO1_printf("ExecInitSort: %s\n",
			   "sort node initialized");

    //LPCE
    //record the initial cardinality estimation at the node
    int node_id = sortstate->ss.ps.plan->plan_node_id;
    card_runLog[node_id].estimate_card = sortstate->ss.ps.plan->plan_rows;
    node_style[node_id]                = 6;
    card_runLog[node_id].outer_node_id = outerPlanState(sortstate)->plan->plan_node_id;
    //elog(INFO, "     ------>------> LPCE ExecInitSort outer node id %ld estimate tuples %.0f", card_runLog[node_id].outer_node_id, card_runLog[node_id].outer_card);


	return sortstate;
}

/* ----------------------------------------------------------------
 *		ExecEndSort(node)
 * ----------------------------------------------------------------
 */
void
ExecEndSort(SortState *node)
{
	SO1_printf("ExecEndSort: %s\n",
			   "shutting down sort node");

	/*
	 * clean out the tuple table
	 */
	ExecClearTuple(node->ss.ss_ScanTupleSlot);
	/* must drop pointer to sort result tuple */
	ExecClearTuple(node->ss.ps.ps_ResultTupleSlot);

    elog(INFO, "     ------>------> LPCE ExecEndSort");

	/*
	 * Release tuplesort resources
	 */
	if (node->tuplesortstate != NULL)
		tuplesort_end((Tuplesortstate *) node->tuplesortstate);
	node->tuplesortstate = NULL;

	/*
	 * shut down the subplan
	 */
	ExecEndNode(outerPlanState(node));

	SO1_printf("ExecEndSort: %s\n",
			   "sort node shutdown");
}

/* ----------------------------------------------------------------
 *		ExecSortMarkPos
 *
 *		Calls tuplesort to save the current position in the sorted file.
 * ----------------------------------------------------------------
 */
void
ExecSortMarkPos(SortState *node)
{
	/*
	 * if we haven't sorted yet, just return
	 */
	if (!node->sort_Done)
		return;

	tuplesort_markpos((Tuplesortstate *) node->tuplesortstate);
}

/* ----------------------------------------------------------------
 *		ExecSortRestrPos
 *
 *		Calls tuplesort to restore the last saved sort file position.
 * ----------------------------------------------------------------
 */
void
ExecSortRestrPos(SortState *node)
{
	/*
	 * if we haven't sorted yet, just return.
	 */
	if (!node->sort_Done)
		return;

	/*
	 * restore the scan to the previously marked position
	 */
	tuplesort_restorepos((Tuplesortstate *) node->tuplesortstate);
}

void
ExecReScanSort(SortState *node)
{
	PlanState  *outerPlan = outerPlanState(node);

	/*
	 * If we haven't sorted yet, just return. If outerplan's chgParam is not
	 * NULL then it will be re-scanned by ExecProcNode, else no reason to
	 * re-scan it at all.
	 */
	if (!node->sort_Done)
		return;

	/* must drop pointer to sort result tuple */
	ExecClearTuple(node->ss.ps.ps_ResultTupleSlot);

	/*
	 * If subnode is to be rescanned then we forget previous sort results; we
	 * have to re-read the subplan and re-sort.  Also must re-sort if the
	 * bounded-sort parameters changed or we didn't select randomAccess.
	 *
	 * Otherwise we can just rewind and rescan the sorted output.
	 */
	if (outerPlan->chgParam != NULL ||
		node->bounded != node->bounded_Done ||
		node->bound != node->bound_Done ||
		!node->randomAccess)
	{
		node->sort_Done = false;
		tuplesort_end((Tuplesortstate *) node->tuplesortstate);
		node->tuplesortstate = NULL;

		/*
		 * if chgParam of subnode is not null then plan will be re-scanned by
		 * first ExecProcNode.
		 */
		if (outerPlan->chgParam == NULL)
			ExecReScan(outerPlan);
	}
	else
		tuplesort_rescan((Tuplesortstate *) node->tuplesortstate);
}

/* ----------------------------------------------------------------
 *						Parallel Query Support
 * ----------------------------------------------------------------
 */

/* ----------------------------------------------------------------
 *		ExecSortEstimate
 *
 *		Estimate space required to propagate sort statistics.
 * ----------------------------------------------------------------
 */
void
ExecSortEstimate(SortState *node, ParallelContext *pcxt)
{
	Size		size;

	/* don't need this if not instrumenting or no workers */
	if (!node->ss.ps.instrument || pcxt->nworkers == 0)
		return;

	size = mul_size(pcxt->nworkers, sizeof(TuplesortInstrumentation));
	size = add_size(size, offsetof(SharedSortInfo, sinstrument));
	shm_toc_estimate_chunk(&pcxt->estimator, size);
	shm_toc_estimate_keys(&pcxt->estimator, 1);
}

/* ----------------------------------------------------------------
 *		ExecSortInitializeDSM
 *
 *		Initialize DSM space for sort statistics.
 * ----------------------------------------------------------------
 */
void
ExecSortInitializeDSM(SortState *node, ParallelContext *pcxt)
{
	Size		size;

	/* don't need this if not instrumenting or no workers */
	if (!node->ss.ps.instrument || pcxt->nworkers == 0)
		return;

	size = offsetof(SharedSortInfo, sinstrument)
		+ pcxt->nworkers * sizeof(TuplesortInstrumentation);
	node->shared_info = shm_toc_allocate(pcxt->toc, size);
	/* ensure any unfilled slots will contain zeroes */
	memset(node->shared_info, 0, size);
	node->shared_info->num_workers = pcxt->nworkers;
	shm_toc_insert(pcxt->toc, node->ss.ps.plan->plan_node_id,
				   node->shared_info);
}

/* ----------------------------------------------------------------
 *		ExecSortInitializeWorker
 *
 *		Attach worker to DSM space for sort statistics.
 * ----------------------------------------------------------------
 */
void
ExecSortInitializeWorker(SortState *node, ParallelWorkerContext *pwcxt)
{
	node->shared_info =
		shm_toc_lookup(pwcxt->toc, node->ss.ps.plan->plan_node_id, true);
	node->am_worker = true;
}

/* ----------------------------------------------------------------
 *		ExecSortRetrieveInstrumentation
 *
 *		Transfer sort statistics from DSM to private memory.
 * ----------------------------------------------------------------
 */
void
ExecSortRetrieveInstrumentation(SortState *node)
{
	Size		size;
	SharedSortInfo *si;

	if (node->shared_info == NULL)
		return;

	size = offsetof(SharedSortInfo, sinstrument)
		+ node->shared_info->num_workers * sizeof(TuplesortInstrumentation);
	si = palloc(size);
	memcpy(si, node->shared_info, size);
	node->shared_info = si;
}
