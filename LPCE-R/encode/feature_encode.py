from encode.metadata import *
import os


class planNode(object):
    leftChild = None
    rightChild = None
    parentNode = None
    info = ""
    indent = -1
    func = {}
    encode = []
    output = {}
    def __int__(self):
        self.leftChild = None
        self.rightChild = None
        self.parentNode = None
        self.info = ""
        self.indent = -1
        self.func = {}
        self.encode = []
        self.output = {}




def findChildren(plan, parNode):
    subPlanStart = False
    childIndent = -1
    leftNode = None
    rightNode = None

    for l in plan:
        if l.count("->") > 0:
            if l == parNode.info:
                if subPlanStart == False:
                    subPlanStart = True
                continue

            if l.find("->") <= parNode.indent and subPlanStart:
                break

            if l.find("->") > parNode.indent and childIndent == -1 and subPlanStart:
                leftNode = planNode()
                if leftNode.info == "":
                    childIndent = l.find("->")
                    leftNode.info = l
                    leftNode.indent = l.find("->")
                    continue

            if l.find("->") > parNode.indent:
                if l.find("->") == childIndent and subPlanStart:
                    rightNode = planNode()
                    rightNode.info = l
                    rightNode.indent = l.find("->")
                else:
                    continue

    return leftNode, rightNode


def dfsSearch(fatherNode, maxIndent, lines):
    if fatherNode.indent == -1:
        return

    left, right = findChildren(lines, fatherNode)
    #For easy understand, we make all scan/index scan nodes at right side
    if left != None:
        if left.info.count("Index Scan") > 0 or left.info.count("Seq Scan") > 0 or left.info.count("Scan") > 0:
            tmp = left
            left = right
            right = tmp
    fatherNode.leftChild = left
    fatherNode.rightChild = right
    if left != None:
        left.parentNode = fatherNode
        dfsSearch(left, maxIndent, lines)
    if right != None:
        right.parentNode = fatherNode
        dfsSearch(right, maxIndent, lines)





def dfsNodeInfo(node, lines, tables):
    if node == None:
        return

    add = False
    for l in lines:
        if add:
            if l.count("->") > 0 or l.count(" Planning") > 0:
                break
            node.info += l
        if l == node.info:
            add = True

    node.func = {}
    for t in tables:
        if node.info.count(t) > 0:
            #print(t)
            node.func['table'] = t
            node.func['table_short'] = tables[t]

    dfsNodeInfo(node.leftChild, lines, tables)
    dfsNodeInfo(node.rightChild, lines, tables)


