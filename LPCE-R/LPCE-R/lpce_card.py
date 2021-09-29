import torch
import torch.optim as optim
from lpce.loaddata import Dataloader
from lpce.contmodule import *
from lpce.trainer_card import *
from lpce import utils


if __name__ == '__main__':

    input_dim = 256 # hidden unit of embed module
    mem_dim = 1280 #
    hidden_dim = 1024 #
    batch_size = 50 #
    lr_set = 0.0001 #

    epoch_num = 20
    cuda_use = True
    GPU_no = 1
    wd_set = 0.00001
    feature_dim = 72
    train_path = './data/train10K'
    test_path = './queries/6join/'
    test_path2 = './queries/8join/'
    train_size = 12000
    test_size = 500
    mode = 'Test'

    torch.cuda.set_device(GPU_no)
    max_label, min_label = utils.get_max_min_label('./data/6-8join_10K/')
    print("card domain: ", str(min_label)+ "(" + str(np.log(min_label))+ ")  " + str(max_label) + "(" + str(np.log(max_label)) + ")")

    dataset_size = train_size
    train_select, vaild_select = utils.random_split(dataset_size)
    if mode == 'Train':
        train_dataset = Dataloader(train_path, train_select, min_label, max_label)
        vaild_dataset = Dataloader(train_path, vaild_select, min_label, max_label)

    test_select = list(range(test_size))
    for i in range(test_size):
        test_select[i] = 1
    test_dataset = Dataloader(test_path, test_select, min_label, max_label)
    test_dataset2 = Dataloader(test_path2, test_select, min_label, max_label)


    if mode == 'Train':
        model = CONTENTmodule(cuda_use, feature_dim, input_dim, mem_dim, hidden_dim)
        optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=lr_set, weight_decay=wd_set)
        trainer = Trainer_CARDmodule(cuda_use, model, optimizer, min_label, max_label)
        for epoch in range(epoch_num):
            loss = trainer.train(train_dataset, batch_size)

            final_error = trainer.test(test_dataset)
            trainer.test(test_dataset2)
        torch.save(model.state_dict(), 'MODLEB.pth')



    if mode == 'Test':
        model = CONTENTmodule(cuda_use, feature_dim, input_dim, mem_dim, hidden_dim)
        model.load_state_dict(torch.load('./MODLEB.pth'))
        optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=lr_set, weight_decay=wd_set)
        trainer = Trainer_CARDmodule(cuda_use, model, optimizer, min_label, max_label)
        qerror = trainer.test(test_dataset)
        qerror2 = trainer.test(test_dataset2)


