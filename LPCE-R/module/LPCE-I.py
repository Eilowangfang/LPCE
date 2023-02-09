import torch
import torch.optim as optim
import numpy as np
import sys 
sys.path.append("..") 
from lpce.loaddata_I import Dataloader
from lpce.contentModule import *
from lpce.trainer_content import *
from lpce import utils



#python3 LPCE-I.py mode epoch
if __name__ == '__main__':
    mode = 'Train'
    epoch_num = 100
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        assert(mode == 'Train' or mode == 'Test') 
        if len(sys.argv) == 3:
            epoch_num = int(sys.argv[2])

    #embed_dim is the hidden unit of embed module
    #mem_dim is the hidden unit of SRU module
    #output_dim is the hidden unit of output module
    embed_dim = 256
    mem_dim = 1024 #
    output_dim = 1024 #
    batch_size = 50 #
    lr_set = 0.0001 #
    operat_dim = 4
    tb_dim = 11
    filter_dim = 18
    join_dim = 37
    cuda_use = True
    GPU_no = 1
    wd_set = 0.00001
    feature_dim = 70
    train_path = '../data/train10K'
    train_size = 11000

    torch.cuda.set_device(GPU_no)
    max_label, min_label = utils.get_max_min_label('../data/train10K')
    print("card domain: ", str(min_label)+ "(" + str(np.log(min_label))+ ")  " + str(max_label) + "(" + str(np.log(max_label)) + ")")
    dataset_size = train_size
    train_select, vaild_select = utils.random_split(dataset_size)
    if mode == 'Train':
        #prepare training set
        train_dataset = Dataloader(train_path, train_select)
        vaild_dataset = Dataloader(train_path, vaild_select)
    else:
         #prepare testing set
        test_dataset = Dataloader(train_path, vaild_select)
   

    if mode == 'Train':
        model = CONTENTModule(cuda_use, feature_dim, embed_dim, mem_dim, output_dim, operat_dim, tb_dim, filter_dim, join_dim)
        optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=lr_set, weight_decay=wd_set)
        trainer = Trainer_ContentModule(cuda_use, model, optimizer, min_label, max_label)
        for epoch in range(epoch_num):
            loss = trainer.train(train_dataset, batch_size)
            print("Evaluation:")
            trainer.test(vaild_dataset)
        torch.save(model.state_dict(), '../model/'+ 'content_module.pth')


    if mode == 'Test':
        model = CONTENTModule(cuda_use, feature_dim, embed_dim, mem_dim, output_dim, operat_dim, tb_dim, filter_dim, join_dim)
        model.load_state_dict(torch.load('../model/content_module.pth'))
        optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=lr_set, weight_decay=wd_set)
        trainer = Trainer_ContentModule(cuda_use, model, optimizer, min_label, max_label)
        qerror = trainer.test(test_dataset)