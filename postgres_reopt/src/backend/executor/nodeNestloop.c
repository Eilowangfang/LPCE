/*-------------------------------------------------------------------------
 *
 * nodeNestloop.c
 *	  routines to support nest-loop joins
 *
 * Portions Copyright (c) 1996-2020, PostgreSQL Global Development Group
 * Portions Copyright (c) 1994, Regents of the University of California
 *
 *
 * IDENTIFICATION
 *	  src/backend/executor/nodeNestloop.c
 *
 *-------------------------------------------------------------------------
 */
/*
 *	 INTERFACE ROUTINES
 *		ExecNestLoop	 - process a nestloop join of two plans
 *		ExecInitNestLoop - initialize the join
 *		ExecEndNestLoop  - shut down the join
 */

#include "postgres.h"

#include "executor/execdebug.h"
#include "executor/nodeNestloop.h"
#include "miscadmin.h"
#include "utils/memutils.h"
#include "nodes/print.h"

double outer_tuple_num = 0;
double inner_tuple_num = 0;
double max_inner_tuple = 0;



/* ----------------------------------------------------------------
 *		ExecNestLoop(node)
 *
 * old comments
 *		Returns the tuple joined from inner and outer tuples which
 *		satisfies the qualification clause.
 *
 *		It scans the inner relation to join with current outer tuple.
 *
 *		If none is found, next tuple from the outer relation is retrieved
 *		and the inner relation is scanned from the beginning again to join
 *		with the outer tuple.
 *
 *		NULL is returned if all the remaining outer tuples are tried and
 *		all fail to join with the inner tuples.
 *
 *		NULL is also returned if there is no tuple from inner relation.
 *
 *		Conditions:
 *		  -- outerTuple contains current tuple from outer relation and
 *			 the right son(inner relation) maintains "cursor" at the tuple
 *			 returned previously.
 *				This is achieved by maintaining a scan position on the outer
 *				relation.
 *
 *		Initial States:
 *		  -- the outer child and the inner child
 *			   are prepared to return the first tuple.
 * ----------------------------------------------------------------
 */
