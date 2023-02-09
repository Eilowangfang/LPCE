import torch
import os
from itertools import combinations
from utils.encode import *
from lpce.contentModule import *
from lpce.cardModule import *
from lpce.refineModule import *
from lpce.caller_content import *
from lpce.caller_card import *
from lpce.caller_refine import *


def getRelatLevel(level, numofRels):
    emu = []
    for n in range(numofRels):
        emu.append(n)
    comb = list(combinations(emu, level))
    return comb

def gettbIds(tbNum):
    tbIds = []
    tbTag = []
    for i in range(tbNum):
        tbIds.append(pow(2, i + 1))
        tbTag.append(i)
    return tbIds, tbTag

def getRelids(comb):
    relids = 0
    for i in comb:
        relids += pow(2, i + 1)
    return relids

def getDoneRelids(real_info):
    list = real_info.split(',')
    doneRelids = []
    relids_realCard = []
    doneRelid = dict()
    i = 0
    for i in range(len(list)):
        if(i % 2 == 0 and i + 1 < len(list)):
            doneRelids.append(int(list[i]))
            relids_realCard.append(int(list[i + 1]))
            doneRelid[int(list[i])] = int(list[i + 1])
    return doneRelid


#Check the node (base relation) already done executed at level 1
def GetDoneBaseRel(planNodes, doneRelids, queryInfo):
    for relid in planNodes.keys():
        node = planNodes[relid]
        if node.level == 1:
            if doneRelids.get(node.relid) != None:
                node.done = True
                node.card = doneRelids[node.relid]
                node.nodeInfo = queryInfo.predicate[node.relid]



#Check the node already done executed at level n
def GetDoneLevelnRel(level, planNodes, doneRelids):
    for relid in planNodes.keys():
        node = planNodes[relid]
        if node.level == level:
            if doneRelids.get(node.relid) != None:
                node.done = True
                node.card = doneRelids[node.relid]



def GetDoneRelatLeveln(relatLeveln, doneRelids):
    doneRelIds = []
    doneRels = []
    for rels in relatLeveln:
        relid = 0
        for r in rels:
            relid += pow(2, r + 1)
        if doneRelids.get(relid) != None:
            doneRelIds.append(relid)
            doneRels.append(rels)
        #print(rels, relid)
    return doneRelIds, doneRels

def EstimateRelatLevel2(relatLevel2, doneRelatBaseLevel):
    #print("###: ", doneRelatBaseLevel)
    print("***: ", len(relatLevel2))
    toRefineRel = []
    toEstimateRel = []
    for rels in relatLevel2:
        isValid = False
        for x in doneRelatBaseLevel:
            if x in rels:
                isValid = True
        if isValid:
            toRefineRel.append(rels)
            bothDone = True
            for r in rels:
                if r not in doneRelatBaseLevel:
                    toEstimateRel.append(r)
                    bothDone = False
            if bothDone:
                toEstimateRel.append(-1)

    print("### ", toRefineRel)
    print("@@  ", toEstimateRel)
    return toRefineRel, toEstimateRel





    #for i in range(len(toRefineRel)):
    #    print(toRefineRel[i], toEstimateRel[i])
    #print("###", toEstimateRel)
    #print("@@@", toRefineRel)


def EstimateRelatLeveln(relatLeveln, doneRelatPrevLevel):
    toRefineRel = []
    toEstimateRel = []
    print("##", relatLeveln)
    print("@@", doneRelatPrevLevel)
    for rels in relatLeveln:
        for doneRel in doneRelatPrevLevel:
            if doneRel in rels:
                print(doneRel, rels)
                toRefineRel.append(rels)
                for r in rels:
                    if r not in doneRel:
                        toEstimateRel.append(r)

    return toRefineRel, toEstimateRel



#def Estimate2RelatLeveln(relatLeveln, refinedRelatPrevLevel, estimatedRelatPrevLevel):
#for rels in relatLeveln:
# for r in refinedRelatPrevLevel:
#     x = set(r)
#     if x.issubset(rels):
#         print(r)











#Hence, we need to train moudle
#1. card module, both left and right child are executed nodes
#   (1,2,3)
#   /    \
#  (1,3) (2)  (1,3) (2) are two executed node

#2. content module, both left and right child are unexected nodes
#   (1,2,3)
#   /    \
#  (1,3) (2)  (1,3) (2) are two unexecuted node

#3. refined module, we need to consider three cases
#  Case 1
#   (1,2,3)
#      |
#   connect layer (CNL)
#   /    \
#  (1,3) (2)
# A) (1,3) is executed node from card module, and (2) is executed node from card module - (CNL-A)
# B) (1,3) is executed node from card module, and (2) unexectued node from content module - (CNL-B)

