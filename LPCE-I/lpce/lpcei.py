import torch
import torch.optim as optim
from lpce.loaddata import Dataloader
from lpce.sru import *
from lpce.trainer import *
from lpce import utils

#0 1 0 0 0                                      5
#0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0        20
#0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0.8990825688073395
#0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0          48
#0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 43



# def estimate(list):
#
#     result=0
#     for i in list:
#         result+=i
#
#
#     input_dim = 128 # hidden unit of embed module
#     mem_dim = 384 #
#     hidden_dim = 512 #
#     lr_set = 0.0001 #
#     cuda_use = True
#     GPU_no = 1
#     wd_set = 0.00001
#     feature_dim = 116
#     test_path = './data/testdata_scale'
#     test_size = 500
#     #
#     torch.cuda.set_device(GPU_no)
#     max_label, min_label = utils.get_max_min_label('/usr/lib/python3.7/data/traindata')
#     # print("card domain: ", np.log(min_label), np.log(max_label))
#     #
#     # test_select = list(range(test_size))
#     # for i in range(test_size):
#     #     test_select[i] = 1
#     # test_dataset = Dataloader(test_path, test_select, False)
#     #
#     # model = SRU(cuda_use, feature_dim, input_dim, mem_dim, hidden_dim)
#     # model.load_state_dict(torch.load('./data/LPCE.pth'))
#     # optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=lr_set, weight_decay=wd_set)
#     # trainer = Trainer(cuda_use, model, optimizer, min_label, max_label)
#     # qerror = trainer.test(test_dataset, False)
#     # meanerror = np.mean(qerror)
#     value = testsum(list)
#
#     return value

if __name__ == '__main__':

    input_dim = 128 # hidden unit of embed module
    mem_dim = 384 #
    hidden_dim = 512 #
    batch_size = 100 #
    lr_set = 0.0001 #

    epoch_num = 2
    cuda_use = True
    GPU_no = 1
    wd_set = 0.00001
    feature_dim = 74
    train_path = './data/10w_0-8join/'
    test_path = './data/10w_0-8join/6join_test_500/'
    train_size = 100000
    test_size = 500
    mode = 'Train'

    torch.cuda.set_device(GPU_no)
    max_label, min_label = utils.get_max_min_label('./data/10w_0-8join/')
    print("card domain: ", np.log(min_label), np.log(max_label))

    dataset_size = train_size
    train_select, vaild_select = utils.random_split(dataset_size)
    if mode == 'Train':
        train_dataset = Dataloader(train_path, train_select, True)
        vaild_dataset = Dataloader(train_path, vaild_select, True)

    test_select = list(range(test_size))
    for i in range(test_size):
        test_select[i] = 1
    test_dataset = Dataloader(test_path, test_select, False)


    if mode == 'Train':


        model = SRU(cuda_use, feature_dim, input_dim, mem_dim, hidden_dim)
        optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=lr_set, weight_decay=wd_set)
        trainer = Trainer(cuda_use, model, optimizer, min_label, max_label)
        for epoch in range(epoch_num):
            loss = trainer.train(train_dataset, batch_size)
            torch.save(model.state_dict(), 'LPCE'+'_'+str(epoch)+'.pth')

            #train_log = open('vaild.log', 'a')
            #final_error = trainer.test_batch(vaild_dataset)
            #train_log.write(str(epoch) + ',' + str(final_error) + " \n")

            test_log = open('test.log', 'a')
            test_log.write("\nEpoch " + str(epoch) + ": \n")
            trainer.test(test_dataset, False)



    if mode == 'Test':
        model = SRU(cuda_use, feature_dim, input_dim, mem_dim, hidden_dim)
        model.load_state_dict(torch.load('./data/LPCE.pth'))
        optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=lr_set, weight_decay=wd_set)
        trainer = Trainer(cuda_use, model, optimizer, min_label, max_label)
        for epoch in range(1):
            #trainer.test_batch(test_dataset)
            qerror = trainer.test(test_dataset, False)