static TupleTableSlot *
ExecNestLoop_NATIVE(PlanState *pstate)
{
	NestLoopState *node = castNode(NestLoopState, pstate);
	NestLoop   *nl;
	PlanState  *innerPlan;
	PlanState  *outerPlan;
	TupleTableSlot *outerTupleSlot;
	TupleTableSlot *innerTupleSlot;
	ExprState  *joinqual;
	ExprState  *otherqual;
	ExprContext *econtext;
	ListCell   *lc;

	CHECK_FOR_INTERRUPTS();

    Tuplestorestate *tuplestorestate;

	/*
	 * get information from the node
	 */
	ENL1_printf("getting info from node");

	nl = (NestLoop *) node->js.ps.plan;
	joinqual = node->js.joinqual;
	otherqual = node->js.ps.qual;
	outerPlan = outerPlanState(node);
	innerPlan = innerPlanState(node);
	econtext = node->js.ps.ps_ExprContext;

	/*
	 * Reset per-tuple memory context to free any expression evaluation
	 * storage allocated in the previous tuple cycle.
	 */
	ResetExprContext(econtext);

	/*
	 * Ok, everything is setup for the join so now loop until we return a
	 * qualifying join tuple.
	 */
	ENL1_printf("entering main loop");


	for (;;)
	{
		/*
		 * 如果我们当前没有outer tuple, 我们就尝试通过执行outPlan的node，获取一个tuple
		 * If we don't have an outer tuple, get the next one and reset the
		 * inner scan.
		 */
		if (node->nl_NeedNewOuter)
		{
			ENL1_printf("getting new outer tuple");
			outerTupleSlot = ExecProcNode(outerPlan);

			//LPCE
			// Feed outer tuples into materialization tuplestore
			//if(outer_tuple_num == 0)
            //elog(INFO, "     ------> LPCE ExecNestLoop outer tuple    %ld", outer_tuple_num);
            outer_tuple_num++;
			/*
			 * 如果获取的outer tuple为空，说明当前NLJ操作可以结束了。
			 * if there are no more outer tuples, then the join is complete..
			 */
			if (TupIsNull(outerTupleSlot))
			{
				ENL1_printf("no outer tuple, ending join");

                elog(INFO, "     ------> LPCE ExecNestLoop Ending up");
				//LPCE
				//update the info of outer node of nested loop join
				int outer_node_id = card_runLog[node->js.ps.plan->plan_node_id].outer_node_id;
                card_runLog[outer_node_id].done_subplan = true;
                card_runLog[outer_node_id].node_card = outer_tuple_num - 1;

                //for nested loop join, the join is complete when the outer tuple is null
                int inner_node_id = card_runLog[node->js.ps.plan->plan_node_id].inner_node_id;
                card_runLog[inner_node_id].done_subplan = true;
                card_runLog[inner_node_id].node_card = inner_tuple_num;

                outer_tuple_num = 0;
                return NULL;
			}

            //for one tuple from outer path, all tuples from inner path are ready to be paired.
            inner_tuple_num = 0;

			ENL1_printf("saving new outer tuple information");
			econtext->ecxt_outertuple = outerTupleSlot;
			node->nl_NeedNewOuter = false;
			node->nl_MatchedOuter = false;

			/*
			 * 我们拿到了一个outer plan, 开始为NLJ做准备。对join的相关属性的信息检查确认
			 * NLJ支持equal join,和非equal的join 关联(>,<,>=,<=,<>)
			 * fetch the values of any outer Vars that must be passed to the
			 * inner scan, and store them in the appropriate PARAM_EXEC slots.
			 */
			foreach(lc, nl->nestParams)
			{
				NestLoopParam *nlp = (NestLoopParam *) lfirst(lc);
				int			paramno = nlp->paramno;
				ParamExecData *prm;

				prm = &(econtext->ecxt_param_exec_vals[paramno]);
				/* Param value should be an OUTER_VAR var */
				Assert(IsA(nlp->paramval, Var));
				Assert(nlp->paramval->varno == OUTER_VAR);
				Assert(nlp->paramval->varattno > 0);
				prm->value = slot_getattr(outerTupleSlot,
										  nlp->paramval->varattno,
										  &(prm->isnull));
				/* Flag parameter value as changed */
				innerPlan->chgParam = bms_add_member(innerPlan->chgParam,
													 paramno);
			}

			/*
			 * 拿到了一个outer plan, 可以准备开始扫描inner plan返回的所有数据。
			 * ExecReScan就是调增inner plan的执行pos，从头开始扫描一遍。
			 * now rescan the inner plan
			 */
			ENL1_printf("rescanning inner plan");
			ExecReScan(innerPlan);
		}

		/*
		 * 我们已经拿到了outer tuple, 此时开始获取下一个inner tuple。
		 * we have an outerTuple, try to get the next inner tuple.
		 */
		ENL1_printf("getting new inner tuple");

		innerTupleSlot = ExecProcNode(innerPlan);
		econtext->ecxt_innertuple = innerTupleSlot;

		inner_tuple_num++;

		if (TupIsNull(innerTupleSlot))
		{
			ENL1_printf("no inner tuple, need new outer tuple");

			node->nl_NeedNewOuter = true;

            /*
             * 对left join和 anti join的特殊处理
             */
			if (!node->nl_MatchedOuter &&
				(node->js.jointype == JOIN_LEFT ||
				 node->js.jointype == JOIN_ANTI))
			{
				/*
				 * We are doing an outer join and there were no join matches
				 * for this outer tuple.  Generate a fake join tuple with
				 * nulls for the inner tuple, and return it if it passes the
				 * non-join quals.
				 */
				econtext->ecxt_innertuple = node->nl_NullInnerTupleSlot;

				ENL1_printf("testing qualification for outer-join tuple");

				if (otherqual == NULL || ExecQual(otherqual, econtext))
				{
					/*
					 * qualification was satisfied so we project and return
					 * the slot containing the result tuple using
					 * ExecProject().
					 */
					ENL1_printf("qualification succeeded, projecting tuple");

					return ExecProject(node->js.ps.ps_ProjInfo);
				}
				else
					InstrCountFiltered2(node, 1);
			}

			/*
			 * Otherwise just return to top of loop for a new outer tuple.
			 */
			continue;
		}

		/*
		 * 程度到这里，我们就已经获取了一个outer tuple和一个inner tuple。
		 * ExecQual(joinqual, econtext)就是用来判断是否满足join条件。
		 * joinqual保存着join条件信息，比如那个column=哪个column
		 * excontext里保存和
		 * at this point we have a new pair of inner and outer tuples so we
		 * test the inner and outer tuples to see if they satisfy the node's
		 * qualification.
		 *
		 * Only the joinquals determine MatchedOuter status, but all quals
		 * must pass to actually return the tuple.
		 */
		ENL1_printf("testing qualification");

		if (ExecQual(joinqual, econtext))
		{
			node->nl_MatchedOuter = true;

			/* In an antijoin, we never return a matched tuple */
			if (node->js.jointype == JOIN_ANTI)
			{
				node->nl_NeedNewOuter = true;
				continue;		/* return to top of loop */
			}

			/*
			 * If we only need to join to the first matching inner tuple, then
			 * consider returning this one, but after that continue with next
			 * outer tuple.
			 */
			if (node->js.single_match)
				node->nl_NeedNewOuter = true;

			if (otherqual == NULL || ExecQual(otherqual, econtext))
			{
				/*
				 * qualification was satisfied so we project and return the
				 * slot containing the result tuple using ExecProject().
				 */
				ENL1_printf("qualification succeeded, projecting tuple");

				return ExecProject(node->js.ps.ps_ProjInfo);
			}
			else
				InstrCountFiltered2(node, 1);
		}
		else
			InstrCountFiltered1(node, 1);

		/*
		 * Tuple fails qual, so free per-tuple memory and try again.
		 */
		ResetExprContext(econtext);

		ENL1_printf("qualification failed, looping");
	}
}






