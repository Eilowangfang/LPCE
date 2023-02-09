import torch
import torch.optim as optim
import sys 
sys.path.append("..") 
from lpce.loaddata_R import Dataloader
from lpce.cardModule import *
from lpce.trainer_card import *
from lpce import utils






if __name__ == '__main__':
    mode = 'Train'
    epoch_num = 30
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        assert(mode == 'Train' or mode == 'Test') 
        if len(sys.argv) == 3:
            epoch_num = int(sys.argv[2])

    embed_dim = 256 # hidden unit of embed module
    mem_dim = 1280 #
    hidden_dim = 1024 #
    batch_size = 50 #
    lr_set = 0.0001 #
    operat_dim = 4
    tb_dim = 11
    filter_dim = 18
    join_dim = 37
    card_dim = 2

    cuda_use = False
    GPU_no = 1
    wd_set = 0.00001
    feature_dim = 72
    train_path = '../data/train10K'
    #test_path = '../queries/8join/'
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
    else:
        test_dataset = Dataloader(train_path, vaild_select, min_label, max_label)


    if mode == 'Train':
        model = CARDModule(cuda_use, feature_dim, embed_dim, mem_dim, hidden_dim, operat_dim, tb_dim, filter_dim, join_dim, card_dim)
        optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=lr_set, weight_decay=wd_set)
        trainer = Trainer_CARDModule(cuda_use, model, optimizer, min_label, max_label)
        for epoch in range(epoch_num):
            loss = trainer.train(train_dataset, batch_size)

            final_error = trainer.test(vaild_dataset)
            if epoch % 10 == 0:
                torch.save(model.state_dict(), 'CARD_M'+str(epoch)+'.pth')

        torch.save(model.state_dict(), '../model/'+ 'card_module.pth')


    if mode == 'Test':
        model = CARDModule(cuda_use, feature_dim, input_dim, mem_dim, hidden_dim)
        model.load_state_dict(torch.load('./card_module.pth'))
        optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=lr_set, weight_decay=wd_set)
        trainer = Trainer_CARDModule(cuda_use, model, optimizer, min_label, max_label)
        qerror = trainer.test(test_dataset)