
import os
import torch
import torchvision as tv
import numpy as np

from torch.utils.data import DataLoader

from src.utils import makedirs, tensor2cuda, load_model, LabelDict
from argument import parser
from src.visualization import VanillaBackprop
from src.attack import FastGradientSignUntargeted
from src.model.madry_model import WideResNet

import matplotlib.pyplot as plt 

max_epsilon = 4.7

perturbation_type = 'l2'

out_num = 5

img_folder = 'img'
makedirs(img_folder)

args = parser()

label_dict = LabelDict(args.dataset)

te_dataset = tv.datasets.CIFAR10(args.data_root, 
                               train=False, 
                               transform=tv.transforms.ToTensor(), 
                               download=True)

te_loader = DataLoader(te_dataset, batch_size=args.batch_size, shuffle=False, num_workers=4)


for data, label in te_loader:

    data, label = tensor2cuda(data), tensor2cuda(label)


    break


adv_list = []
pred_list = []

with torch.no_grad():

    model = WideResNet(depth=34, num_classes=10, widen_factor=10, dropRate=0.0)

    load_model(model, args.load_checkpoint)

    if torch.cuda.is_available():
        model.cuda()

    attack = FastGradientSignUntargeted(model, 
                                        max_epsilon, 
                                        args.alpha, 
                                        min_val=0, 
                                        max_val=1, 
                                        max_iters=args.k, 
                                        _type=perturbation_type)

   
    adv_data = attack.perturb(data, label, 'mean', False)

    output = model(adv_data, _eval=True)
    pred = torch.max(output, dim=1)[1]
    adv_list.append(adv_data.cpu().numpy().squeeze() * 255.0)  # (N, 28, 28)
    pred_list.append(pred.cpu().numpy())

data = data.cpu().numpy().squeeze()  # (N, 28, 28)
data *= 255.0
label = label.cpu().numpy()

adv_list.insert(0, data)

pred_list.insert(0, label)


types = ['Original', 'Your Model']

fig, _axs = plt.subplots(nrows=len(adv_list), ncols=out_num)

axs = _axs

for j, _type in enumerate(types):
    axs[j, 0].set_ylabel(_type)

    for i in range(out_num):
        axs[j, i].set_xlabel('%s' % label_dict.label2class(pred_list[j][i]))
        img = adv_list[j][i]
        # print(img)
        img = np.transpose(img, (1, 2, 0))

        img = img.astype(np.uint8)
        axs[j, i].imshow(img)

        axs[j, i].get_xaxis().set_ticks([])
        axs[j, i].get_yaxis().set_ticks([])

plt.tight_layout()
plt.savefig(os.path.join(img_folder, 'cifar_large_%s_%s.jpg' % (perturbation_type, args.affix)))
# plt.savefig(os.path.join(img_folder, 'test_%s.jpg' % (args.affix)))


# types = ['Original', 'Standard', r'$l_{\infty}$-trained', r'$l_2$-trained']


# model_checkpoints = ['checkpoint/cifar-10_std/checkpoint_76000.pth',
#                      'checkpoint/cifar-10_linf/checkpoint_76000.pth', 
#                      'checkpoint/cifar-10_l2/checkpoint_76000.pth']

# adv_list = []
# pred_list = []

# max_epsilon = 4

# perturbation_type = 'l2'

# with torch.no_grad():
#     for checkpoint  in model_checkpoints:

#         model = WideResNet(depth=34, num_classes=10, widen_factor=10, dropRate=0.0)

#         load_model(model, checkpoint)

#         if torch.cuda.is_available():
#             model.cuda()

#         attack = FastGradientSignUntargeted(model, 
#                                             max_epsilon, 
#                                             args.alpha, 
#                                             min_val=0, 
#                                             max_val=1, 
#                                             max_iters=args.k, 
#                                             _type=perturbation_type)

       
#         adv_data = attack.perturb(data, label, 'mean', False)

#         output = model(adv_data, _eval=True)
#         pred = torch.max(output, dim=1)[1]
#         adv_list.append(adv_data.cpu().numpy().squeeze() * 255.0)  # (N, 28, 28)
#         pred_list.append(pred.cpu().numpy())

# data = data.cpu().numpy().squeeze()  # (N, 28, 28)
# data *= 255.0
# label = label.cpu().numpy()

# adv_list.insert(0, data)

# pred_list.insert(0, label)

# out_num = 5

# fig, _axs = plt.subplots(nrows=len(adv_list), ncols=out_num)

# axs = _axs

# for j, _type in enumerate(types):
#     axs[j, 0].set_ylabel(_type)

#     for i in range(out_num):
#         axs[j, i].set_xlabel('%s' % label_dict.label2class(pred_list[j][i]))
#         img = adv_list[j][i]
#         # print(img)
#         img = np.transpose(img, (1, 2, 0))

#         img = img.astype(np.uint8)
#         axs[j, i].imshow(img)

#         axs[j, i].get_xaxis().set_ticks([])
#         axs[j, i].get_yaxis().set_ticks([])

# plt.tight_layout()
# plt.savefig(os.path.join(img_folder, 'cifar_large_%s_%s.jpg' % (perturbation_type, args.affix)))