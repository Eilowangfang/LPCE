def TableDic():
    tbDic=['cast_info ci','keyword kw','movie_companies mc','movie_info mi','movie_info_idx mi_idx','movie_keyword mk','movie_link ml','aka_title ati', 'complete_cast cc', 'title t']
    tbShortDic=['ci.', 'kw.', 'mc.','mi.','mi_idx.','mk.','ml.','ati.','cc.','t.']
    return tbDic, tbShortDic

def getJoincol():
    joinCol = ['t.id', 'mc.movie_id', 'ci.movie_id', 'mi.movie_id', 'mi_idx.movie_id', 'mk.movie_id', 'ml.movie_id',
               'kw.id','mk.keyword_id',
               'ati.movie_id', 'cc.movie_id']
    return joinCol



def getFilterCol():
    filterCol = ['t.production_year',
                 'mc.id',
                 'ci.role_id',
                 'ci.person_id',
                 'mi.id',
                 'mi.info_type_id',
                 'mi_idx.id',
                 'mk.id',
                 'kw.keyword',
                 'ml.linked_movie_id',
                 'ati.kind_id',
                 'ati.production_year',
                 'cc.subject_id',
                 'cc.status_id'
                 ]
    return filterCol



def getJoinFeatDic():
    joinFeatDic={
        't.id=mc.movie_id':            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        't.id=ci.movie_id':            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        't.id=mi.movie_id':            [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        't.id=mi_idx.movie_id':        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        't.id=mk.movie_id':            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        't.id=ml.movie_id':            [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        't.id=ati.movie_id':           [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        't.id=cc.movie_id':            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],

        'mc.movie_id=ci.movie_id':     [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'mc.movie_id=mi.movie_id':     [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'mc.movie_id=mi_idx.movie_id': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'mc.movie_id=mk.movie_id':     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'mc.movie_id=ml.movie_id':     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'mc.movie_id=ati.movie_id':    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'mc.movie_id=cc.movie_id':     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],

        'ci.movie_id=mi.movie_id':     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'ci.movie_id=mi_idx.movie_id': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'ci.movie_id=mk.movie_id':     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'ci.movie_id=ml.movie_id':     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'ci.movie_id=ati.movie_id':    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'ci.movie_id=cc.movie_id':     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],

        'mi.movie_id=mi_idx.movie_id': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'mi.movie_id=mk.movie_id':     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'mi.movie_id=ml.movie_id':     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'mi.movie_id=ati.movie_id':    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'mi.movie_id=cc.movie_id':     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],

        'mi_idx.movie_id=mk.movie_id': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'mi_idx.movie_id=ml.movie_id': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'mi_idx.movie_id=ati.movie_id':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        'mi_idx.movie_id=cc.movie_id': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],

        'mk.movie_id=ml.movie_id':     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        'mk.movie_id=ati.movie_id':    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        'mk.movie_id=cc.movie_id':     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],

        'ml.movie_id=ati.movie_id':  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        'ml.movie_id=cc.movie_id':   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],

        'ati.movie_id=cc.movie_id':  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],

        'mk.keyword_id=kw.id':         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        'blank':                       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    }
    return joinFeatDic




def Rewrite_query(query):
    nqur=query
    if nqur.count("keyword k") > 0:
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


#Return the number of tables, and table name
def GetTableInfo(query):
    query = Rewrite_query(query)
    tb_str = query[query.index("FROM")+5:query.index("WHERE")]
    tb_list = list(tb_str.split(","))
    tbDic, tbShortDic = TableDic()
    l = []
    for tb in tb_list:
        for j in range(len(tbDic)):
            if tb.count(tbDic[j])>0:
                l.append(tbShortDic[j])
    return l




#Return the join in the query
def GetJoinInfo(query, tbsInQuery):
    query = Rewrite_query(query)
    pred_str = query[query.index("WHERE")+5:query.index(";")]
    plist = list(pred_str.split("AND"))
    join_num = isjoinnum(plist)
    join_list = plist[0:join_num]
    join_att = getJoinAtt(join_list, tbsInQuery)
    return join_list, join_att




#Return the filter predicate in the query
def GetFilterInfo(query, tb_list):
    query = Rewrite_query(query)
    tb_str = query[query.index("FROM")+5:query.index("WHERE")]
    pred_str = query[query.index("WHERE")+5:query.index(";")]
    plist = list(pred_str.split("AND"))
    join_num = isjoinnum(plist)
    filter_list = plist[join_num:]
    clause = getFilter(tb_list,filter_list)
    return clause


def isjoinnum(pList):
    tbDic, tbShortDic = TableDic()
    num = 0
    for p in pList:
        occ = 0
        for tb in tbShortDic:
            if p.count(tb) > 0:
                occ += 1
        if occ > 1:
            num += 1
    return num


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




def getOpeators():
    operator=['<', '=',  '>']
    operator_dic={
        '<':[1, 0, 0],
        '=': [0, 1, 0],
        '>': [0, 0, 1],
        'blank': [0, 0, 0]
    }
    return operator, operator_dic


def getType():
    type_dic={
        'join':      [1, 0, 0, 0],
        'filter':    [0, 1, 0, 0],
        'scan':      [0, 0, 1, 0],
        'indexscan': [0, 0, 0, 1]
    }
    return type_dic


def getTableFeatDic():
    tableFeatDic ={
        'mi.':     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'mi_idx.': [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'ci.':     [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        't.':      [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        'mk.':     [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        'mc.':     [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        'pi.':     [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        'kw.':     [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        'ml.':     [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        'ati.':    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        'cc.':     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        'blank':   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    return tableFeatDic


def getFilterColDomain():
    FilterColDomain ={
        't.production_year':  [1880.0,2019.0],
        'mc.id':              [1.0,2609129.0],
        'ci.role_id':         [1.0, 11.0],
        'ci.person_id':       [1.0, 4061926.0],
        'mi.id':              [1.0, 14835720.0],
        'mi.info_type_id':    [1.0, 110.0],
        'mi_idx.id':          [1.0, 1380035.0],
        'mk.id':              [1.0, 4523930.0],
        'kw.keyword':         [1.0, 134169.0],
        'ml.linked_movie_id':  [284.0, 2524994.0],
        'ati.kind_id':         [1.0, 7.0],
        'ati.production_year': [1888.0, 2016.0],
        'cc.subject_id':       [1.0, 2.0],
        'cc.status_id':        [3.0, 4.0]
    }
    return FilterColDomain



def getFilterFeatDic():
    FilterFeatDic ={
        't.production_year':   [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'mc.id':               [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'ci.role_id':          [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'ci.person_id':        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'mi.id':               [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'mi.info_type_id':     [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        'mi_idx.id':           [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        'mk.id':               [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        'kw.keyword':          [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        'ml.linked_movie_id':  [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        'ati.kind_id':         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        'ati.production_year': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        'cc.subject_id':       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        'cc.status_id':        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        'blank':               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    }
    return FilterFeatDic


def getTableCard():
    tbCard = {
        'ci.': 36244344.0,
        'kw.': 134170.0,
        'mc.': 2609129.0,
        'mi.': 14835720.0,
        'mi_idx.': 1380035.0,
        'mk.': 4523930.0,
        'ml.': 59994.0,
        'ati.': 361472.0,
        'cc.': 135086.0,
        't.': 2528312.0
    }
    return tbCard