static TupleTableSlot *
ExecNestLoop(PlanState *pstate)
{
    NestLoopState *node = castNode(NestLoopState, pstate);
    NestLoop   *nl;
    PlanState  *innerPlan;
    PlanState  *outerPlan;
    TupleTableSlot *outerTupleSlot;
    TupleTableSlot *innerTupleSlot;
    TupleTableSlot *slot;
    ExprState  *joinqual;
    ExprState  *otherqual;
    ExprContext *econtext;
    ListCell   *lc;

    CHECK_FOR_INTERRUPTS();

    //LPCE
    Tuplestorestate *tuplestorestate;
    bool		forward;
    EState	   *estate;
    ScanDirection dir;
    bool		eof_tuplestore;

    eof_tuplestore = false;
    //dir = estate->es_direction;
    forward = ScanDirectionIsForward(dir);
    tuplestorestate = node->tuplestorestate;


    /*
     * get information from the node
     */
    ENL1_printf("getting info from node");

    nl = (NestLoop *) node->js.ps.plan;
    joinqual = node->js.joinqual;
    otherqual = node->js.ps.qual;
    outerPlan = outerPlanState(node);
    innerPlan = innerPlanState(node);
    econtext = node->js.ps.ps_ExprContext;


    /*
     * Reset per-tuple memory context to free any expression evaluation
     * storage allocated in the previous tuple cycle.
     */
    ResetExprContext(econtext);

    /*
     * Ok, everything is setup for the join so now loop until we return a
     * qualifying join tuple.
     */
    ENL1_printf("entering main loop");



    /* Author: LPCE LPCE
     * We block the outer path node, and store the tuples into tuplestore
     * */

    /*
     * If first time through, and we need a tuplestore, initialize it.
     */
    if (node->build_tuplestore && tuplestorestate == NULL)
    {
        tuplestorestate = tuplestore_begin_heap(true, false, work_mem);
        tuplestore_set_eflags(tuplestorestate, 2);
        if (2 & EXEC_FLAG_MARK)
        {
            /*
             * Allocate a second read pointer to serve as the mark. We know it
             * must have index 1, so needn't store that.
             */
            int			ptrno PG_USED_FOR_ASSERTS_ONLY;

            ptrno = tuplestore_alloc_read_pointer(tuplestorestate,
                                                  2);
            Assert(ptrno == 1);
        }
        node->tuplestorestate = tuplestorestate;
        node->build_tuplestore = false;
        node->get_outertuple = true;
        elog(INFO, "     ------> LPCE ExecNestLoop build up the tuplestore at node %ld ", node->js.ps.plan->plan_node_id);
    }


    /*
     * If first time through, read all tuples from outer plan and pass them to
     * tuplestore. Subsequent calls just fetch tuples from tuplesort.
     */

    if(node->get_outertuple && tuplestorestate != NULL) {
        for (;;) {
            outer_tuple_num++;
            outerTupleSlot = ExecProcNode(outerPlan);

            /* Author: LPCE LPCE. Learning cardinality for re-optimization.
             * Detect error and early end query
            * We check the real card of outer node (outer path of nested loop join node)
            * and trigger the re-optimization once detect large error.
            *
            * Once we detect the large error, we can set the child hash node as done work.
            * Nested loop join make materialization for tuples from outer path (the side with relatively
            * small number of tuples).
            * (Noted that the default implementation of PG is pipeline processing of nested loop join).
            * However, we modify it as blocked processing, which means the all tuples are collected and stored
            * in a tuplestore at once.
            * */
            if (TupIsNull(outerTupleSlot)) {
                //update the info of outer node of nested loop join
                outer_tuple_num = tuplestore_tuple_count(tuplestorestate);
                int outer_node_id = card_runLog[node->js.ps.plan->plan_node_id].outer_node_id;
                card_runLog[outer_node_id].done_subplan = true;
                card_runLog[outer_node_id].node_card = outer_tuple_num;

                if(LPCECheck && !LPCERerun){
                    if(outer_tuple_num < 1.0)
                        outer_tuple_num = 1.0;
                    if(card_runLog[outer_node_id].estimate_card < 1.0)
                        card_runLog[outer_node_id].estimate_card = 1.0;

                    //Large error is detected
                    //LPCE
                    if(node->js.ps.plan->plan_node_id >= 4 &&
                            (outer_tuple_num / card_runLog[outer_node_id].estimate_card> 50 || card_runLog[outer_node_id].estimate_card / outer_tuple_num > 50)){
                        elog(INFO, "     +++++++>++++++> LPCE ExecNestLoop Trigger Re-optimization Point: %d  ", node->js.ps.plan->plan_node_id);
                        LPCERerun    = true;

                        //update the info of outer node of nested loop join
                        card_runLog[outer_node_id].done_work = true;
                        return NULL;
                    }
                }
                break;
            }

            if(tuplestorestate)
                tuplestore_puttupleslot(tuplestorestate, outerTupleSlot);
        }

        tuplestore_rescan(tuplestorestate);

        elog(INFO, "     +++++++>++++++> LPCE ExecNestLoop insert tuple into tuplestore at node %ld %lf", node->js.ps.plan->plan_node_id, outer_tuple_num);

        //now we are ready to receive the inner tuple.
        node->get_outertuple = false;
        node->start_nljoin = true;
        outer_tuple_num = 0;
    }

    /*
     * Now we have materialize the outer tuple in tuplestore.
     * Ready to start nested loop join.
     */
    if(node->start_nljoin && node->tuplestorestate != NULL){
        for (;;) {
            /*
             * If we don't have an outer tuple, get the next one and reset the
             * inner scan.
             */
            if (node->nl_NeedNewOuter) {
                ENL1_printf("getting new outer tuple");

                slot = MakeSingleTupleTableSlot(outerPlan->ps_ResultTupleDesc, &TTSOpsMinimalTuple);
                //outerTupleSlot = MakeTupleTableSlot(outerPlan->ps_ResultTupleDesc, &TTSOpsMinimalTuple);
                if (tuplestore_gettupleslot(tuplestorestate, true, false, slot)){
                    outer_tuple_num++;
                    outerTupleSlot = slot;
                    if(max_inner_tuple < inner_tuple_num)
                        max_inner_tuple = inner_tuple_num;
                    //max_inner_tuple = max(max_inner_tuple, inner_tuple_num);
                    inner_tuple_num = 0;
                }else {
                    ExecDropSingleTupleTableSlot(slot);
                    //general cases, once the max_inner_tuple is > 1, which means the inner plan is
                    //already done work, since nested loop have scan the inner plan at least once.
                    if(max_inner_tuple - 1 > 0) {
                        //for nested loop join, the join is complete when the outer tuple is null
                        int inner_node_id = card_runLog[node->js.ps.plan->plan_node_id].inner_node_id;
                        card_runLog[inner_node_id].done_subplan = true;
                        if(card_runLog[inner_node_id].node_card < 1)
                            card_runLog[inner_node_id].node_card = max_inner_tuple;
                        elog(INFO, "     +++++++>++++++> +++++++>++++++> DEBUG DEBUG DEBUG DEBUG DEBUG DEBUG DEBUG");
                        elog(INFO, "     +++++++>++++++> nested inner_node_id: %d %lf %lf", inner_node_id, inner_tuple_num, max_inner_tuple);
                        elog(INFO, "     +++++++>++++++> +++++++>++++++> DEBUG DEBUG DEBUG DEBUG DEBUG DEBUG DEBUG");
                    }
                    //in case index scan, index only scan
                    if(inner_tuple_num == 1){
                        int inner_node_id = card_runLog[node->js.ps.plan->plan_node_id].inner_node_id;
                        if(node_style[inner_node_id] == 2 || node_style[inner_node_id] == 4) {
                            card_runLog[inner_node_id].done_subplan = true;
                            if (card_runLog[inner_node_id].node_card < 1)
                                card_runLog[inner_node_id].node_card = max_inner_tuple;
                            elog(INFO,
                                 "     +++++++>++++++> +++++++>++++++> DEBUG DEBUG DEBUG DEBUG DEBUG DEBUG DEBUG");
                            elog(INFO, "     +++++++>++++++> nested inner_node_id: %d %lf %lf", inner_node_id, inner_tuple_num, max_inner_tuple);
                            elog(INFO, "     +++++++>++++++> +++++++>++++++> DEBUG DEBUG DEBUG DEBUG DEBUG DEBUG DEBUG");
                        }
                    }
                    inner_tuple_num = 0;
                    max_inner_tuple = 0;
                    //node->tuplestorestate = NULL;
                    return NULL;
                }

                //print_slot(outerTupleSlot);
                outer_debugtup(outerTupleSlot, NULL);

                /*
                 * if there are no more outer tuples, then the join is complete..
                 */
                if (TupIsNull(outerTupleSlot)) {
                    ENL1_printf("no outer tuple, ending join");
                    ExecDropSingleTupleTableSlot(slot);
                    break;
                    return NULL;
                }


                ENL1_printf("saving new outer tuple information");
                econtext->ecxt_outertuple = outerTupleSlot;
                node->nl_NeedNewOuter = false;
                node->nl_MatchedOuter = false;

                /*
                 * fetch the values of any outer Vars that must be passed to the
                 * inner scan, and store them in the appropriate PARAM_EXEC slots.
                 */
                foreach(lc, nl->nestParams)
                {
                    NestLoopParam *nlp = (NestLoopParam *) lfirst(lc);
                    int paramno = nlp->paramno;
                    ParamExecData *prm;

                    prm = &(econtext->ecxt_param_exec_vals[paramno]);
                    /* Param value should be an OUTER_VAR var */
                    Assert(IsA(nlp->paramval, Var));
                    Assert(nlp->paramval->varno == OUTER_VAR);
                    Assert(nlp->paramval->varattno > 0);
                    prm->value = slot_getattr(outerTupleSlot,
                                              nlp->paramval->varattno,
                                              &(prm->isnull));
                    /* Flag parameter value as changed */
                    innerPlan->chgParam = bms_add_member(innerPlan->chgParam,
                                                         paramno);
                }

                /*
                 * now rescan the inner plan
                 */
                ENL1_printf("rescanning inner plan");
                ExecReScan(innerPlan);
            }

            /*
             * we have an outerTuple, try to get the next inner tuple.
             */
            ENL1_printf("getting new inner tuple");

            innerTupleSlot = ExecProcNode(innerPlan);
            econtext->ecxt_innertuple = innerTupleSlot;
            inner_tuple_num++;

            if (TupIsNull(innerTupleSlot))
            {
                ENL1_printf("no inner tuple, need new outer tuple");

                node->nl_NeedNewOuter = true;

                if (!node->nl_MatchedOuter &&
                    (node->js.jointype == JOIN_LEFT ||
                     node->js.jointype == JOIN_ANTI))
                {
                    /*
                     * We are doing an outer join and there were no join matches
                     * for this outer tuple.  Generate a fake join tuple with
                     * nulls for the inner tuple, and return it if it passes the
                     * non-join quals.
                     */
                    econtext->ecxt_innertuple = node->nl_NullInnerTupleSlot;

                    ENL1_printf("testing qualification for outer-join tuple");

                    if (otherqual == NULL || ExecQual(otherqual, econtext))
                    {
                        /*
                         * qualification was satisfied so we project and return
                         * the slot containing the result tuple using
                         * ExecProject().
                         */
                        ENL1_printf("qualification succeeded, projecting tuple");

                        return ExecProject(node->js.ps.ps_ProjInfo);
                    }
                    else
                        InstrCountFiltered2(node, 1);
                }

                /*
                 * Otherwise just return to top of loop for a new outer tuple.
                 */
                continue;
            }

            /*
             * at this point we have a new pair of inner and outer tuples so we
             * test the inner and outer tuples to see if they satisfy the node's
             * qualification.
             *
             * Only the joinquals determine MatchedOuter status, but all quals
             * must pass to actually return the tuple.
             */
            ENL1_printf("testing qualification");


            if (ExecQual(joinqual, econtext))
            {
                node->nl_MatchedOuter = true;

                /* In an antijoin, we never return a matched tuple */
                if (node->js.jointype == JOIN_ANTI)
                {
                    node->nl_NeedNewOuter = true;
                    continue;		/* return to top of loop */
                }

                /*
                 * If we only need to join to the first matching inner tuple, then
                 * consider returning this one, but after that continue with next
                 * outer tuple.
                 */
                if (node->js.single_match)
                    node->nl_NeedNewOuter = true;

                if (otherqual == NULL || ExecQual(otherqual, econtext))
                {
                    /*
                     * qualification was satisfied so we project and return the
                     * slot containing the result tuple using ExecProject().
                     */
                    ENL1_printf("qualification succeeded, projecting tuple");

                    return ExecProject(node->js.ps.ps_ProjInfo);
                }
                else
                    InstrCountFiltered2(node, 1);
            }
            else
                InstrCountFiltered1(node, 1);

            /*
             * Tuple fails qual, so free per-tuple memory and try again.
             */
            ResetExprContext(econtext);

            ENL1_printf("qualification failed, looping");
        }
    }

    return NULL;
}