#  Case 2
#     (1,2,3,4)
#     /      \
#   (1,2,3)  (4)
#      |
#   connect layer (CNL-A)
#   /    \
#  (2)  (1,3)
#  (2), (1,3) are executed node from card module,
#  and (1, 2, 3) (4) are unexectued node at refine module.
# the connect layer is CNL-A


#  Case 3
#     (1,2,3,4)
#     /      \
#   (1,2,3)  (4)
#      |
#   connect layer (CNL-B)
#   /    \
#  (2)  (1,3)
#  (2) is executed node from card module,
#  (1,3) are unexecuted node from content module,
#  and (1, 2, 3) (4) are unexectued node at refine module.
# the connect layer is CNL-B



class RelNode:
    def __int__(self):
        self.level = -1
        self.relid = relid
        self.tag = 0
        self.rel = 0
        self.leftChild = -1
        self.rightChild = -1
        #leftChild: relid of left child
        #rightChild: relid of right child
        self.done = False
        self.module = -1
        # 0 card module   1 content module   2 refine + connect layer    3 refine internal
        self.card = -1
        self.content_hidden_state = []
        self.real_hidden_state = []
        self.refine_hidden_state = []
        #Encoded feature vector for current node
        self.feature = []
        self.leftChildCard = 0
        self.rightChildCard = 0
        self.nodeInfo = ""





#Init all nodes at level 1, that is base relation
def InitBaseNodes(numofRels, planNodes):
    for i in range(numofRels):
        tmpNode = RelNode()

        tmpNode.level = 1
        tmpNode.relid = pow(2, i + 1)
        tmpNode.done = False
        tmpNode.card = -1
        tmpNode.module = -1
        tmpNode.leftChild = -1
        tmpNode.rightChild = -1
        tmpNode.content_hidden_state = []
        tmpNode.real_hidden_state = []
        tmpNode.refine_hidden_state = []
        tmpNode.feature = []
        rel = []
        rel.append(i)
        tmpNode.rel = rel
        tmpNode.leftChildCard = 0
        tmpNode.rightChildCard = 0
        tmpNode.nodeInfo = ""
        planNodes[tmpNode.relid] = tmpNode




#Init all nodes at level n, one node is join among relations
def GetLevelnNodes(level, numofRels, planNodes):
    emu = []
    for n in range(numofRels):
        emu.append(n)
    comb = list(combinations(emu, level))
    for x in comb:
        tmpNode = RelNode()
        tmpNode.level = level
        tmpNode.done = False
        tmpNode.card = -1
        tmpNode.module = -1
        # 0 card module   1 content module   2 refine + connect layer    3 refine internal
        tmpNode.leftChild = -1
        tmpNode.rightChild = -1
        tmpNode.content_hidden_state = []
        tmpNode.real_hidden_state = []
        tmpNode.refine_hidden_state = []
        tmpNode.feature = []
        tmpNode.rel = x
        relid = 0
        for i in x:
            relid += pow(2, i + 1)
        tmpNode.relid = relid
        tmpNode.nodeInfo = ""
        tmpNode.leftChildCard = 0
        tmpNode.rightChildCard = 0
        planNodes[tmpNode.relid] = tmpNode



def GetBaseRelto_CardModule(planNodes, callerCardModule, min_label, max_label):
    # Given base relation
    # Return feature vector, c_l, c_r

    tableCard_Dic = getTableCard()
    feat_batch = []
    for relid in planNodes:
        node = planNodes[relid]
        if node.level == 1 and node.done == True:
            node.module = 0
            #Encode feature vector
            node.feature = encodingFeat(node.nodeInfo, node.level)
            #Add the real card of child node to done executed node
            for tb in tableCard_Dic:
                if(node.nodeInfo.count(tb) > 0):
                    node.leftChildCard = tableCard_Dic[tb]
                    node.rightChildCard = tableCard_Dic[tb]
                    norm_card = (np.log(node.leftChildCard) - np.log(min_label)) / (
                            np.log(max_label) - np.log(min_label))
                    node.feature.append(norm_card)
                    node.feature.append(norm_card)
            feat_batch.append(node.feature)


    #Call CARD module for done executed node
    out_batch, hidden_batch = callerCardModule.testbase(feat_batch)

    #Update hidden state from card module for done executed node
    no = 0
    for relid in planNodes:
        node = planNodes[relid]
        if node.level == 1 and node.done == True:
            node.real_hidden_state= hidden_batch[no]
            no = no + 1




