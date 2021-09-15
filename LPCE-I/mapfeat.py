from statistics import *
import numpy as np

def origin_encode():
    column_dic = {
        "t.id":                 [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "t.kind_id":            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "t.production_year":    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "mc.id":                [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "mc.company_id":        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "mc.movie_id":          [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "mc.company_type_id":   [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "ci.id":                [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "ci.movie_id":          [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "ci.person_id":         [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "ci.role_id":           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "mi.id":                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "mi.movie_id":          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "mi.info_type_id":      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "mi_idx.id":            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "mi_idx.movie_id":      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "mi_idx.info_type_id":  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "mk.id":                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "mk.movie_id":          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "mk.keyword_id":        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "k.id":                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        "k.keyword":            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        "pi.id":                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        "pi.person_id":         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        "pi.info_type_id":      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        "ml.id":                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        "ml.movie_id":          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        "ml.linked_movie_id":   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        "ml.link_type_id":      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
    }

    return column_dic


def get_origin_column(feat):
    column_dic = origin_encode()
    found = False
    result = ""
    for key in column_dic:
        encode = column_dic[key]
        found = True
        for j in range(len(encode)):
            if encode[j] != int(feat[j]):
                found = False
        if found == True:
            result = key
            break

    if found == False:
        return "blank"
    else:
        return result


def getoperator(feat):
    opera_dic = { "=": [0,0,1], ">": [0,1,0], "<": [1,0,0]}
    found = False
    result = ""
    for key in opera_dic:
        encode = opera_dic[key]
        found = True
        for j in range(len(encode)):
            if encode[j] != int(feat[j]):
                found = False
        if found == True:
            result = key
            break
    if found == False:
        return "blank"
    else:
        return result

def get_origin_type(feat):
    opera_dic = { "aggregation": [0,0,0,0,1], "nested loop": [0,0,0,1,0], "hash join": [0,0,1,0,0],
                  "seq_scan": [0,1,0,0,0], "index_scan": [1,0,0,0,0]
                  }
    found = False
    result = ""
    for key in opera_dic:
        encode = opera_dic[key]
        found = True
        for j in range(len(encode)):
            if encode[j] != int(feat[j]):
                found = False
        if found == True:
            result = key
            break
    if found == False:
        return "blank"
    else:
        return result


def mappingfeat():
    f=open("/home/dbgroup/csfwang/samples/10w_0-8join_withcard/6join_test_500/feature.txt")
    writeFile=open("/home/dbgroup/csfwang/samples/10w_0-8join_withcard/6join_test_500/new_feature.txt","w")
    lines=f.readlines()

    allcolumns, col_dic = getallcolumns()
    operator, operator_dic = getallopeator()
    join_dic = getalljoin()
    type_dic = gettype()

    no = 0
    for oneline in lines:
        if oneline.count("plan"):
            writeFile.write(oneline)
        else:
            feat = oneline.split(" ")
            type = feat[:5]
            type = get_origin_type(type)

            filterA = feat[5:(5 + 29)]
            operA = feat[(5 + 29):(5 + 29 + 3)]
            constA = feat[(5 + 29 + 3):(5 + 29 + 3 + 1)]
            filterB = feat[(5 + 29 + 3 + 1):(5 + 29 + 3 + 1 + 29)]
            operB = feat[(5 + 29 + 3 + 1 + 29):(5 + 29 + 3 + 1 + 29 + 3)]
            constB = feat[(5 + 29 + 3 + 1 + 29 + 3):(5 + 29 + 3 + 1 + 29 + 3 + 1)]
            filterA = get_origin_column(filterA)
            filterB = get_origin_column(filterB)
            operA = getoperator(operA)
            operB = getoperator(operB)

            joincolA = feat[(5 + 29 + 3 + 1 + 29 + 3 + 1):(5 + 29 + 3 + 1 + 29 + 3 + 1 + 29)]
            joinoper = feat[(5 + 29 + 3 + 1 + 29 + 3 + 1 + 29):(5 + 29 + 3 + 1 + 29 + 3 + 1 + 29 + 3)]
            joincolB = feat[(5 + 29 + 3 + 1 + 29 + 3 + 1 + 29 + 3):(5 + 29 + 3 + 1 + 29 + 3 + 1 + 29 + 3 + 29)]
            cardl = feat[(5 + 29 + 3 + 1 + 29 + 3 + 1 + 29 + 3 + 29):(5 + 29 + 3 + 1 + 29 + 3 + 1 + 29 + 3 + 29 + 1)]
            cardr = feat[(5 + 29 + 3 + 1 + 29 + 3 + 1 + 29 + 3 + 29 + 1):(5 + 29 + 3 + 1 + 29 + 3 + 1 + 29 + 3 + 29 + 1 + 1)]
            #with real cardinality

            joincolA = get_origin_column(joincolA)
            joinoper = getoperator(joinoper)
            joincolB = get_origin_column(joincolB)

            #
            if filterA == "k.keyword":
                filterA = "kw.keyword"
            if filterB == "k.keyword":
                filterB = "kw.keyword"
            if filterA == "k.id":
                filterA = "kw.id"
            if filterB == "k.id":
                filterB = "kw.id"
            if joincolA == "k.id":
                joincolA = "kw.id"
            if joincolB == "k.id":
                joincolB = "kw.id"
            if joincolA == "k.keyword":
                joincolA = "kw.keyword"
            if joincolB == "k.keyword":
                joincolB = "kw.keyword"

                # write new feature
            # print(col_dic(filterA))
            new_feat = []
            if joinoper != "blank":
                new_feat.append(type_dic['join'])
                #print("Join: ", joincolA, joinoper, joincolB)
            else:
                if operA == "blank" and operB == "blank":
                    new_feat.append(type_dic['scan'])
                    #print("Select: ", filterA, operA, constA, filterB, operB, constB)
                if operA != "blank" or operB != "blank":
                    new_feat.append(type_dic['filter'])
                    #print("Select: ", filterA, operA, constA, filterB, operB, constB)

            pos_filterA = 0
            pos_filterB = 0
            for i in range(len(col_dic[filterA])):
                if col_dic[filterA][i] == 1:
                    pos_filterA = i
            for i in range(len(col_dic[filterB])):
                if col_dic[filterB][i] == 1:
                    pos_filterB = i


            if pos_filterA == 0 and pos_filterB == 0:
                new_feat.append(col_dic[filterA])
                new_feat.append(operator_dic[operA])
                new_feat.append(constA)
                new_feat.append(col_dic[filterB])
                new_feat.append(operator_dic[operB])
                new_feat.append(constB)

            if pos_filterB == 0 and pos_filterA > 0:
                new_feat.append(col_dic[filterA])
                new_feat.append(operator_dic[operA])
                new_feat.append(constA)
                new_feat.append(col_dic[filterB])
                new_feat.append(operator_dic[operB])
                new_feat.append(constB)

            if pos_filterA == 0 and pos_filterB > 0:
                new_feat.append(col_dic[filterB])
                new_feat.append(operator_dic[operB])
                new_feat.append(constB)
                new_feat.append(col_dic[filterA])
                new_feat.append(operator_dic[operA])
                new_feat.append(constA)

            if pos_filterA > 0 and pos_filterB > 0:
                if pos_filterA < pos_filterB:
                    new_feat.append(col_dic[filterA])
                    new_feat.append(operator_dic[operA])
                    new_feat.append(constA)
                    new_feat.append(col_dic[filterB])
                    new_feat.append(operator_dic[operB])
                    new_feat.append(constB)
                else:
                    new_feat.append(col_dic[filterB])
                    new_feat.append(operator_dic[operB])
                    new_feat.append(constB)
                    new_feat.append(col_dic[filterA])
                    new_feat.append(operator_dic[operA])
                    new_feat.append(constA)


            for key in join_dic:
                if key.count(joincolA) > 0 and key.count(joincolB) > 0:
                    new_feat.append(join_dic[key])

            new_feat.append(cardl)  #with real cardinality
            new_feat.append(cardr)  #with real cardinality
            if cardr[0].find('\n') >=0:
                cardr[0] = cardr[0][:len(cardr[0])-1]
            if no < 20:
                print(new_feat)

            n_feat = []
            for i in range(len(new_feat)):
                for j in range(len(new_feat[i])):
                    n_feat.append(new_feat[i][j])



            #print(no, len(n_feat))
            for i in range(len(n_feat)):
                if i == len(n_feat) - 1:
                    writeFile.write(str(n_feat[i]) + "\n")
                else:
                    writeFile.write(str(n_feat[i]) + " ")
        no=no+1



def checkfeat():
    f=open("/home/dbgroup/csfwang/LPCEI/LPCE_postgres/data/10w_0-8join/new_feature.txt")
    lines=f.readlines()

    for oneline in lines:
        if oneline.find("plan")<0:
            feat = oneline.split(" ")
            print(len(feat))

def adjacency_list():
    f=open("/home/dbgroup/csfwang/LPCEI/LPCE_postgres/data/10w_0-8join/6join_test_500/adjacency_list.txt")
    writeFile=open("/home/dbgroup/csfwang/LPCEI/LPCE_postgres/data/8join_100K/6join_test/new_adjacency_list.txt","w")
    lines=f.readlines()

    no = 0
    onequr = False
    for oneline in lines:
        part = oneline.split(" ")
        if onequr == True:
            onequr = False
            continue

        if oneline.find("plan") < 0:
            for i in range(len(part)):
                tmp = int(part[i]) - 1
                writeFile.write(str(tmp))
                if i == len(part) - 1:
                    writeFile.write("\n")
                else:
                    writeFile.write(" ")

        if oneline.count("plan") > 0:
            onequr = True
            writeFile.write(oneline)

        no = no + 1










def edge_order():
    f=open("/home/dbgroup/csfwang/LPCEI/LPCE_postgres/data/10w_0-8join/6join_test_500/edge_order.txt")
    writeFile=open("/home/dbgroup/csfwang/LPCEI/LPCE_postgres/data/8join_100K/6join_test/new_edge_order.txt","w")
    lines=f.readlines()

    no = 0
    for oneline in lines:
        if oneline.find("plan") < 0:
            part = oneline.split(" ")

            for i in range(len(part)):
                tmp = int(part[i])
                if i == 0:
                    continue
                else:
                    writeFile.write(str(tmp))
                    if i == len(part) - 1:
                        writeFile.write("\n")
                    else:
                        writeFile.write(" ")

        if oneline.count("plan") > 0:
            writeFile.write(oneline)

        no = no + 1





def node_order():
    f=open("/home/dbgroup/csfwang/LPCEI/LPCE_postgres/data/10w_0-8join/6join_test_500/node_order.txt")
    writeFile=open("/home/dbgroup/csfwang/LPCEI/LPCE_postgres/data/8join_100K/6join_test/new_node_order.txt","w")
    lines=f.readlines()

    no = 0
    for oneline in lines:
        if oneline.find("plan") < 0:
            part = oneline.split(" ")
            for i in range(len(part)):
                tmp = int(part[i])
                if i == 0:
                    continue
                else:
                    writeFile.write(str(tmp))
                    if i == len(part) - 1:
                        writeFile.write("\n")
                    else:
                        writeFile.write(" ")

        if oneline.count("plan") > 0:
            writeFile.write(oneline)

        no = no + 1





def label():
    f=open("/home/dbgroup/csfwang/LPCEI/LPCE_postgres/data/10w_0-8join/6join_test_500/label.txt")
    writeFile=open("/home/dbgroup/csfwang/LPCEI/LPCE_postgres/data/8join_100K/6join_test/new_label.txt","w")
    lines=f.readlines()

    no = 0
    onequr = False
    for oneline in lines:
        if onequr == True:
            onequr = False
            continue

        if oneline.find("plan") < 0:
            writeFile.write(oneline)

        if oneline.count("plan") > 0:
            onequr = True
            writeFile.write(oneline)

        no = no + 1



def exetime():
    f = open("/home/dbgroup/csfwang/LPCEI/LPCE_postgres/tmp")
    writeFile = open("/home/dbgroup/csfwang/LPCEI/LPCE_postgres/card.csv", "w")
    lines = f.readlines()

    iscard = False
    for oneline in lines:
        #pos = oneline.find("Execution Time:") + len("Execution Time:")
        #end = oneline.find("ms")

        if iscard:
            part = oneline.split(",")
            num = len(part)
            end = part[num-1].find(".")
            card_txt = part[num-1][:end]
            card = float(card_txt)
            writeFile.write(str(card)+"\n")
            iscard =False
        if oneline.find("Learned estimator outputs cardinality:")>=0:
            iscard = True





def exetime_card():
    f = open("/home/dbgroup/csfwang/samples/queries/8join/8joins_card.txt")
    writeFile = open("/home/dbgroup/csfwang/samples/queries/8join/useful_8join_label.txt", "w")
    #f = open("/home/dbgroup/csfwang/samples/queries/6join/join6_tmpres.txt")
    #writeFile = open("/home/dbgroup/csfwang/samples/queries/6join/join6_time.csv", "w")

    lines = f.readlines()

    onequer = []
    isqur = False
    no = 0
    for oneline in lines:
        if oneline.count("Query") > 0:
            isqur = True
            no = no + 1

        if isqur == True:
            onequer.append(oneline)

        if oneline.count("2021-07") > 0:
            isqur = False
            exc_time = 0
            card = 0
            loop = 0
            getcard = False
            if no < 5:
                for j in range(len(onequer)):
                    print(onequer[j])

            x = -1
            y = -1
            for i in range(len(onequer)):
                if onequer[i].find("Nested Loop") >= 0:
                    x = i
                    break

            for i in range(len(onequer)):
                if onequer[i].find("Hash Join") >= 0:
                    y = i
                    break

            if x >=0 and x < y:
                for j in range(len(onequer)):
                    if onequer[j].find("Nested Loop") >= 0:
                        start = onequer[j].find("actual time=") + len("actual time=")
                        left = onequer[j][start:]
                        start = left.find("..")+len("..")
                        end = left.find(" ")
                        exc_time = left[start:end]

                        start = left.find("rows=")+len("rows=")
                        leftcard = left[start:]
                        end = leftcard.find(" ")
                        card = int(leftcard[:end])

                        start = left.find("loops=")+len("loops=")
                        leftloop = left[start:]
                        end = leftloop.find(")")
                        loop = int(leftloop[:end])
                        card = card * loop

                        getcard = True
                        break




            if getcard == False:
                for j in range(len(onequer)):
                    if onequer[j].find("Hash Join") >= 0:
                        start = onequer[j].find("actual time=") + len("actual time=")
                        left = onequer[j][start:]
                        start = left.find("..") + len("..")
                        end = left.find(" ")
                        exc_time = left[start:end]

                        start = left.find("rows=") + len("rows=")
                        leftcard = left[start:]
                        end = leftcard.find(" ")
                        card = int(leftcard[:end])

                        start = left.find("loops=") + len("loops=")
                        leftloop = left[start:]
                        end = leftloop.find(")")
                        loop = int(leftloop[:end])
                        card = card * loop
                        break



            if card < 100000000 and card > 0 and float(exc_time) > 200000.0:
                print("Time: ", exc_time, " Card: ", card)
                for j in range(len(onequer)):
                    if onequer[j].find("SELECT COUNT") >= 0:
                        #writeFile.write(onequer[j])
                        writeFile.write(str(exc_time) + ",")
                        writeFile.write(str(card) + "\n")


            onequer = []





def compute_qerror():
    f = open("/home/dbgroup/csfwang/LPCEI/LPCE_postgres/card_LPCE.csv")
    lines = f.readlines()

    qerror=[]
    no = 0
    for oneline in lines:
        part = oneline.split(",")
        true = float(part[0])
        pred = float(part[1])
        if true <= pred:
            qerror.append(pred/true)
        else:
            qerror.append(true/pred)

    print("     =========Q-error Accuracy=========")
    print("     50th percentile: {}".format(np.percentile(qerror, 50)))
    print("     90th percentile: {}".format(np.percentile(qerror, 90)))
    print("     95th percentile: {}".format(np.percentile(qerror, 95)))
    print("     99th percentile: {}".format(np.percentile(qerror, 99)))
    print("     Max: {}".format(np.max(qerror)))
    print("     Mean: {}".format(np.mean(qerror)))





if __name__ == '__main__':
    mappingfeat()
    #checkfeat()
    # adjacency_list()
    # edge_order()
    # node_order()
    # label()
    #exetime()
    #exetime_card()
    #compute_qerror()