def nodeFunc(node, filterInQur, joinInQur):
    if node == None:
        return

    if node.info.count("Seq Scan") > 0:
        node.func['operation'] = 'Seq Scan'
        node.func['predicate'] = filterInQur[node.func['table']]

    if node.info.count("Index Scan") > 0 or node.info.count("Index Only Scan") > 0:
        node.func['operation'] = 'Index Scan'
        node.func['predicate'] = filterInQur[node.func['table']]


    if node.info.count("Hash Join") > 0:
        if node.info.count("Hash Cond: (") > 0:
            pos = node.info.find("Hash Cond: (")
            tmp = node.info[pos+12 :]
            endPos = tmp.find(")")
            node.func['operation'] = 'Hash Join'
            node.func['predicate'] = []
            node.func['predicate'].append(tmp[:endPos])
        else:
            assert("ERROR: Hash Join node extract failed")

    if node.info.count("Nested Loop") > 0:
        if node.info.count("Join Filter: (") > 0:
            pos = node.info.find("Join Filter: (")
            tmp = node.info[pos+14 :]
            endPos = tmp.find(")")
            node.func['operation'] = 'Nested Loop'
            node.func['predicate'] = []
            node.func['predicate'].append(tmp[:endPos])
        elif node.leftChild != None and node.leftChild.info.count("Index Cond: (") > 0:
            pos = node.leftChild.info.find("Index Cond: (")
            tmp = node.leftChild.info[pos+13 :]
            endPos = tmp.find(")")
            join_Cond = tmp[:endPos]
            node.func['operation'] = 'Nested Loop'
            node.func['predicate'] = []
            node.func['predicate'].append(join_Cond)
        elif node.rightChild!= None and node.rightChild.info.count("Index Cond: (") > 0:
            pos = node.rightChild.info.find("Index Cond: (")
            tmp = node.rightChild.info[pos+13 :]
            endPos = tmp.find(")")
            join_Cond = tmp[:endPos]
            join_Cond = node.rightChild.func['table_short'] + "." + join_Cond
            node.func['operation'] = 'Nested Loop'
            node.func['predicate'] = []
            node.func['predicate'].append(join_Cond)
        else:
            assert("ERROR: Nested Loop node extract failed")

    if node.info.count("Hash  (") > 0:
        node.func['operation'] = 'Hash'

    if node.info.count("Sort  (") > 0:
        node.func['operation'] = 'Sort'

    if node.info.count("Merge Join") > 0:
        if node.info.count("Merge Cond: (") > 0:
            pos = node.info.find("Merge Cond: (")
            tmp = node.info[pos+13 :]
            endPos = tmp.find(")")
            node.func['operation'] = 'Merge Join'
            node.func['predicate'] = []
            node.func['predicate'].append(tmp[:endPos])
        else:
            assert("ERROR: Nested Loop node extract failed")

    nodeFunc(node.leftChild,filterInQur, joinInQur)
    nodeFunc(node.rightChild, filterInQur, joinInQur)


def dfsTravel(node):
    if node == None:
        return
    print(node.func)
    dfsTravel(node.leftChild)
    dfsTravel(node.rightChild)


def readPlan(plan, filterInQur, joinInQur):
    lines = plan
    rootNode = planNode()
    tables = tables_info()

    for l in lines:
        if l.count("->") > 0:
            rootNode.info = l
            rootNode.indent = l.find("->")
            break

    maxIndent = 0
    n = 0
    for l in lines:
        maxIndent = max(maxIndent, l.find("->"))
        if l.count("->") > 0:
            n = n + 1

    dfsSearch(rootNode, maxIndent, lines)
    dfsNodeInfo(rootNode, lines, tables)
    nodeFunc(rootNode, filterInQur, joinInQur)
    #dfsTravel(rootNode)

    return rootNode


def parseQuery(qur):
    tables = tables_info()
    filters, tables_filters = filters_info()
    tbsInQur = []
    filtersInQur = []
    joinInQur = []
    for t in tables:
        if qur.count(t) > 0:
            tbsInQur.append(t)

    pos = qur.find("WHERE ")
    endPos = qur.find(";")
    temp = qur[pos + 6 : endPos]
    #print(temp)
    parts = temp.split(" AND ")

    for p in parts:
        if p.count(".") > 1:
            joinInQur.append(p)
        else:
            check = False
            for f in filters:
                if p.count(f) > 0:
                    check = True
                    break
            if check == False:
                assert ("Error: unseen filter column")
            filtersInQur.append(p)

    dic_filterInQur = {}
    for t in tbsInQur:
        dic_filterInQur[t] = []
        for tf in tables_filters[t]:
            for f in filtersInQur:
                if f.count(tf) > 0:
                    dic_filterInQur[t].append(f)

    return dic_filterInQur, joinInQur



