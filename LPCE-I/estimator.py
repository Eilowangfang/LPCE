import torch
from lpce.sru import *
from itertools import combinations
from encode import *
from caller import *


def paraser(query):

    input_dim = 256 # hidden unit of embed module
    mem_dim = 1024 #
    hidden_dim = 1024 #
    feature_dim = 70
    operat_dim = 4
    tb_dim = 11
    filter_dim = 18
    join_dim = 37
    cuda_use = False
    GPU_no = 1
    min_label = 1.2
    max_label = 256668117

    torch.cuda.set_device(GPU_no)
    model = SRU(cuda_use, feature_dim, input_dim, mem_dim, hidden_dim)
    path = os.path.join(os.path.abspath('.'), "model/example_model.pth")
    model.load_state_dict(torch.load(path, map_location='cpu'))
    caller = Caller(cuda_use, model, min_label, max_label, operat_dim, tb_dim, filter_dim, join_dim)

    start_time = time.time()


    query = rewrite_query(query)
    #print(query)
    tb_str=query[query.index("FROM")+5:query.index("WHERE")]
    tb_list=list(tb_str.split(","))
    tb_list=gettable(tb_list)
    pred_str = query[query.index("WHERE")+5:query.index(";")]
    plist = list(pred_str.split("AND"))
    join_num = isjoinnum(plist)
    join_list=plist[0:join_num]
    join_str=""
    join_str=join_str.join(join_list)
    join_att=getJoinAtt(join_list, tb_list)
    filter_list=plist[join_num:]
    if len(join_list)+1 != len(tb_list):
        print("join number does not match table num")
    if len(join_att) != len(tb_list):
        print("join attributes does not match table num")

    clause = getFilter(tb_list,filter_list)

    #print("Involved tables:", tb_list)
    #print("Filters: ", clause)
    #print("Join content: ", join_str)
    #print("Join att: ", join_att)
    #DP enumeration
    #predicate
    memRel=[] #memory pool for relation
    memCard=[] #memory pool for cardinality
    memCheapestPath=[] #memory pool for cheapest relation combination
    memPathWord=[] #memory pool for printing
    memState= [] #memory pool for hidden state of LPCE
    #print("Level 1")
    relLevel1 = getRelatLevel(1, clause) #level1
    relLevel1_Vec, relLevel1_Path = getBaseVec(clause)
    memRel.append(relLevel1)
    memCheapestPath.append(relLevel1_Path)
    memPathWord.append(relLevel1_Vec)
    #call LPCE
    relLevel1_Card, relLevel1_Hstate, relLevel1_Feat = call_LPCE_AtLevel1(relLevel1_Vec, caller)
    relLevel1_Card = doublecheck_baserel(relLevel1_Vec, relLevel1_Card) #adjust prediction
    memCard.append(relLevel1_Card)
    memState.append(relLevel1_Hstate)
    #
    #print("Possible joining relations: ", memRel)
    #print("mem card: ", memCard)
    #print("mem cheapestpath: ", memCheapestPath)
    #print("mem pathword: ", memPathWord)
    #print(memState)


    # #level2
    #get feature vector and right/left children state
    #print("\nLevel 2")
    relL2 = getRelatLevel(2, clause)
    relL2 = remove_IllegalJoin(relL2, join_att)
    l2_Vec, l2_LChildState, l2_RChildState, l2_Path, l2_Pathword = getJoinVecLevel2(relL2, clause, join_att, memState) #level2
    l2_Card, l2_State = call_LPCE_atlevel2(l2_Vec, caller, l2_LChildState, l2_RChildState)
    memRel.append(relL2)
    memCheapestPath.append(l2_Path) #cheapest path for two relations at level 2
    memPathWord.append(l2_Pathword)
    memCard.append(l2_Card)
    memState.append(l2_State)

    #print("Possible joining relations: ", relL2)
    #print("mem card: ", l2_Card)
    #print("mem cheapestpath: ", l2_Path)
    #print("mem pathword: ", l2_Pathword)


    for i in range(3,len(clause)+1):
        #print("Level " + str(i))
        relLeveln = getRelatLevel(i, clause)
        relLeveln = remove_IllegalJoin(relLeveln, join_att)
        #print("Possible joining relations: ", relLeveln)
        ln_Vec, ln_LChildState, ln_RChildState, ln_Path, ln_Pathword = getJoinVecLeveln(i, relLeveln, clause, tb_list, join_att, memRel, memCheapestPath, memCard, memState, memPathWord)
        ln_Card, ln_State = call_LPCE_atleveln(ln_Vec, caller, ln_LChildState, ln_RChildState, i)
        memRel.append(relLeveln)
        memCheapestPath.append(ln_Path) #cheapest path for two relations at level 3
        memPathWord.append(ln_Pathword)
        memCard.append(ln_Card)
        memState.append(ln_State)


    #for i in range(len(memCard)):
    #    print("Total card: ", len(memCard[i]))

    predict_card = []
    for i in range(len(memCard)):
        for j in range(len(memCard[i])):
            predict_card.append(int(memCard[i][j]))

    end_time = time.time()
    print("Number of cardinalities to estimate:", len(predict_card))
    print("Model inference time: ", (end_time - start_time)*1000.0, "ms")

    print("Learned estimator outputs cardinality:")
    print(predict_card)