static bool
outer_debugtup(TupleTableSlot *slot, DestReceiver *self)
{
    TupleDesc	typeinfo = slot->tts_tupleDescriptor;
    int			natts = typeinfo->natts;
    int			i;
    Datum		attr;
    char	   *value;
    bool		isnull;
    Oid			typoutput;
    bool		typisvarlena;


    for (i = 0; i < natts; ++i)
    {
        attr = slot_getattr(slot, i + 1, &isnull);
        if (isnull)
            continue;
        getTypeOutputInfo(TupleDescAttr(typeinfo, i)->atttypid,
                          &typoutput, &typisvarlena);

        value = OidOutputFunctionCall(typoutput, attr);

        //printatt((unsigned) i + 1, TupleDescAttr(typeinfo, i), value);
    }
    //printf("\t----\n");

    return true;
}


/* ----------------------------------------------------------------
 *		ExecInitNestLoop
 * ----------------------------------------------------------------
 */
NestLoopState *
ExecInitNestLoop(NestLoop *node, EState *estate, int eflags)
{
	NestLoopState *nlstate;

	/* check for unsupported flags */
	Assert(!(eflags & (EXEC_FLAG_BACKWARD | EXEC_FLAG_MARK)));

	NL1_printf("ExecInitNestLoop: %s\n",
			   "initializing node");

	/*
	 * create state structure
	 */
	nlstate = makeNode(NestLoopState);
	nlstate->js.ps.plan = (Plan *) node;
	nlstate->js.ps.state = estate;
	nlstate->js.ps.ExecProcNode = ExecNestLoop;

    elog(INFO, "     ------> LPCE ExecInitNestLoop at node %ld estimate tuples %.0f", nlstate->js.ps.plan->plan_node_id, nlstate->js.ps.plan->plan_rows);
    //elog(INFO, "     ------> LPCE ExecInitNestLoop###################inner %ld  outer %ld", nlstate->js.ps.plan->inner_relids, nlstate->js.ps.plan->outer_relids);
	/*
	 * Miscellaneous initialization
	 *
	 * create expression context for node
	 */
	ExecAssignExprContext(estate, &nlstate->js.ps);

	/*
	 * initialize child nodes
	 *
	 * If we have no parameters to pass into the inner rel from the outer,
	 * tell the inner child that cheap rescans would be good.  If we do have
	 * such parameters, then there is no point in REWIND support at all in the
	 * inner child, because it will always be rescanned with fresh parameter
	 * values.
	 */
	outerPlanState(nlstate) = ExecInitNode(outerPlan(node), estate, eflags);
	if (node->nestParams == NIL)
		eflags |= EXEC_FLAG_REWIND;
	else
		eflags &= ~EXEC_FLAG_REWIND;
	innerPlanState(nlstate) = ExecInitNode(innerPlan(node), estate, eflags);

    //LPCE
    //record the initial cardinality estimation at the node
    int node_id = nlstate->js.ps.plan->plan_node_id;
    card_runLog[node_id].estimate_card = nlstate->js.ps.plan->plan_rows;
    node_style[node_id]              = 9; //nested loop join

    card_runLog[node_id].inner_node_id = innerPlan(node)->plan_node_id;
    card_runLog[node_id].outer_node_id = outerPlan(node)->plan_node_id;

    card_runLog[node_id].inner_relids = nlstate->js.ps.plan->inner_relids;
    card_runLog[node_id].outer_relids = nlstate->js.ps.plan->outer_relids;



	/*
	 * Initialize result slot, type and projection.
	 */
	ExecInitResultTupleSlotTL(&nlstate->js.ps, &TTSOpsVirtual);
	ExecAssignProjectionInfo(&nlstate->js.ps, NULL);
    //LPCE
	nlstate->tuplestorestate = NULL;

	/*
	 * initialize child expressions
	 */

	nlstate->js.ps.qual =
		ExecInitQual(node->join.plan.qual, (PlanState *) nlstate);
	nlstate->js.jointype = node->join.jointype;
	nlstate->js.joinqual =
		ExecInitQual(node->join.joinqual, (PlanState *) nlstate);


	/*
	 * detect whether we need only consider the first matching inner tuple
	 */
	nlstate->js.single_match = (node->join.inner_unique ||
								node->join.jointype == JOIN_SEMI);

	/* set up null tuples for outer joins, if needed */
	switch (node->join.jointype)
	{
		case JOIN_INNER:
		case JOIN_SEMI:
			break;
		case JOIN_LEFT:
		case JOIN_ANTI:
			nlstate->nl_NullInnerTupleSlot =
				ExecInitNullTupleSlot(estate,
									  ExecGetResultType(innerPlanState(nlstate)),
									  &TTSOpsVirtual);
			break;
		default:
			elog(ERROR, "unrecognized join type: %d",
				 (int) node->join.jointype);
	}

	/*
	 * finally, wipe the current outer tuple clean.
	 */
	nlstate->nl_NeedNewOuter = true;
	nlstate->nl_MatchedOuter = false;

	//LPCE
	nlstate->build_tuplestore = true;
    nlstate->get_outertuple   = false;
    nlstate->start_nljoin     = false;
    outer_tuple_num = 0;
    inner_tuple_num = 0;

	NL1_printf("ExecInitNestLoop: %s\n",
			   "node initialized");

	return nlstate;
}

