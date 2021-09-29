import torch
import torch.optim as optim
from lpce.loaddata import Dataloader
from lpce.cardmoudle import *
from lpce.contmodule import *
from lpce.refinemodule import *
from lpce.hytrainer import *
from lpce import utils





if __name__ == '__main__':

    input_dim = 256 # hidden unit of embed module
    hidden_dim = 1024 #
    batch_size = 50 #
    lr_set = 0.0001 #

    epoch_num = 20
    cuda_use = False
    GPU_no = 1
    wd_set = 0.00001
    feature_dim = 70
    train_path = './data/train10K/'
    test_path = './queries/6join'
    test_path2 = './queries/8join'
    train_size = 12000
    test_size = 500
    mode = 'Train'

    torch.cuda.set_device(GPU_no)
    max_label, min_label = utils.get_max_min_label('./data/6-8join_10K/')
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
        modela = CONTENTmodule(cuda_use, feature_dim, input_dim, input_dim * 4, hidden_dim)
        modela.load_state_dict(torch.load('MODELA.pth'))

        modelb = CARDModule(cuda_use, feature_dim+2, input_dim, input_dim * 5, hidden_dim)
        modelb.load_state_dict(torch.load('MODELB.pth'))

        modelc = REFINEModule(cuda_use, feature_dim, input_dim, input_dim * 4, hidden_dim)


        pretrained_dict = torch.load('./MODELA.pth')
        model_dict = modelc.state_dict()
        pretrained_dict = {k: v for k, v in pretrained_dict.items() if k in model_dict}
        model_dict.update(pretrained_dict)
        modelc.load_state_dict(model_dict)
        optimizer = optim.Adam(filter(lambda p: p.requires_grad, modelc.parameters()), lr=lr_set, weight_decay=wd_set)
        trainer = HyTrainer(cuda_use,  modela, modelb, modelc, optimizer, min_label, max_label)
        for epoch in range(epoch_num):
            loss = trainer.train(train_dataset, batch_size)
            print("  6-join Test")
            trainer.test(test_dataset, 2)
            trainer.test(test_dataset, 4)
            trainer.test(test_dataset, 5)
            print("\n 8-join Test")
            trainer.test(test_dataset2, 2)
            trainer.test(test_dataset2, 4)
            trainer.test(test_dataset2, 6)
            print("\n")

        torch.save(modelc.state_dict(), 'MODELC.pth')












    if mode == 'Test':

        modela = CARDModule(cuda_use, feature_dim, input_dim, input_dim * 4, hidden_dim)
        modela.load_state_dict(torch.load('MODELA.pth'))

        modelb = CONTENTmodule(cuda_use, feature_dim+2, input_dim, input_dim * 5, hidden_dim)
        modelb.load_state_dict(torch.load('MODELB.pth'))

        modelc = REFINEModule(cuda_use, feature_dim, input_dim, input_dim * 4, hidden_dim)
        modelc.load_state_dict(torch.load('MODELC.pth'))


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