def doublecheck_baserel(relLeve1_Node, relLeve1_Card):
    operts, opertDic = getOpeators()
    filterCols = getFilterCol()
    tbDic, tbShortDic = getTableDic()
    tbCards = getTableCard()

    for n in range(len(relLeve1_Node)):
        node = relLeve1_Node[n]
        colnum = 0
        for i in filterCols:
            if node.count(i) > 0:
                colnum += 1
        oper = []
        for i in operts:
            if node.count(i)>0:
                oper.append(i)

        tb = ""
        for i in tbShortDic:
            if node.count(i) > 0:
                tb = i

        if colnum == 0 and len(oper) == 0:
            relLeve1_Card[n] = tbCards[tb]

    return relLeve1_Card










def remove_IllegalJoin(rels, join_att):
    legalrels=[]
    for i in range(len(rels)):
        legalkwjoin = True
        legalperjoin = True
        joins = ""
        for j in range(len(rels[i])):
            tbno = rels[i][j]
            for z in range(len(join_att[tbno])):
                joins += join_att[tbno][z]
                joins += " "

        if joins.count("kw.id") > 0:
            if joins.count("mk.keyword_id") > 0:
                legalkwjoin = True
            else:
                legalkwjoin = False

        if joins.count("pi.person_id") > 0:
            if joins.count("ci.person_id") > 0:
                legalperjoin = True
            else:
                legalperjoin = False

        if legalkwjoin == True and legalperjoin == True:
            legalrels.append(rels[i])
    return legalrels








def call_LPCE_AtLevel1(level_vector, caller):
    hidden=[]
    feat_batch = []
    for i in range(len(level_vector)):
        feature = encodingFeat(level_vector[i], 1)
        hidden.append(random.uniform(0,1.0))
        feat_batch.append(feature)
        #print(level_vector[i], feature, len(feature))
    card, hidden = caller.testbase(feat_batch)
    return card, hidden, feat_batch


def call_LPCE_atlevel2(level_vector, caller, left_hidden, right_hidden):
    feat_batch = []
    for i in range(len(level_vector)):
        feature = encodingFeat(level_vector[i], 2)
        feat_batch.append(feature)
    card, hidden = caller.testjoin(feat_batch, left_hidden, right_hidden)
    return card, hidden


def call_LPCE_atleveln(level_vector, caller, left_hidden, right_hidden, level):
    feat_batch = []
    for i in range(len(level_vector)):
        feature=encodingFeat(level_vector[i], level)
        feat_batch.append(feature)
    card, hidden = caller.testjoin(feat_batch, left_hidden, right_hidden)
    return card, hidden