def encodeFeatVector(node, typeCode, tableCode, operCode, filterCode, filterDomain, joinCode):
    if node == None:
        return

    #operation feature
    feature = []
    if 'operation' not in node.func:
        print("###", node.func)
    if node.func['operation'].count("Hash Join") > 0 or node.func['operation'].count("Nested Loop") > 0 or node.func['operation'].count("Merge Join") > 0 :
        feature.append(typeCode['join'])
    elif node.func['operation'].count("Scan") > 0: # table with filter
        if 'predicate' in node.func:
            feature.append(typeCode['scan'])
        else:
            feature.append(typeCode['fullscan'])


    #table feature
    if 'table' in node.func:
        t = node.func['table']
        if t in tableCode:
            feature.append(tableCode[t])
        else:
            assert print("Error: unseen table")
    else:
        feature.append(tableCode['blank'])

    #filter feature
    if 'table' in node.func and 'predicate' in node.func:
        #filter without no predicate
        if len(node.func['predicate']) == 0:
            feature.append(filterCode['blank'])
            feature.append(operCode['blank'])
            feature.append('0.0')
        for pred in node.func['predicate']:
            for p in operCode:
                if pred.count(p) > 0:
                    column = pred[:pred.find(p)]
                    value = pred[pred.find(p) + len(p):]
                    if column in filterCode:
                        feature.append(filterCode[column])
                    else:
                        assert print("ERROR: unseen filter column", column)
                    feature.append(operCode[p])
                    if column in filterDomain:
                        down = filterDomain[column][0]
                        up = filterDomain[column][1]
                        v = (float(value) - down) / (up - down)
                        feature.append(v)
                    else:
                        assert print("ERROR: unseen filter column and domain", column)
    else:
        feature.append(filterCode['blank'])
        feature.append(operCode['blank'])
        feature.append('0.0')

    #join feature
    if node.func['operation'].count("Hash Join") > 0 or node.func['operation'].count("Nested Loop") > 0 or node.func['operation'].count("Merge Join") > 0 :
        if 'predicate' in node.func:
            joinWord = node.func['predicate'][0]
            joinWord = joinWord.replace(' ', '')
            parts = joinWord.split('=')
            for j in joinCode:
                if j.count(parts[0]) > 0 and j.count(parts[1]) > 0:
                    feature.append(joinCode[j])
        else:
            assert print("Error: unseen join node predicate")
    else:
       feature.append(joinCode['blank'])

    feature_encode = []
    for f in feature:
        if isinstance(f,list):
           for ff in f:
               feature_encode.append(ff)
        else:
            feature_encode.append(f)

    #if node.func['operation'] == 'Hash' or node.func['operation'] == 'Sort':
    #    print('')
    #else:
    #    print(node.func, "    ---------  ", len(feature_encode))
        #print(feature_encode)
    node.encode = []
    node.encode = feature_encode

    encodeFeatVector(node.leftChild, typeCode, tableCode, operCode, filterCode, filterDomain, joinCode)
    encodeFeatVector(node.rightChild, typeCode, tableCode, operCode, filterCode, filterDomain, joinCode)


def encodeNode(rootNode):
    joinCode, tableCode, filterCode, typeCode, operCode, filterDomain = getFeatCode()
    encodeFeatVector(rootNode, typeCode, tableCode, operCode, filterCode, filterDomain, joinCode)


def getNodeOrder(rootNode):
    if rootNode == None:
        return

    getNodeOrder(rootNode.leftChild)
    getNodeOrder(rootNode.rightChild)
    #left node node_order = 0
    if rootNode.leftChild == None and rootNode.rightChild == None:
       rootNode.func['node_order'] = 0

    #hash/sort/mater node node_order = its child node
    if rootNode.leftChild != None and rootNode.rightChild == None:
        if rootNode.func['operation'] == 'Sort' or rootNode.func['operation'] == 'Hash':
            rootNode.func['node_order'] = rootNode.leftChild.func['node_order']
        else:
            assert print("ERROR: wrong node_order for node with single left child node")
    if rootNode.leftChild == None and rootNode.rightChild != None:
        if rootNode.func['operation'] == 'Sort' or rootNode.func['operation'] == 'Hash':
            rootNode.func['node_order'] = rootNode.rightChild.func['node_order']
        else:
            assert print("ERROR: wrong node_order for node with single right child node")

    if rootNode.leftChild != None and rootNode.rightChild != None:
        rootNode.func['node_order'] = max(rootNode.rightChild.func['node_order'], rootNode.leftChild.func['node_order']) + 1



