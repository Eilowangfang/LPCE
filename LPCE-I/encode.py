import random
import sys
from statistics import *



def encodingFeat(node, level):
    #print("node content:", node)

    feat = []
    oper_Dic, operFeatDic = getOpeators()
    type_Dic = getType()
    tableFetDic = getTableFeatDic()
    col_FilterDic = getFilterCol()
    filterFetDic = getFilterFeatDic()
    filterColDomain = getFilterColDomain()
    joinFeatDic = getJoinFeatDic()
    col_JoinDic = getJoinCol()

    #base relation
    if level == 1:
        #operator part
        #type operator
        isFilter = False
        for i in range(len(oper_Dic)):
            if node.count(oper_Dic[i])>0:
                isFilter = True
        if isFilter:
            feat.append(type_Dic["filter"])
        else:
            feat.append(type_Dic["scan"]) #here, "scan" means read the whole column without selection

        #table part
        for key in tableFetDic.keys():
            if node.count(key) > 0:
                feat.append(tableFetDic[key])


        if isFilter:
            # one filter
            num = 0
            for col in col_FilterDic:
                num += node.count(col)

            if num == 1:
                cf = ""
                for key in filterFetDic.keys():
                    if node.count(key) > 0:
                        feat.append(filterFetDic[key])
                        cf = key
                for key in operFeatDic.keys():
                    if node.count(key) > 0:
                        feat.append(operFeatDic[key])
                        lwb = filterColDomain[cf][0]
                        upb = filterColDomain[cf][1]
                        pos = node.find(key)
                        value = node[pos + 1:]
                        value = (float(value) - lwb) / (upb - lwb)
                        feat.append(value)
                # join part
                feat.append(joinFeatDic['blank'])

            if num > 1:
                print("Error: There are two filters in one table")

        #base relation has no selection
        if isFilter == False:
            #filter part
            feat.append(filterFetDic['blank'])
            feat.append(operFeatDic['blank'])
            feat.append(0.0)
            #Join part
            feat.append(joinFeatDic['blank'])



    #join node
    if level >= 2:
        feat.append(type_Dic['join'])

        #table part
        l = tableFetDic['blank']
        for key in tableFetDic.keys():
            if node.count(key) > 0:
                for i in range(len(tableFetDic[key])):
                    l[i] =  l[i] ^ tableFetDic[key][i]
        feat.append(l)

        #filter part
        feat.append(filterFetDic['blank'])
        feat.append(operFeatDic['blank'])
        feat.append(0.0)
        #join part
        pos = node.find("=")
        lCol = node[:pos]
        rCol = node[pos+1:]
        for col in col_JoinDic:
            if lCol.count(col) > 0:
                lCol = col
            if rCol.count(col) > 0:
                rCol = col
        for key in joinFeatDic.keys():
            if key.count(lCol) > 0 and key.count(rCol) > 0:
                feat.append(joinFeatDic[key])
                break



    tmp = []
    for v in feat:
        if isinstance(v,float):
            tmp.append(v)
        else:
            for i in v:
                tmp.append(i)
    feat = tmp
    #print(feat)
    #print("  ", len(feat))
    #print("\n")


    return feat