#join relation
def getJoinVecLevel2(rel_level2, clause, join_att, mem_state):
    join_vec=[]
    rightchild_state=[]
    leftchild_state=[]
    path=[]
    pathword=[]

    for i in range(len(rel_level2)):
        leftchild_state.append(mem_state[0][rel_level2[i][0]])
        rightchild_state.append(mem_state[0][rel_level2[i][1]])
        joinnode = findJoinRelatL2(rel_level2[i],join_att,clause)
        join_vec.append(joinnode)

        path.append(rel_level2[i])
        tmp=[]
        tmp.append(clause[rel_level2[i][0]])
        tmp.append(clause[rel_level2[i][1]])
        tmp.append(joinnode)
        pathword.append(tmp)
    return join_vec, leftchild_state, rightchild_state, path, pathword




def getJoinVecLeveln(level, rel_leveln, clause, tblist, join_att, mem_rel, mem_cheapestpath, mem_card, mem_state, mem_pathword):
    joinvec=[]
    lchildstate=[]
    rchildstate=[]
    cheapest_path=[]
    cheapest_pathword=[]
    joinsDic = getJoinFeatDic()
    for i in range(len(rel_leveln)):
        cob = list(combinations(rel_leveln[i], level-1))
        cob = remove_IllegalJoin(cob, join_att)
        #print("  \n")
        #print("  rel_leveln[i]: ", rel_leveln[i])
        #print("  cob: ", cob)

        #left deep tree
        cheap_leftrel, cheap_leftrelstate, cheap_leftrelword = leftDeep_FindCheapest_n(cob, level, mem_rel, mem_cheapestpath, mem_card, mem_state, mem_pathword)
        #print("  cheap_leftrel: ", cheap_leftrel)
        b = [y for y in (rel_leveln[i] + cheap_leftrel) if y not in cheap_leftrel]

        lchildstate.append(cheap_leftrelstate)
        rchildstate.append(mem_state[0][b[0]])
        cheapestrel = cheap_leftrel+(b[0],)
        cheapest_path.append(cheapestrel)

        joinnode = getjoinnodevec(cheap_leftrel, b[0], tblist, clause, join_att)
        pos = joinnode.find("=")
        l = joinnode[:pos]
        r = joinnode[pos+1:]
        for key in joinsDic.keys():
            if key.count(l) > 0 and key.count(r) > 0:
                joinnode = key
        joinvec.append(joinnode)
        #print("  joinnode: ", joinnode)

        tmp_pathword=[]
        tmp_pathword.append(cheap_leftrelword)
        tmp_pathword.append(mem_pathword[0][b[0]])
        tmp_pathword.append(joinnode)
        cheapest_pathword.append(tmp_pathword)

        #bushy tree to do
    return joinvec, lchildstate, rchildstate, cheapest_path, cheapest_pathword



def leftDeep_FindCheapest_n(rel_lowerlevel, level, mem_rel, mem_cheapestrel, mem_card, mem_state, mem_pathword):
    min = sys.maxsize
    cheapestrel = []
    cheapestrel_state = []
    cheapestrel_word = []
    leftlevel = level-2
    for i in range(len(rel_lowerlevel)):
        for j in range(len(mem_rel[leftlevel])):
            if mem_rel[leftlevel][j] == rel_lowerlevel[i]:
                if mem_card[leftlevel][j] < min:
                    min = mem_card[leftlevel][j]
                    cheapestrel = mem_cheapestrel[leftlevel][j]
                    cheapestrel_state = mem_state[leftlevel][j]
                    cheapestrel_word = mem_pathword[leftlevel][j]
    return cheapestrel, cheapestrel_state, cheapestrel_word





def getjoinnodevec(deepleft_rel, right_rel, tblist, clause, join_att):
    joinnode = joinrelation(deepleft_rel, right_rel, tblist, clause, join_att)
    return joinnode