# Give node already executed at level n
# Get hidden state of the node
def GetLevelnRelto_CardModule(level, planNodes, queryInfo, callerCardModule, callerContentModel, min_label, max_label):

    feat_batch = []
    right_batch = []
    left_batch = []
    node_cache = []
    for relid in planNodes:
        node = planNodes[relid]
        if node.level == level and node.done == True:
            node.module = 0

            #For node estimate in card module, the possible case is
            #both left and right child are from busy tree
            #Hence, we need to consider the case of busy tree
            #The method is for node at level n, we can combine the nodes
            #at nodes at n - i and i levels.

            found = False
            #1 left deep case
            for rightRel in node.rel:
                rightRelid = pow(2, rightRel + 1)
                leftRelid  = node.relid - rightRelid
                if planNodes[leftRelid].done == True and planNodes[rightRelid].done == True:
                    if found == False:
                        node.leftChild = leftRelid
                        node.rightChild = rightRelid
                        found == True

            #2 busy tree case
            for rightRelid in planNodes:
                rightNode = planNodes[rightRelid]
                if rightNode.done == True and found == False:
                    leftRelid  = node.relid - rightRelid
                    if planNodes.get(leftRelid) != None and planNodes[leftRelid].done == True:
                         node.leftChild = leftRelid
                         node.rightChild = rightRelid
                         found = True

            #Get the node info according to left and right child
            tbsInLeft = num2array(node.leftChild, 2)
            tbsInRight = num2array(node.rightChild, 2)
            node.nodeInfo = GetJoinNodeInfo(tbsInLeft, tbsInRight, queryInfo)
            #Encode node feature vector
            node.feature = encodingFeat(node.nodeInfo, node.level)

            card_tmp = planNodes[node.leftChild].card
            if card_tmp < 2:
                card_tmp = 2.0
            norm_card = (np.log(card_tmp) - np.log(min_label)) / (np.log(max_label) - np.log(min_label))
            node.feature.append(norm_card)

            card_tmp = planNodes[node.rightChild].card
            if card_tmp < 2:
                card_tmp = 2.0
            norm_card = (np.log(card_tmp) - np.log(min_label)) / (np.log(max_label) - np.log(min_label))
            node.feature.append(norm_card)

            feat_batch.append(node.feature)
            left_batch.append(planNodes[node.leftChild].real_hidden_state)
            right_batch.append(planNodes[node.rightChild].real_hidden_state)
            node_cache.append(node)

    if len(node_cache) > 0 :
        #Call card module, return hidden state
        out_batch, hidden_batch = callerCardModule.testJoin(feat_batch, left_batch, right_batch)
        #Update hidden state from card module for done executed node
        no = 0
        for node in node_cache:
            node.real_hidden_state = hidden_batch[no]

        #Call content module, used for refine module
        feat_batch = []
        right_batch = []
        left_batch = []
        for node in node_cache:
            feat_batch.append(node.feature[0:feature_dim])
            left_batch.append(planNodes[node.leftChild].content_hidden_state)
            right_batch.append(planNodes[node.rightChild].content_hidden_state)

        out_batch, hidden_batch = callerContentModel.testJoin(feat_batch, left_batch, right_batch)
        no = 0
        for node in node_cache:
            node.content_hidden_state = hidden_batch[no]






def GetBaseRelto_ContentModule(planNodes, queryInfo, callerContentModel, feature_dim):
    # Given base relation
    # Return feature vector, c_l, c_r
    for relid in planNodes:
        node = planNodes[relid]
        if node.level == 1 and node.done == False:
            node.module = 1
            node.nodeInfo = queryInfo.predicate[relid]
            # Encode feature vector
            node.feature = encodingFeat(node.nodeInfo, node.level)


   #We output the hidden states for all base relations
   #Call CONTENT module for all base node
    feat_batch = []
    for relid in planNodes:
        node = planNodes[relid]
        feat_batch.append(node.feature[0:feature_dim])

    card_batch, hidden_batch = callerContentModel.testbase(feat_batch)


    #Update hidden state from content module for each node
    #update the card estimation, if the node is not filtered (no <, =, >), then we can use the
    #real card of the whole table.
    no = 0
    operator, operator_Dic = getOpeators()
    tableCard_Dic = getTableCard()
    for relid in planNodes:
        node = planNodes[relid]
        if node.level == 1:
          node.content_hidden_state = hidden_batch[no]
          if node.done == False:
              node.card = card_batch[no]

              #In case the relation does not have filter
              hasFilter = False
              for op in operator:
                if(node.nodeInfo.count(op) > 0):
                    hasFilter = True
                    break
              if(hasFilter == False):
                    for key in tableCard_Dic:
                        if(node.nodeInfo.count(key) > 0):
                            node.card = tableCard_Dic[key]

          no = no + 1




