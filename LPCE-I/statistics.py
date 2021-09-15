def getalltable():
    tb_name=['movie_info mi','movie_info_idx mi_idx','cast_info ci','title t','movie_keyword mk','movie_companies mc', 'person_info pi', 'cast_info ci', 'keyword kw']
    tb_abbname=['mi.', 'mi_idx.', 'ci.','t.','mk.','mc.', 'pi.', 'ci.', 'kw.']
    return tb_name, tb_abbname

def getalljoin():
    join_dic={'t.id=mc.movie_id':          [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              't.id=ci.movie_id':          [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              't.id=mi.movie_id':          [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              't.id=mi_idx.movie_id':      [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              't.id=mk.movie_id':          [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              't.id=ml.movie_id':          [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'mc.movie_id=ci.movie_id':     [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'mc.movie_id=mi.movie_id':     [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'mc.movie_id=mi_idx.movie_id': [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'mc.movie_id=mk.movie_id':     [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'mc.movie_id=ml.movie_id':     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'ci.movie_id=mi.movie_id':     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'ci.movie_id=mi_idx.movie_id': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'ci.movie_id=mk.movie_id':     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'ci.movie_id=ml.movie_id':     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            'ci.person_id=pi.person_id':   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
            'mi.movie_id=mi_idx.movie_id': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            'mi.movie_id=mk.movie_id':     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            'mi.movie_id=ml.movie_id':     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
            'mi_idx.movie_id=mk.movie_id': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
            'mi_idx.movie_id=ml.movie_id': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
            'mk.movie_id=ml.movie_id':           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
            'mk.keyword_id=kw.id':         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
              'blank':                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    }
    return join_dic


def getallcolumns():
    allcolumns = ['t.id', 't.kind_id',
                  't.production_year',
                  'mc.company_id',
                  'mc.movie_id',
                  'mc.company_type_id',
                  'ci.movie_id',
                  'ci.person_id',
                  'ci.role_id',
                  'mi.movie_id',
                  'mi.info_type_id',
                  'mi_idx.movie_id',
                  'mi_idx.info_type_id',
                  'mk.id',
                  'mk.movie_id',
                  'mk.keyword_id',
                  'kw.id',
                  'kw.keyword',
                  'pi.person_id',
                  'pi.info_type_id',
                  'ml.movie_id'
    ]
    col_dic={'t.id':               [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             't.kind_id':          [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             't.production_year':  [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             'mc.company_id':      [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             'mc.movie_id':        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             'mc.company_type_id': [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             'ci.movie_id':        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             'ci.person_id':       [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             'ci.role_id':         [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             'mi.movie_id':        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             'mi.info_type_id':    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             'mi_idx.movie_id':    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
             'mi_idx.info_type_id':[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
             'mk.id':              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
             'mk.movie_id':        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
             'mk.keyword_id':      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
             'kw.id':              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
             'kw.keyword':         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
             'pi.person_id':       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
             'pi.info_type_id':    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
             'ml.movie_id':        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
             'blank':              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
             }
    return allcolumns, col_dic


def getcolumnstatis():
    columns_domain={'t.id':    [1.0,2528312.0],
                    't.kind_id':          [1.0,7.0],
                    't.production_year':  [1880.0,2019.0],

                    'mc.company_id':      [1.0,234997.0],
                    'mc.movie_id':        [2.0,2525745.0],
                    'mc.company_type_id': [1.0,2.0],

                    'ci.movie_id':        [1.0,2525975.0],
                    'ci.person_id':       [1.0,4061926.0],
                    'ci.role_id':         [1.0,11.0],

                    'mi.movie_id':        [1.0,2526430.0],
                    'mi.info_type_id':    [1.0, 110.0],

                    'mi_idx.movie_id':    [2.0, 2525793.0],
                    'mi_idx.info_type_id':[99.0, 113.0],

                    'mk.id':              [1,4523930],
                    'mk.movie_id':        [2.0, 2525971.0],
                    'mk.keyword_id':      [1.0, 134170.0],

                    'kw.id':        [1.0, 134170],
                    'kw.keyword':      [1.0, 134169.0],

                    'pi.person_id':        [4.0, 4167491.0],
                    'pi.info_type_id':      [15.0, 39.0],

                    'ml.movie_id':        [2, 186175]
                    }

    columns_card ={'t.id':    2528312,
                    't.kind_id':          2528312,
                    't.production_year':  2528312,

                    'mc.company_id':      2609129,
                    'mc.movie_id':        2609129,
                    'mc.company_type_id': 2609129,

                    'ci.movie_id':        36244344,
                    'ci.person_id':       36244344,
                    'ci.role_id':         36244344,

                    'mi.movie_id':        14835720,
                    'mi.info_type_id':    14835720,

                    'mi_idx.movie_id':    1380035,
                    'mi_idx.info_type_id':1380035,

                    'mk.id':              4523930,
                    'mk.movie_id':        4523930,
                    'mk.keyword_id':      4523930,

                    'kw.id':              134170,
                    'kw.keyword':         134170,

                    'pi.person_id':        2963664,
                    'pi.info_type_id':     2963664,

                    'ml.movie_id':         29997
                    }

    return columns_domain, columns_card



def getcolumstatis():
    col_name=['ci.id', 'ci.person_id',  'ci.movie_id', "ci.person_role_id", "ci.nr_order", "ci.role_id",
              'kw.id', 'kw.keyword ',
              'mc.id', 'mc.movie_id', 'mc.company_id', 'mc.company_type_id',
              'mi.id', 'mi.movie_id', 'mi.info_type_id',
              'mi_idx.id','mi_idx.movie_id', 'mi_idx.info_type_id',
              'mk.id','mk.movie_id', 'mk.keyword_id',
              'ml.id','ml.movie_id', 'ml.linked_movie_id', 'ml.link_type_id',
              'pi.id','pi.person_id', 'pi.info_type_id',
              't.id','t.kind_id', 't.production_year',
              ]
    return col_name


























def getTableDic():
    tbDic=['cast_info ci','keyword kw','movie_companies mc','movie_info mi','movie_info_idx mi_idx','movie_keyword mk','movie_link ml','aka_title ati', 'complete_cast cc', 'title t']
    tbShortDic=['ci.', 'kw.', 'mc.','mi.','mi_idx.','mk.','ml.','ati.','cc.','t.']
    return tbDic, tbShortDic


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

def getJoincol():
    joinCol = ['t.id', 'mc.movie_id', 'ci.movie_id', 'mi.movie_id', 'mi_idx.movie_id', 'mk.movie_id', 'ml.movie_id',
                'kw.id','mk.keyword_id',
                'ati.movie_id', 'cc.movie_id']
    return joinCol

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

        'ml.movie_id = ati.movie_id':  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        'ml.movie_id = cc.movie_id':   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],

        'ati.movie_id = cc.movie_id':  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],

        'mk.keyword_id=kw.id':         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        'blank':                       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    }
    return joinFeatDic

def getJoinCol():
    join_col = ['t.id', 'mc.movie_id', 'ci.movie_id', 'mi.movie_id', 'mi_idx.movie_id', 'mk.movie_id', 'ml.movie_id',
                'kw.id','mk.keyword_id',
                'ati.movie_id', 'cc.movie_id']
    return join_col