def joinrelation(deepleft_rel, right_rel, tblist, clause, join_att):

    joinnode=""
    #print("right node", join_att[right_rel])
    #for i in range(len(deepleft_rel)):
        #print("for join left node", join_att[deepleft_rel[i]])

    #left deep tree
    #right_rel is just on number
    if len(join_att[right_rel]) == 1:
        firstcol = join_att[right_rel][0]
        if firstcol.count("keyword_id") > 0 or firstcol.count("kw.id") > 0:
            for i in range(len(deepleft_rel)):
                for j in range(len(join_att[deepleft_rel[i]])):
                    if join_att[deepleft_rel[i]][j].count("keyword_id") > 0 or join_att[deepleft_rel[i]][j].count(
                                "kw.id") > 0:
                        return firstcol + "=" + join_att[deepleft_rel[i]][j]

        if firstcol.count("person_id") > 0:
            for i in range(len(deepleft_rel)):
                for j in range(len(join_att[deepleft_rel[i]])):
                     if join_att[deepleft_rel[i]][j].count("person_id") > 0:
                        return firstcol + "=" + join_att[deepleft_rel[i]][j]

        if firstcol.count("movie_id") > 0:
              for i in range(len(deepleft_rel)):
                for j in range(len(join_att[deepleft_rel[i]])):
                    if join_att[deepleft_rel[i]][j].count("t.id") > 0:
                         return firstcol + "=" + join_att[deepleft_rel[i]][j]
                for i in range(len(deepleft_rel)):
                    revs = len(deepleft_rel) - 1 - i
                    for j in range(len(join_att[deepleft_rel[revs]])):
                        if join_att[deepleft_rel[revs]][j].count("movie_id") > 0:
                            return firstcol + "=" + join_att[deepleft_rel[revs]][j]

                for i in range(len(deepleft_rel)):
                    for j in range(len(join_att[deepleft_rel[i]])):
                        if join_att[deepleft_rel[i]][j].count("movie_id") > 0:
                            return firstcol + "=" + join_att[deepleft_rel[i]][j]

        if firstcol.count("t.id") > 0:
            for i in range(len(deepleft_rel)):
                 revs = len(deepleft_rel) - 1 - i
                 for j in range(len(join_att[deepleft_rel[revs]])):
                      if join_att[deepleft_rel[revs]][j].count("movie_id") > 0:
                         return firstcol + "=" + join_att[deepleft_rel[revs]][j]



    if len(join_att[right_rel]) > 1:
        firstcol = join_att[right_rel][0]
        secdcol = join_att[right_rel][1]

        allleftcol = ""
        for i in range(len(deepleft_rel)):
            for j in range(len(join_att[deepleft_rel[i]])):
                allleftcol += join_att[deepleft_rel[i]][j]
                allleftcol += " "

        if firstcol.count("keyword_id") > 0 or secdcol.count("keyword_id") > 0 :
            if allleftcol.count("kw.id") > 0:
                return "mk.keyword_id=kw.id"

        if firstcol.count("kw.id") > 0 or secdcol.count("kw.id") > 0 :
            if allleftcol.count("keyword_id") > 0:
                return "mk.keyword_id=kw.id"

        if firstcol.count("person_id") > 0:
            if allleftcol.count("person_id") > 0:
                for i in range(len(deepleft_rel)):
                    for j in range(len(join_att[deepleft_rel[i]])):
                        if join_att[deepleft_rel[i]][j].count("person_id") > 0:
                            return firstcol+"="+join_att[deepleft_rel[i]][j]

        if secdcol.count("person_id") > 0:
            if allleftcol.count("person_id") > 0:
                for i in range(len(deepleft_rel)):
                    for j in range(len(join_att[deepleft_rel[i]])):
                        if join_att[deepleft_rel[i]][j].count("person_id") > 0:
                            return secdcol+"="+join_att[deepleft_rel[i]][j]

        if firstcol.count("movie_id") > 0:
            if allleftcol.count("t.id") > 0:
                return firstcol+"=t.id"
            if allleftcol.count("movie_id") > 0:
                for i in range(len(deepleft_rel)):
                    revs = len(deepleft_rel) - 1 - i
                    for j in range(len(join_att[deepleft_rel[revs]])):
                        if join_att[deepleft_rel[revs]][j].count("movie_id") > 0:
                            return firstcol + "=" + join_att[deepleft_rel[revs]][j]

        if secdcol.count("movie_id") > 0:
            if allleftcol.count("t.id") > 0:
                return secdcol+"=t.id"
            if allleftcol.count("movie_id") > 0:
                for i in range(len(deepleft_rel)):
                    revs = len(deepleft_rel) - 1 - i
                    for j in range(len(join_att[deepleft_rel[revs]])):
                        if join_att[deepleft_rel[revs]][j].count("movie_id") > 0:
                            return secdcol + "=" + join_att[deepleft_rel[revs]][j]

        return join_att[right_rel][0] + "=" + join_att[len(deepleft_rel)-1][0]


        # find cheapest path