/* ----------------------------------------------------------------
 *		ExecEndNestLoop
 *
 *		closes down scans and frees allocated storage
 * ----------------------------------------------------------------
 */
void
ExecEndNestLoop(NestLoopState *node)
{
	NL1_printf("ExecEndNestLoop: %s\n",
			   "ending node processing");

	/*
	 * Free the exprcontext
	 */
	ExecFreeExprContext(&node->js.ps);

    elog(INFO, "     ------>------> LPCE ExecEndNestLoop");

	/*
	 * clean out the tuple table
	 */
	ExecClearTuple(node->js.ps.ps_ResultTupleSlot);


    /*
     * Release tuplestore resources
     */
    if (node->tuplestorestate != NULL)
        tuplestore_end(node->tuplestorestate);
    node->tuplestorestate = NULL;


	/*
	 * close down subplans
	 */
	ExecEndNode(outerPlanState(node));
	ExecEndNode(innerPlanState(node));

	NL1_printf("ExecEndNestLoop: %s\n",
			   "node processing ended");
}

/* ----------------------------------------------------------------
 *		ExecReScanNestLoop
 * ----------------------------------------------------------------
 */
void
ExecReScanNestLoop(NestLoopState *node)
{
	PlanState  *outerPlan = outerPlanState(node);

	/*
	 * If outerPlan->chgParam is not null then plan will be automatically
	 * re-scanned by first ExecProcNode.
	 */
	if (outerPlan->chgParam == NULL)
		ExecReScan(outerPlan);

	/*
	 * innerPlan is re-scanned for each new outer tuple and MUST NOT be
	 * re-scanned from here or you'll get troubles from inner index scans when
	 * outer Vars are used as run-time keys...
	 */

	node->nl_NeedNewOuter = true;
	node->nl_MatchedOuter = false;
}
