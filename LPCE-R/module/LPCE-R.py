import torch
import torch.optim as optim
import sys 
sys.path.append("..") 
from lpce.loaddata_R import Dataloader
from lpce.cardModule import *
from lpce.contentModule import *
from lpce.refineModule import *
from lpce.trainer import *
from lpce import utils






# refined module, we need to consider three cases
#  Case 1
#   (1,2,3)
#      |
#   connect layer (CNL)
#   /    \
#  (1,3) (2)
# A) (1,3) and (2) are both executed node from card module - (CNL-A)
# This case means to refine nodes at level upper than i,
# The left and right child of level i - 1 are done.




#python3 LPCE-R mode epoch_num
#`mode` can be selected as `Train` for training, and `Test` for testing when a model is ready. 
#`epoch_num` is optimal setting, and as 30 epochs by default.
# `workload/queries/` has two datasets (6join/8join) for testing convenience.
if __name__ == '__main__':
    mode = 'Train'
    epoch_num = 30
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        assert(mode == 'Train' or mode == 'Test') 
        if len(sys.argv) == 3:
            epoch_num = int(sys.argv[2])

    input_dim = 256
    hidden_dim = 1024
    batch_size = 256
    lr_set = 0.0001

    cuda_use = False
    GPU_no = 1
    wd_set = 0.00001
    feature_dim = 70
    operat_dim = 4
    tb_dim = 11
    filter_dim = 18
    join_dim = 37
    card_dim = 2

    train_path = '../data/train10K/'
    test_path = '../workload/queries/6join'
    test_path2 = '../workload/queries/8join'
    train_size = 12000
    test_size = 500
    mode = 'Train'

    torch.cuda.set_device(GPU_no)
    max_label, min_label = utils.get_max_min_label('../data/train10K/')
    print("card domain: ", str(min_label)+ "(" + str(np.log(min_label))+ ")  " + str(max_label) + "(" + str(np.log(max_label)) + ")")

    dataset_size = train_size
    train_select, vaild_select = utils.random_split(dataset_size)


    if mode == 'Train':
        train_dataset = Dataloader(train_path, train_select, min_label, max_label)
        vaild_dataset = Dataloader(train_path, vaild_select, min_label, max_label)

    test_select_a = list(range(test_size))
    for i in range(test_size):
        test_select_a[i] = 1
    test_dataset = Dataloader(test_path, test_select_a, min_label, max_label)
    test_dataset2 = Dataloader(test_path2, test_select_a, min_label, max_label)



    if mode == 'Train':
        #modela = CARDModule(cuda_use, feature_dim+2, input_dim, input_dim * 5, hidden_dim)
        mem_dim = input_dim * 5
        modela = CARDModule(cuda_use, feature_dim + card_dim, input_dim, mem_dim, hidden_dim, operat_dim, tb_dim, filter_dim, join_dim, card_dim)
        modela.load_state_dict(torch.load('../model/card_module.pth'))

        #modelb = CONTENTModule(cuda_use, feature_dim, input_dim, input_dim * 4, hidden_dim)
        mem_dim = input_dim * 4
        modelb = CONTENTModule(cuda_use, feature_dim, input_dim, mem_dim, hidden_dim, operat_dim, tb_dim, filter_dim, join_dim)
        modelb.load_state_dict(torch.load('../model/content_module.pth'))

        mem_dim = input_dim * 4
        #modelc = REFINEModule(cuda_use, feature_dim, input_dim, input_dim * 4, hidden_dim)
        modelc = REFINEModule(cuda_use, feature_dim, input_dim, mem_dim, hidden_dim, operat_dim, tb_dim, filter_dim, join_dim)
        pretrained_dict = torch.load('../model/content_module.pth')
        model_dict = modelc.state_dict()
        pretrained_dict = {k: v for k, v in pretrained_dict.items() if k in model_dict}
        model_dict.update(pretrained_dict)
        modelc.load_state_dict(model_dict)

        optimizer = optim.Adam(filter(lambda p: p.requires_grad, modelc.parameters()), lr=lr_set, weight_decay=wd_set)
        trainer = HyTrainer(cuda_use,  modela, modelb, modelc, optimizer, min_label, max_label)
        for epoch in range(epoch_num):
            loss = trainer.train(train_dataset, batch_size)
            print("  8-join Test")
            trainer.test(vaild_dataset, 2)
            trainer.test(vaild_dataset, 4)
            trainer.test(vaild_dataset, 6)
            torch.save(modelc.state_dict(), '../model/'+ 'refine_module.pth')



    if mode == 'Test':

        #modela = CARDModule(cuda_use, feature_dim+2, input_dim, input_dim * 5, hidden_dim)
        mem_dim = input_dim * 5
        modela = CARDModule(cuda_use, feature_dim + card_dim, input_dim, mem_dim, hidden_dim, operat_dim, tb_dim, filter_dim, join_dim, card_dim)
        modela.load_state_dict(torch.load('../model/card_module.pth'))

        #modelb = CONTENTModule(cuda_use, feature_dim, input_dim, input_dim * 4, hidden_dim)
        mem_dim = input_dim * 4
        modelb = CONTENTModule(cuda_use, feature_dim, input_dim, mem_dim, hidden_dim, operat_dim, tb_dim, filter_dim, join_dim)
        modelb.load_state_dict(torch.load('../model/content_module.pth'))

        #modelc = REFINEModule(cuda_use, feature_dim, input_dim, input_dim * 4, hidden_dim)
        mem_dim = input_dim * 4
        #modelc = REFINEModule(cuda_use, feature_dim, input_dim, input_dim * 4, hidden_dim)
        modelc = REFINEModule(cuda_use, feature_dim, input_dim, mem_dim, hidden_dim, operat_dim, tb_dim, filter_dim, join_dim)
        modelc.load_state_dict('../model/refine_module.pth')

        optimizer = optim.Adam(filter(lambda p: p.requires_grad, modelc.parameters()), lr=lr_set, weight_decay=wd_set)
        trainer = HyTrainer(cuda_use,  modela, modelb, modelc, optimizer, min_label, max_label)

        print("\n 6-join Test")
        qerror62 = trainer.test(test_dataset, 2)
        qerror64 = trainer.test(test_dataset, 4)
        qerror65 = trainer.test(test_dataset, 5)
        print("\n 8-join Test")
        qerror82 = trainer.test(test_dataset2, 2)
        qerror84 = trainer.test(test_dataset2, 4)
        qerror86 = trainer.test(test_dataset2, 6)