def getNodeIndex(rootNode):
    queue=list()
    queue.append(rootNode)
    no = 0
    while len(queue)>0:
        treeNode=queue.pop(len(queue) - 1)
        treeNode.func['node_idx'] = no
        if treeNode.leftChild != None and treeNode.rightChild == None:
            no = no
        elif treeNode.leftChild == None and treeNode.rightChild != None:
            no = no
        else:
            no = no + 1
        if(treeNode.rightChild!=None):
            queue.append(treeNode.rightChild)
        if(treeNode.leftChild!=None):
            queue.append(treeNode.leftChild)

def outputAdjacentList(rootNode, adjacentList):
    if rootNode == None:
        return
    if rootNode.parentNode != None:
        if rootNode.parentNode.func['node_idx'] != rootNode.func['node_idx']:
            #print(rootNode.parentNode.func['node_idx'], rootNode.func['node_idx'])
            tmp = str(rootNode.parentNode.func['node_idx']) + " " + str(rootNode.func['node_idx'])
            adjacentList.append(tmp)
    outputAdjacentList(rootNode.leftChild, adjacentList)
    outputAdjacentList(rootNode.rightChild, adjacentList)

def outputEdgeOrder(node, edgeOrder):
    if node == None:
        return
    if node.parentNode != None:
        #skip hash/sort node
        if node.parentNode.func['node_order'] != node.func['node_order']:
            #print(rootNode.parentNode.func['node_order'])
            edgeOrder.append(node.parentNode.func['node_order'])
    outputEdgeOrder(node.leftChild, edgeOrder)
    outputEdgeOrder(node.rightChild, edgeOrder)


def outputNodeOrder(node, nodeOrder):
    if node == None:
        return
    #skip hash/sort node
    if node.leftChild != None and node.rightChild != None:
        nodeOrder.append(node.func['node_order'])
    if node.leftChild == None and node.rightChild == None:
        nodeOrder.append(node.func['node_order'])
    outputNodeOrder(node.leftChild, nodeOrder)
    outputNodeOrder(node.rightChild, nodeOrder)


def outputFeatEncode(node, featEncode):
    if node == None:
        return
    #skip hash/sort node
    if node.leftChild != None and node.rightChild != None:
        featEncode.append(node.encode)
    if node.leftChild == None and node.rightChild == None:
        featEncode.append(node.encode)
    outputFeatEncode(node.leftChild, featEncode)
    outputFeatEncode(node.rightChild, featEncode)


def getNodeRealCard(node):
    if node == None:
        return
    if node.info.count("(actual") > 0:
        pos = node.info.find("(actual")
        tmp = node.info[pos:]
        endPos = tmp.find(")")
        tmpInfo = tmp[:endPos]
        #print("---", tmpInfo)
        pos = tmpInfo.find("rows=")
        tmpInfo = tmpInfo[pos + 5:]
        endPos = tmpInfo.find(" ")
        row = tmpInfo[:endPos]
        #print(" rows", row)
        pos = tmpInfo.find("loops=")
        loop = tmpInfo[pos + 6:]
        #print(" loops", loop)
        if int(row) == 0:
            card = 1 * int(loop)
        else:
            card = int(row) * int(loop)
        node.func['realCard'] = card

    getNodeRealCard(node.leftChild)
    getNodeRealCard(node.rightChild)



def outputRealCard(node, realCard):
    if node == None:
        return
    if node.leftChild != None and node.rightChild != None:
        realCard.append(node.func['realCard'])
    if node.leftChild == None and node.rightChild == None:
        realCard.append(node.func['realCard'])
    outputRealCard(node.leftChild, realCard)
    outputRealCard(node.rightChild, realCard)