def leftdeep_findchepest(rel_lowerlevel, lowlevel, mem_rel, mem_cheapestrel, mem_card, mem_state, mem_pathword):
    min = sys.maxsize
    cheapestrel=[]
    cheapestrel_state=[]
    cheapestrel_word=""
    leftlevel = lowlevel-1
    for i in range(len(rel_lowerlevel)):
        for j in range(len(mem_rel[leftlevel])):
            if mem_rel[leftlevel][j] == rel_lowerlevel[i]:
                #print(mem_rel[leftlevel][j], mem_card[leftlevel][j])
                if mem_card[leftlevel][j] < min:
                    min = mem_card[leftlevel][j]
                    cheapestrel = mem_cheapestrel[leftlevel][j]
                    cheapestrel_state = mem_state[leftlevel][j]
                    cheapestrel_word = mem_pathword[leftlevel][j]
    return cheapestrel, cheapestrel_state, cheapestrel_word



def findJoinRelatL2(comb, joinAtt, clause):
    joinsDic = getJoinFeatDic()

    firstJoinAtts = joinAtt[comb[0]]
    secondJoinAtts = joinAtt[comb[1]]

    join = ""
    for key in joinsDic.keys():
        for i in firstJoinAtts:
            for j in secondJoinAtts:
                if key.count(i) > 0 and key.count(j) > 0:
                    join = key
    if len(join) == 0:
        print("ERROR: wrong join")
    return join






#[1,2,3,4] =>[(1,2), (1,3), (1,4), (2,3)...]
def getRelatLevel(level, clause):
    emu = []
    for n in range(len(clause)):
        emu.append(n)
    comb = list(combinations(emu, level))
    return comb

#base relation feature
#[1,2,3,4] =>[' mc.company_id > 10 ', ' t.kind_id > 4 '...]
def getBaseVec(clause):
    vector=[]
    relno=[]
    for i in range(len(clause)):
        vector.append(clause[i])
        relno.append(i)
    return vector, relno



def getJoinAtt(joinList, tbList):
    joinAtt = []
    joinCols = getJoincol()

    for i in joinList:
        for j in joinCols:
            if i.count(j) > 0 and j not in joinAtt:
                joinAtt.append(j)

    #reorder accroding to table order
    orderJoinAtt = []
    for i in tbList:
        tbJoinAtt = []
        for j in joinAtt:
            if j.count(i) > 0:
                tbJoinAtt.append(j)
        orderJoinAtt.append(tbJoinAtt)
    return orderJoinAtt



def gettable(tbList):
    tbDic, tbShortDic = getTableDic()
    l=[]
    for tb in tbList:
        for j in range(len(tbDic)):
            if tb.count(tbDic[j])>0:
                l.append(tbShortDic[j])
    return l






def getFilter(tbList,filterList):

    filterCols = getFilterCol()
    clause = []
    no = 0
    for tb in tbList:
        first = True
        found = False
        for f in filterList:
            if f.count(tb)>0:
                found = True
                if first:
                    clause.append(f)
                    first = False
                else:
                    clause[no] += f
        if found == False:
            clause.append(tb)
        no += 1

    return clause



