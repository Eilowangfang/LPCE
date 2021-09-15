import torch
import torch.optim as optim
from lpce.loaddata import Dataloader
from lpce.sru import *
from lpce.trainer import *
from lpce import utils



if __name__ == '__main__':

    #embed_dim is the hidden unit of embed module
    #mem_dim is the hidden unit of SRU module
    #output_dim is the hidden unit of output module
    embed_dim = 256
    mem_dim = 1024 #
    output_dim = 1024 #
    batch_size = 50 #
    lr_set = 0.0001 #

    epoch_num = 60
    cuda_use = False
    GPU_no = 1
    wd_set = 0.00001
    feature_dim = 70
    train_path = './data/train_10K'
    test_path = './queries/8join'
    train_size = 11000
    test_size = 520
    mode = 'Train'


    torch.cuda.set_device(GPU_no)
    max_label, min_label = utils.get_max_min_label('./data/train_10K')
    print("card domain: ", str(min_label)+ "(" + str(np.log(min_label))+ ")  " + str(max_label) + "(" + str(np.log(max_label)) + ")")
    #prepare training set
    dataset_size = train_size
    train_select, vaild_select = utils.random_split(dataset_size)
    if mode == 'Train':
        train_dataset = Dataloader(train_path, train_select, True)
        vaild_dataset = Dataloader(train_path, vaild_select, True)
    #prepare testing set
    test_select = list(range(test_size))
    for i in range(test_size):
        test_select[i] = 1
    test_dataset = Dataloader(test_path, test_select, False)

    if mode == 'Train':
        model = SRU(cuda_use, feature_dim, embed_dim, mem_dim, output_dim)
        optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=lr_set, weight_decay=wd_set)
        trainer = Trainer(cuda_use, model, optimizer, min_label, max_label)
        for epoch in range(epoch_num):
            loss = trainer.train(train_dataset, batch_size)
            torch.save(model.state_dict(), 'modela_'+str(epoch)+'.pth')

            print("Evaluation:")
            trainer.test(vaild_dataset)
            print("Test:")
            trainer.test_batch(test_dataset)

    if mode == 'Test':
        model = SRU(cuda_use, feature_dim, embed_dim, mem_dim, output_dim)
        model.load_state_dict(torch.load('./LPCEI_50.pth'))
        optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=lr_set, weight_decay=wd_set)
        trainer = Trainer(cuda_use, model, optimizer, min_label, max_label)
        qerror = trainer.test(test_dataset)



