"""
Common utilities for training.


Note: this code is for research i.e. quick experimentation; it has minimal
comments for now, but if we see further interest from the community -- we will
add further comments, unify the style, improve efficiency and add unittests.

@contactrika

"""
import os
import platform
from datetime import datetime

import numpy as np
import torch
import wandb


def object_to_str(obj):
    # Print all fields of the given object as text in tensorboard.
    text_str = ''
    for member in vars(obj):
        # Tensorboard uses markdown-like formatting, hence '  \n'.
        text_str += f'  \n{str(member):s}={str(getattr(obj, member)):s}'
    return text_str


def init_train(algo, args, tags=None):
    np.set_printoptions(precision=4, linewidth=150, suppress=True)
    if platform.system() == 'Linux':
        os.environ['IMAGEIO_FFMPEG_EXE'] = '/usr/bin/ffmpeg'
    logdir = None
    if args.logdir is not None:
        tstamp = datetime.strftime(datetime.today(), '%y%m%d_%H%M%S')
        lst = [algo, tstamp, args.env]
        subdir = '_'.join(lst)
        logdir = os.path.join(os.path.expanduser(args.logdir), subdir)
        if args.use_wandb:
            wandb.init(config=vars(args), project='dedo',
                       name=logdir, tags=tags)
            wandb.init(sync_tensorboard=False)
            try:  # patch only once, if more than one run, ignore error
                wandb.tensorboard.patch(tensorboardX=True, pytorch=True)
            except ValueError:
                pass
    device = args.device
    if not torch.cuda.is_available():
        device = 'cpu'
    return logdir, device