def outputFile(rootNode, tag):

    getNodeOrder(rootNode)
    getNodeIndex(rootNode)
    getNodeRealCard(rootNode)

    #output node order
    nodeOrder = []
    outputNodeOrder(rootNode, nodeOrder)

    print("Node order: ", nodeOrder)
    dir=os.path.join(os.getcwd(),"outfile")
    fw = open(os.path.join(dir, "node_order.txt"), "w")
    fw.write("Plan  " + str(tag) + "\n")
    for no in nodeOrder:
        fw.write(str(no) + " ")
    fw.write("\n")

    #Adjacent List
    adjacentList = []
    outputAdjacentList(rootNode, adjacentList)
    print("Adjacent list: ", adjacentList)
    fw = open(os.path.join(dir, "adjacency_list.txt"), "w")
    fw.write("Plan  " + str(tag) + "\n")
    for adj in adjacentList:
        fw.write(adj + "\n")

    #Edge Order
    edgeOrder = []
    outputEdgeOrder(rootNode, edgeOrder)
    print("Edge order: ", edgeOrder)
    fw = open(os.path.join(dir, "edge_order.txt"), "w")
    fw.write("Plan  " + str(tag) + "\n")
    for eo in edgeOrder:
        fw.write(str(eo) + " ")
    fw.write("\n")

    featEncode = []
    outputFeatEncode(rootNode, featEncode)
    fw = open(os.path.join(dir, "feature.txt"), "w")
    fw.write("Plan  " + str(tag) + "\n")
    print("Feature: ")
    for eo in featEncode:
        if len(eo) != 70:
            assert  print("ERROR: check wrong feature length")
        for i in range(len(eo)):
            if i != len(eo) - 1:
                fw.write(str(eo[i]) + " ")
            else:
                fw.write(str(eo[i]) + "\n")


    realCard = []
    outputRealCard(rootNode,realCard)
    print("Label ", realCard)
    fw = open(os.path.join(dir, "label.txt"), "w")
    fw.write("Plan  " + str(tag) + "\n")
    for card in realCard:
        fw.write(str(card) + "\n")


if __name__ == "__main__":
    #query = "SELECT COUNT(*) FROM title t,movie_companies mc,cast_info ci,movie_info mi,movie_info_idx mi_idx,movie_keyword mk,keyword k WHERE t.id=mc.movie_id AND t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND t.id=mk.movie_id AND mk.keyword_id=k.id AND t.production_year>1921 AND mc.id>467277 AND ci.role_id=7 AND mi.id>4459358 AND mk.id<106866 AND k.keyword>123487;"
    #query = "SELECT COUNT(*) FROM title t,movie_companies mc,cast_info ci,movie_info mi,movie_keyword mk,keyword k,movie_link ml WHERE t.id=mc.movie_id AND t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mk.movie_id AND mk.keyword_id=k.id AND t.id=ml.movie_id AND t.production_year=1986 AND ci.role_id=9 AND mi.id<3860470 AND mk.id<2608316 AND k.keyword>41149 AND ml.linked_movie_id<2323262;"



    #filterInQur is a dictionary to denote the filter columns of tables
    #joinInQur
    #filterInQur, joinInQur = parseQuery(query)
    #rootNode = readPlan(filterInQur, joinInQur)
    #encodeNode(rootNode)
    #outputFile(rootNode, 1)
    #dfsTravel(rootNode)



    f = open("example_plan_log.txt")
    lines = f.readlines()
    #
    plan = []
    qur = ""
    oneQur = False
    no = 0
    for l in lines:
        if oneQur:
            plan.append(l)

        if l.count("SELECT") > 0:
            qur = l
            no = no + 1
            plan = []
            oneQur = True

        if l.count("Execution Time:") > 0:
            filterInQur, joinInQur = parseQuery(qur)
            #print(filterInQur, joinInQur)
            rootNode = readPlan(plan, filterInQur, joinInQur)
            print("============\n")
            dfsTravel(rootNode)
            encodeNode(rootNode)
            outputFile(rootNode, no)




