import torch
import torch.optim as optim
from lpce.loaddata import Dataloader
from lpce.sru import *
from lpce.trainer import *
from lpce import utils
from lpce.trainer_distll import *
from lpce.sru_distill import *


if __name__ == '__main__':

    #embed_dim is the hidden unit of embed module
    #mem_dim is the hidden unit of SRU module
    #output_dim is the hidden unit of output module
    embed_dim = 64 # model parameters for student model
    mem_dim = 256 # model parameters for student model
    output_dim = 1024 #
    batch_size = 50 #
    lr_set = 0.0001 #
    embed_dim_teacher = 256 # model parameters for teacher model
    mem_dim_teacher = 1024 # model parameters for teacher model

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
        mode_teacher = SRU(cuda_use, feature_dim, embed_dim_teacher, mem_dim_teacher, output_dim)
        mode_teacher.load_state_dict(torch.load('TEACHER.pth'))

        model_student = SRU_distill(cuda_use, feature_dim, embed_dim, mem_dim, output_dim, embed_dim_teacher)
        optimizer = optim.Adam(filter(lambda p: p.requires_grad, model_student.parameters()), lr=lr_set, weight_decay=wd_set)
        trainer = DistillTrainer(cuda_use, model_student, mode_teacher, optimizer, min_label, max_label)
        for epoch in range(epoch_num):
            loss = trainer.train(train_dataset, batch_size)
            torch.save(model_student.state_dict(), 'modela_'+str(epoch)+'.pth')

            print("Evaluation:")
            trainer.test(vaild_dataset)
            print("Test:")
            trainer.test_batch(test_dataset)





    if mode == 'Test':
        model = SRU_distill(cuda_use, feature_dim, embed_dim, mem_dim, output_dim, embed_dim_teacher)
        pretrained_dict = torch.load('DISTILL.pth')
        model_dict = model.state_dict()
        pretrained_dict = {k: v for k, v in pretrained_dict.items() if k in model_dict}
        model_dict.update(pretrained_dict)
        model.load_state_dict(model_dict)
        optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=lr_set, weight_decay=wd_set)
        trainer = Trainer(cuda_use, model, optimizer, min_label, max_label)
        for epoch in range(1):
            trainer.test(test_dataset)