#Check the node at level n, which has to be estimated by CONTENT module
#That is neither left nor right child are executed node
def GetLevelnRelto_ContentModule(level, planNodes, callerContentModel, feature_dim):

    node_cache = []
    feat_batch = []
    left_state_batch = []
    right_state_batch = []
    for relid in planNodes:
        node = planNodes[relid]
        if node.level == level and node.done == False and node.module == -1:
            # if left and right child is not card node, neither refine node
            # then we send the node to content module
            # If both left and right child are from content module
            # Then we estimate the node at content module
            # We can only consider the left deep tree, which means the right child is
            # signle relation.
            for rightRel in node.rel:
                rightRelid = pow(2, rightRel + 1)
                leftRelid  = node.relid - rightRelid
                if planNodes[leftRelid].nodeInfo.count("ILLEGAL_JOIN") > 0:
                    continue
                if planNodes[rightRelid].nodeInfo.count("ILLEGAL_JOIN") > 0:
                    continue
                if planNodes[leftRelid].module == 1 and planNodes[rightRelid].module == 1:
                    node.module = 1
                    node.rightChild = rightRelid
                    node.leftChild = leftRelid

            if node.module != -1:
                tbsInLeft = num2array(node.leftChild, 2)
                tbsInRight = num2array(node.rightChild, 2)
                node.nodeInfo = GetJoinNodeInfo(tbsInLeft, tbsInRight, queryInfo)
                #Encode feature vector
                node.feature = encodingFeat(node.nodeInfo, node.level)
                if len(node.feature) == feature_dim:
                    node_cache.append(node)
                    feat_batch.append(node.feature)
                    left_state_batch.append(planNodes[node.leftChild].content_hidden_state)
                    right_state_batch.append(planNodes[node.rightChild].content_hidden_state)
                else:
                    if node.nodeInfo.count("ILLEGAL_JOIN") > 0:
                        node.card = -1
                    else:
                        print("ERROR: The feature is encoded as a vector of unmatched dimension")

    if len(node_cache) > 0 :
        #Card estimation on content module
        card_batch, hidden_batch = callerContentModel.testJoin(feat_batch, left_state_batch, right_state_batch)
        #Update card estimation
        no = 0
        for node in node_cache:
            node.card = card_batch[no]
            node.content_hidden_state = hidden_batch[no]
            no = no + 1
        #Update card estimation



def GetLevelnRel_HiddenState_ContentModule(level, planNodes, callerContentModel, feature_dim):
    node_cache = []
    feat_batch = []
    left_batch = []
    right_batch = []
    for relid in planNodes:
        node = planNodes[relid]
        if node.level == level:
            if node.card != -1 and node.nodeInfo.count("ILLEGAL_JOIN") > 0:
                print("Some node are not estimated")

            if node.nodeInfo.count("ILLEGAL_JOIN") == 0:
                if planNodes[node.leftChild].nodeInfo.count("ILLEGAL_JOIN") > 0 :
                    print("Some nodes are not estimated")
                    continue
                if planNodes[node.rightChild].nodeInfo.count("ILLEGAL_JOIN") > 0 :
                    print("Some nodes are not estimated")
                    continue
                if len(node.feature) < feature_dim:
                    print("Some nodes are not encoded into feature")
                    continue

                node_cache.append(node)
                feat_batch.append(node.feature[0:feature_dim])
                left_batch.append(planNodes[node.leftChild].content_hidden_state)
                right_batch.append(planNodes[node.rightChild].content_hidden_state)

    #Card estimation on content module
    card_batch, hidden_batch = callerContentModel.testJoin(feat_batch, left_batch, right_batch)
    no = 0
    for node in node_cache:
        node.content_hidden_state = hidden_batch[no]
        #print("node ", node.rel, " ", len(node.content_hidden_state))
        no = no + 1