def isjoinnum(pList):
    tbDic, tbShortDic = getTableDic()
    num = 0
    for p in pList:
        occ = 0
        for tb in tbShortDic:
            if p.count(tb) > 0:
                occ += 1
        if occ > 1:
            num += 1
    return num


def rewrite_query(query):
    nqur=query
    if nqur.count("keyword k") > 0:
        print("--------------")
        nqur = nqur.replace('keyword k','keyword kw')
        if nqur.count(" k.id=") > 0:
            nqur = nqur.replace(' k.id=',' kw.id=')
        if nqur.count("=k.id ") > 0:
            nqur = nqur.replace('=k.id ','=kw.id ')
        if nqur.count("k.keyword ") > 0:
            nqur = nqur.replace('k.keyword ','kw.keyword ')
        if nqur.count(" k.keyword") > 0:
            nqur = nqur.replace(' k.keyword',' kw.keyword')

    if nqur.count("aka_title at") > 0:
        nqur = nqur.replace('aka_title at','aka_title ati')
        if nqur.count("at.") > 0:
            nqur = nqur.replace('at.','ati.')
    return nqur



if __name__ == '__main__':
    #
    #query = "SELECT COUNT(*) FROM title t,movie_companies mc,cast_info ci,movie_info mi,movie_info_idx mi_idx,movie_keyword mk,keyword k,aka_title at,complete_cast cc WHERE t.id=mc.movie_id AND t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND t.id=mk.movie_id AND mk.keyword_id=k.id AND t.id=at.movie_id AND t.id=cc.movie_id AND mc.id<1965148 AND ci.person_id>3063162 AND mi.info_type_id=3 AND mi_idx.id>1335393 AND k.keyword>85543 AND at.production_year<1924 AND cc.status_id=3;"
    #query = "SELECT COUNT(*) FROM title t,movie_companies mc,cast_info ci,movie_info mi,movie_info_idx mi_idx,movie_keyword mk,keyword k WHERE t.id=mc.movie_id AND t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND t.id=mk.movie_id AND mk.keyword_id=k.id AND t.production_year<1905 AND mc.id<1572602 AND ci.role_id=8 AND mi.info_type_id=42 AND mi_idx.id<1264333 AND mk.id>2493270 AND k.keyword<95670;"
    #query = "SELECT COUNT(*) FROM title t,movie_companies mc,cast_info ci,movie_info mi,movie_info_idx mi_idx,movie_keyword mk,keyword k WHERE t.id=mc.movie_id AND t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND t.id=mk.movie_id AND mk.keyword_id=k.id AND t.production_year>1895 AND mc.id>356335 AND ci.role_id=4 AND mi.id<434495 AND mi_idx.id>769638 AND k.keyword=1677;"
    #query = "SELECT COUNT(*) FROM title t,movie_companies mc,movie_info mi,movie_info_idx mi_idx,movie_keyword mk,keyword k,movie_link ml WHERE t.id=mc.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND t.id=mk.movie_id AND mk.keyword_id=k.id AND t.id=ml.movie_id AND t.production_year<1995 AND mc.id>967215 AND mi.info_type_id=42 AND mi_idx.id<1073108 AND mk.id<323877 AND ml.linked_movie_id<1142364;"
    query = str(sys.argv[1])
    #query = "SELECT COUNT(*) FROM title t,movie_companies mc,cast_info ci,movie_info mi,movie_info_idx mi_idx,movie_keyword mk,movie_link ml,aka_title at,complete_cast cc WHERE t.id=mc.movie_id AND t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND t.id=mk.movie_id AND t.id=ml.movie_id AND t.id=at.movie_id AND t.id=cc.movie_id AND mc.id<1028764 AND ci.person_id<459871 AND mi.info_type_id=86 AND mi_idx.id<98052 AND ml.linked_movie_id<2403289 AND at.production_year>1906 AND cc.status_id=4;"
    paraser(query)