#Check the node at level n, which has to be estimated by REFINE module with connect layer
#That is left child is executed node from CARD module,
#and right child is unexecuted node from CONTENT module.
def GetLevelnRelto_RefineConnectLayerModule(level, planNodes, callerRefineModule):
    feat_batch = []
    left_real_batch = []
    left_content_batch = []
    right_batch = []
    node_cache = []
    for relid in planNodes:
        node = planNodes[relid]
        if node.level == level and node.done == False and node.module == -1:
            # There are two cases that needs connect layer and refine module
            # Case 1: left child node is from card module
            # then we can regard the node as refine module, and also next to connect layer
            # note that we assume the subplan (the root of which is the node)
            # is left deep tree, we only consider right child is a signle relation
            # Case 2: both left child node and right node are from card module

            # Case 1: left deep tree
            for i in range(len(node.rel)):
                rightRel = node.rel[len(node.rel) - i - 1]
                rightRelid = pow(2, rightRel + 1)
                leftRelid = node.relid - rightRelid
                if planNodes[leftRelid].module == 0:
                    node.module = 2
                    node.leftChild = leftRelid
                    node.rightChild = rightRelid


            # # Case 2: bushy tree
            # #2 busy tree case
            # if found == False:
            #     for rightRelid in planNodes:
            #         rightNode = planNodes[rightRelid]
            #         leftRelid  = node.relid - rightRelid
            #         if planNodes.get(leftRelid) != None and found == False:
            #             if planNodes[leftRelid].level + planNodes[rightRelid].level != node.level:
            #                 continue
            #             if planNodes[leftRelid].module == 0 and planNodes[rightRelid].module == 0:
            #                 node.module = 2
            #                 node.leftChild = leftRelid
            #                 node.rightChild = rightRelid
            #                 found = True
            #             if planNodes[leftRelid].module == 0 and planNodes[rightRelid].module == 1:
            #                 node.module = 3
            #                 node.leftChild = leftRelid
            #                 node.rightChild = rightRelid
            #                 found = True

            #get vector feature
            if node.module != -1:
                tbsInLeft = num2array(node.leftChild, 2)
                tbsInRight = num2array(node.rightChild, 2)
                node.nodeInfo = GetJoinNodeInfo(tbsInLeft, tbsInRight, queryInfo)
                #Encode node feature vecotr
                node.feature = encodingFeat(node.nodeInfo, node.level)

                if len(node.feature) == feature_dim:
                    node_cache.append(node)
                    feat_batch.append(node.feature)
                    left_real_batch.append(planNodes[node.leftChild].real_hidden_state)
                    left_content_batch.append(planNodes[node.leftChild].content_hidden_state)
                    if len(planNodes[node.leftChild].content_hidden_state) == 0 :
                        print("     ---- ", planNodes[node.leftChild].relid, " ", planNodes[node.leftChild].nodeInfo)
                    right_batch.append(planNodes[node.rightChild].content_hidden_state)
                else:
                    if node.nodeInfo.count("ILLEGAL_JOIN") > 0:
                        node.card = -1
                    else:
                        print("ERROR: The feature is encoded as a vector of unmatched dimension")


    if len(node_cache) > 0:
        # Card estimation on content module
        card_batch, hidden_batch = callerRefineModule.testConnectLayer(feat_batch, left_real_batch, left_content_batch, right_batch)
        no = 0
        for node in node_cache:
            node.card = card_batch[no]
            node.refine_hidden_state = hidden_batch[no]
            no = no + 1



#Check the node at level n, which has to be estimated by REFINE module
#The node is upper level of connect layer at Refine Internal, which we say "RefineInternalModule"
#Assume the connect layer connect to refine module at level i, Refine Internal denotes the
#node at levels upper than i + 1.
#That is left child is executed node from REFINE module,
#and right child is unexecuted node from CONTENT module.
def GetLevelnRelto_RefineInternalModule(level, planNodes, callerRefineModule):

    feat_batch = []
    left_batch = []
    right_batch = []
    node_cache = []
    for relid in planNodes:
        node = planNodes[relid]
        inRefinModule = False

        if node.level == level and node.done == False and node.module == -1:
            # both left and right module are from refine module
            # note that we assume the subplan (the root of which is the node)
            # is left deep tree, we only consider right child is a signle relation
            for i in range(len(node.rel)):
                rightRel = node.rel[len(node.rel) - i - 1]
                rightRelid = pow(2, rightRel + 1)
                leftRelid = node.relid - rightRelid
                if planNodes[leftRelid].module == 2:
                    if planNodes[leftRelid].nodeInfo.count("ILLEGAL_JOIN") > 0:
                        continue
                    node.module = 3
                    node.leftChild = leftRelid
                    node.rightChild = rightRelid
                    inRefinModule = True
                    break


        if node.level == level and node.done == False and node.module == -1:
            # both left and right module are from refine module
            # note that we assume the subplan (the root of which is the node)
            # is left deep tree, we only consider right child is a signle relation
            for i in range(len(node.rel)):
                rightRel = node.rel[len(node.rel) - i - 1]
                rightRelid = pow(2, rightRel + 1)
                leftRelid = node.relid - rightRelid
                if planNodes[leftRelid].nodeInfo.count("ILLEGAL_JOIN") > 0:
                    continue
                if planNodes[leftRelid].module == 3:
                    node.module = 3
                    node.leftChild = leftRelid
                    node.rightChild = rightRelid
                    inRefinModule = True
                    break

        if node.level == level and node.module == -1:
            node.nodeInfo = "ILLEGAL_JOIN"

        if node.module != -1 and inRefinModule == True:
            tbsInLeft = num2array(node.leftChild, 2)
            tbsInRight = num2array(node.rightChild, 2)
            node.nodeInfo = GetJoinNodeInfo(tbsInLeft, tbsInRight, queryInfo)
            #Encode node feature vector
            node.feature = encodingFeat(node.nodeInfo, node.level)

            if len(node.feature) == feature_dim:
                node_cache.append(node)
                feat_batch.append(node.feature)
                # Left node is at refine module
                left_batch.append(planNodes[node.leftChild].refine_hidden_state)
                # Right node is from content module, as we consider left-deep tree
                right_batch.append(planNodes[node.rightChild].content_hidden_state)
                if len(planNodes[node.leftChild].refine_hidden_state) == 0 :
                    print("     ---- ", planNodes[node.leftChild].relid, " ", planNodes[node.leftChild].nodeInfo)
            else:
                if node.nodeInfo.count("ILLEGAL_JOIN") > 0:
                    node.card = -1
                else:
                    print("ERROR: The feature is encoded as a vector of unmatched dimension")

    if len(node_cache) > 0 :
        card, hidden_state = callerRefineModule.testInternalLayer(feat_batch, left_batch, right_batch)
        no = 0
        for node in node_cache:
            node.card = card[no]
            node.refine_hidden_state = hidden_state[no]
            no = no + 1


def GetLevelnRelto_RefineRemainCases(level, planNodes):
    for relid in planNodes:
        node = planNodes[relid]
        if node.level == level and node.done == False and node.module == -1:
            # both left and right module are from refine module
            # note that we assume the subplan (the root of which is the node)
            # is left deep tree, we only consider right child is a signle relation
            for rightRel in node.rel:
                rightRelid = pow(2, rightRel + 1)
                leftRelid = node.relid - rightRelid
                if planNodes[leftRelid].module == 2 or planNodes[leftRelid].module == 3:
                    node.module = 3  # refine internal module
                    node.leftChild = leftRelid
                    node.rightChild = rightRelid
                node.module = 3  # refine internal module
                node.leftChild = leftRelid
                node.rightChild = rightRelid


            #get vector feature
            if node.module != -1:
                tbsInLeft = num2array(node.leftChild, 2)
                tbsInRight = num2array(node.rightChild, 2)
                node.nodeInfo = GetJoinNodeInfo(tbsInLeft, tbsInRight, queryInfo)





class QueryInfo:
    def __int__(self):
        self.querytxt = ""
        self.table = []
        self.predicate = dict()
        self.joins = []
        self.joinAtt = dict() #join attribute at each table


def InitQueryInfo(query):
    tmpInfo = QueryInfo()
    tmpInfo.querytxt = query
    tmpInfo.table = GetTableInfo(query)
    tmpInfo.joins, joinAtt = GetJoinInfo(query, tmpInfo.table)
    predicate = GetFilterInfo(query, tmpInfo.table)
    tmpInfo.joinAtt = dict()
    tmpInfo.predicate = dict()

    for i in range(len(joinAtt)):
        tbIds = pow(2, i + 1)
        tmpInfo.joinAtt[tbIds] = joinAtt[i]

    for i in range(len(predicate)):
        tbIds = pow(2, i + 1)
        tmpInfo.predicate[tbIds] = predicate[i]

    #print(tmpInfo.table)
    #print(tmpInfo.joins)
    #print(tmpInfo.joinAtt)
    #print(tmpInfo.predicate)
    return  tmpInfo



def GetJoinNodeInfo(tbsInLeft, tbsInRight, queryInfo):

    for i in range(len(tbsInLeft)):
        if(tbsInLeft[i] == 1):
            tbsInLeft[i] = pow(2, i)

    for i in range(len(tbsInRight)):
        if(tbsInRight[i] == 1):
            tbsInRight[i] = pow(2, i)

    vaildJoins = getJoinFeatDic()
    joinNodeInfo = ""

    possJoins_left = set()
    possJoins_right = set()
    for relidLeft in tbsInLeft:
        if queryInfo.joinAtt.get(relidLeft) != None:
            for joinLeft in queryInfo.joinAtt[relidLeft]:
                for relidRight in tbsInRight:
                    if queryInfo.joinAtt.get(relidRight) != None:
                        for joinRight in queryInfo.joinAtt[relidRight]:
                            possJoins_left.add(joinLeft)
                            possJoins_right.add(joinRight)

    for vJoin in vaildJoins:
        if vJoin.find("=") == -1:
            continue
        l = vJoin[:vJoin.index("=")]
        r = vJoin[vJoin.index("=") + 1:]

        if l in possJoins_left and r in possJoins_right:
            joinNodeInfo = vJoin
            break
        if r in possJoins_left and l in possJoins_right:
            joinNodeInfo = vJoin
            break

    if joinNodeInfo == "":
        joinNodeInfo = "ILLEGAL_JOIN"
    return joinNodeInfo




def num2array(din, bit_width):
    bin_obj = bin(int(din))[2:]
    bin_str = bin_obj.rjust(bit_width, '0')
    o_arr = []
    for ii in range(len(bin_str)):
        o_arr.append(int(bin_str[len(bin_str) - ii - 1]))
    return o_arr





if __name__ == '__main__':
    input_dim = 256 # hidden unit of embed module
    mem_dim = 1024 #
    hidden_dim = 1024 #
    feature_dim = 70
    operat_dim = 4
    tb_dim = 11
    filter_dim = 18
    join_dim = 37
    card_dim = 2
    cuda_use = False
    GPU_no = 1
    min_label = 1.2
    max_label = 256668117

    #load content module
    contentModel = CONTENTModule(cuda_use, feature_dim, input_dim, mem_dim, hidden_dim,
                                 operat_dim, tb_dim, filter_dim, join_dim)
    path = os.path.join(os.path.abspath('.'), "/home/dbgroup/csfwang/reopt/LPCE-R/CONTENT_M.pth")
    contentModel.load_state_dict(torch.load(path, map_location='cpu'))
    callerContentModel = Caller_ContentModule(cuda_use, contentModel, min_label, max_label, operat_dim, tb_dim, filter_dim, join_dim)

    #load card module
    cardModel = CARDModule(cuda_use, feature_dim + card_dim, input_dim, input_dim * 5, hidden_dim,
                           operat_dim, tb_dim, filter_dim, join_dim, card_dim)
    path = os.path.join(os.path.abspath('.'), "/home/dbgroup/csfwang/reopt/LPCE-R/CARD_M.pth")
    cardModel.load_state_dict(torch.load(path, map_location='cpu'))
    callerCardModule = Caller_CardModule(cuda_use, cardModel, min_label, max_label,
                                         operat_dim, tb_dim, filter_dim, join_dim, card_dim)

    #load refine module
    refineModel = REFINEModule(cuda_use, feature_dim, input_dim, input_dim * 4, hidden_dim,
                          operat_dim, tb_dim, filter_dim, join_dim)
    path = os.path.join(os.path.abspath('.'), "/home/dbgroup/csfwang/reopt/LPCE-R/REFINE.pth")
    refineModel.load_state_dict(torch.load(path, map_location='cpu'))
    callerRefineModule = Caller_RefineModule(cuda_use, refineModel, min_label, max_label,
                                           operat_dim, tb_dim, filter_dim, join_dim)


    #Query = "SELECT COUNT(*) FROM title t,movie_companies mc,cast_info ci,movie_info mi,movie_info_idx mi_idx,movie_keyword mk,keyword k WHERE t.id=mc.movie_id AND t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND t.id=mk.movie_id AND mk.keyword_id=k.id AND t.production_year>1991 AND mc.id<1326734 AND ci.person_id<2784508 AND mi.info_type_id=93 AND mi_idx.id>605074 AND mk.id<3661441 AND k.keyword<81160;"
    #Query = "SELECT COUNT(*) FROM title t,movie_companies mc,cast_info ci,movie_info_idx mi_idx,movie_keyword mk WHERE t.id=mc.movie_id AND t.id=ci.movie_id AND t.id=mi_idx.movie_id AND t.id=mk.movie_id AND t.production_year>1887 AND ci.person_id=1758610 AND mi_idx.id<829146;"
    #Query = "SELECT COUNT(*) FROM title t,movie_companies mc,cast_info ci,movie_info_idx mi_idx,movie_keyword mk WHERE t.id=mc.movie_id AND t.id=ci.movie_id AND t.id=mi_idx.movie_id AND t.id=mk.movie_id AND t.production_year>1887 AND ci.person_id=1758610 AND mi_idx.id<829146;"
    #Query = "SELECT COUNT(*) FROM title t,movie_companies mc,cast_info ci,movie_info mi,movie_info_idx mi_idx,movie_keyword mk,keyword k,aka_title at,complete_cast cc WHERE t.id=mc.movie_id AND t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND t.id=mk.movie_id AND mk.keyword_id=k.id AND t.id=at.movie_id AND t.id=cc.movie_id AND mc.id<2604591 AND ci.role_id=9 AND mi_idx.id>803543 AND mk.id>4201634 AND k.keyword<81160 AND at.kind_id=4 AND cc.status_id=4;"
    #Query = "SELECT COUNT(*) FROM title t,movie_companies mc,cast_info ci,movie_info mi,movie_info_idx mi_idx,movie_keyword mk,keyword k,movie_link ml,complete_cast cc WHERE t.id=mc.movie_id AND t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND t.id=mk.movie_id AND mk.keyword_id=k.id AND t.id=ml.movie_id AND t.id=cc.movie_id AND t.production_year>1937 AND mc.id<287850 AND ci.person_id>1286761 AND mi.info_type_id=105 AND mi_idx.id<184574 AND mk.id<4312144 AND k.keyword>119295 AND cc.status_id=3;"
    #Query = "SELECT COUNT(*) FROM title t,movie_companies mc,cast_info ci,movie_info_idx mi_idx,movie_keyword mk,keyword k,movie_link ml WHERE t.id=mc.movie_id AND t.id=ci.movie_id AND t.id=mi_idx.movie_id AND t.id=mk.movie_id AND mk.keyword_id=k.id AND t.id=ml.movie_id AND t.production_year>2000 AND mc.id<841964 AND ci.role_id=11 AND mi_idx.id<345562 AND mk.id<973369 AND k.keyword>23112 AND ml.linked_movie_id<81121;"
    input = str(sys.argv[1])
    Query = input[input.index("SELECT"):input.index(";")+1]
    real_info = input[input.index("##")+2:input.index("###")]


    queryInfo = InitQueryInfo(Query)
    #doneRelids is a dictionary, recording the nodes that has been done executed
    doneRelids = getDoneRelids(real_info)



    numofRels = len(queryInfo.table)
    planNodes = dict()

    #Level 1
    #Init the nodes at level 1
    InitBaseNodes(numofRels, planNodes)
    #Get the node info executed
    GetDoneBaseRel(planNodes, doneRelids, queryInfo)

    #The node is done executed, send to card module
    GetBaseRelto_CardModule(planNodes, callerCardModule, min_label, max_label)
    #The node is not executed, send to content module
    GetBaseRelto_ContentModule(planNodes, queryInfo, callerContentModel, feature_dim)




    # getRelto_CardModule  both left and right nodes are executed node
    # getRelto_ContentModule  both right and left nodes are unexectued node
    # getRelto_RefineModule   at least one of left and right nodes is executed or refined node
    # case 1 getRelto_RefineConnectLayerModule: left children is executed node, right children is unexecuted node,
    # then firstly go through connect layer, then refine module
    # case 2 getRelto_RefineInternalModule: left children is refined node, right children is unexecuted node/refine node,
    # then go through refine module directly.

    #Hence, we need to train moudle
    #1. card module, both left and right child are executed nodes
    #   (1,2,3)
    #   /    \
    #  (1,3) (2)  (1,3) (2) are two executed node

    #2. content module, both left and right child are unexected nodes
    #   (1,2,3)
    #   /    \
    #  (1,3) (2)  (1,3) (2) are two unexecuted node

    #3. refined module, we need to consider two cases
    #  Case 1
    #   (1,2,3)
    #      |
    #   connect layer
    #   /    \
    #  (1,3) (2)
    #(1,3) is executed node from CARD module
    #(2) is unexecuted node from CONTENT module
    #Check the node at level n, which has to be estimated by REFINE module with connect layer
    #That is left child is executed node from CARD module, and right child is unexecuted node
    # from CONTENT module.

    #  Case 2
    #     (1,2,3,4)
    #     /      \
    #   (1,2,3)  (4)
    #      |
    #   connect layer (CNL-A)
    #   /    \
    #  (2)  (1,3)
    #(1,2,3) are refined node at refine internal, (2) is unexecuted node from content module
    #Check the node at level n, which has to be estimated by REFINE module
    #The node is upper level of connect layer at Refine Internal, which we say "RefineInternalModule"
    #Assume the connect layer connect to refine module at level i, Refine Internal denotes the
    #node at levels upper than i + 1.
    #That is left child is executed node from REFINE module,
    #and right child is unexecuted node from CONTENT module.

    #With above cases, we only refine nodes consider left deep tree, that is
    #left child can be from either CARD module, conect layer, or REFINE (Internal) module
    #but right child is just base relation, from content module.
    #The reason that we only consider the method to refine the node cardinality, due to same way,
    #We can make the cardinality estimation simple, and just train one REFINE module.
    #If we consider the busy tree that both left and right child are executed node,
    #then we need to train another REFINE module to match such case.


    for level in range(2, numofRels + 1):
        GetLevelnNodes(level, numofRels, planNodes)
        GetDoneLevelnRel(level, planNodes, doneRelids)
        GetLevelnRelto_CardModule(level, planNodes, queryInfo, callerCardModule, callerContentModel, min_label, max_label)
        GetLevelnRelto_ContentModule(level, planNodes, callerContentModel, feature_dim)
        GetLevelnRelto_RefineConnectLayerModule(level, planNodes, callerRefineModule)
        GetLevelnRelto_RefineInternalModule(level, planNodes, callerRefineModule)
        GetLevelnRel_HiddenState_ContentModule(level, planNodes, callerContentModel, feature_dim)

    cardResult = []
    vaildNum = 0
    for relid in planNodes:
        node = planNodes[relid]
        #print(" ", node.relid, node.rel, node.module, "    ",  node.nodeInfo, node.card)
        if node.nodeInfo.count("ILLEGAL_JOIN") > 0:
            vaildNum = vaildNum + 1
            #print(" ", node.relid, node.rel, node.module, "    ",  node.nodeInfo, format(planNodes[relid].card, '.1f'))
        if node.card >= 0:
           cardResult.append(int(planNodes[relid].card))
              #len(planNodes[relid].content_hidden_state), len(planNodes[relid].real_hidden_state), len(planNodes[relid].refine_hidden_state), "      ",  planNodes[relid].card)
    print("Total estimated cardinality : ", len(cardResult))
    print("Learned estimator outputs cardinality:")
    print(cardResult)



