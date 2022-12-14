from __future__ import absolute_import, division, print_function

import os
import argparse
import torch
import torch.optim as optim
from models.UCPR.preprocess.dataset import DataLoader, Dataset
from models.UCPR.utils import *
from models.UCPR.preprocess.transe_model import KnowledgeEmbedding
import json
import sys
logger = None


def train(args):
    dataset_name = args.dataset
    train_set = Dataset(args,set_name='train')
    val_set = Dataset(args,set_name='valid')
    train_loader = DataLoader(train_set, args.batch_size)
    valid_loader = DataLoader(val_set, args.batch_size)
    review_to_train = len(train_set.review.data) * args.epochs + 1

    model = KnowledgeEmbedding(args, train_loader).to(args.device)
    logger.info('Parameters:' + str([i[0] for i in model.named_parameters()]))
    optimizer = optim.SGD(model.parameters(), lr=args.lr)
    steps = 0
    smooth_loss = 0.0

    best_val_loss = sys.maxsize
    train_loss_history = []
    val_loss_history = []
    for epoch in range(1, args.epochs + 1):
        train_loader.reset()
        while train_loader.has_next():
            # Set learning rate.
            lr = args.lr * max(1e-4, 1.0 - train_loader.finished_review_num / float(review_to_train))
            for pg in optimizer.param_groups:
                pg['lr'] = lr

            # Get training batch.
            batch_idxs = train_loader.get_batch()
            batch_idxs = torch.from_numpy(batch_idxs).to(args.device)

            # Train models.
            optimizer.zero_grad()
            train_loss = model(batch_idxs)
            train_loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), args.max_grad_norm)
            optimizer.step()
            smooth_loss += train_loss.item() / args.steps_per_checkpoint

            steps += 1
            if steps % args.steps_per_checkpoint == 0:
                logger.info('Epoch: {:02d} | '.format(epoch) +
                            'Review: {:d}/{:d} | '.format(train_loader.finished_review_num, review_to_train) +
                            'Lr: {:.5f} | '.format(lr) +
                            'Smooth loss: {:.5f}'.format(smooth_loss))
                train_loss_history.append(smooth_loss)
                smooth_loss = 0.0
        if epoch % 10 == 0:
            if args.do_validation:
                model.eval()
                total_val_loss = 0
                cnt = 0
                valid_loader.reset()
                while valid_loader.has_next():
                    # Get valid batch.
                    batch_idxs = valid_loader.get_batch()
                    batch_idxs = torch.from_numpy(batch_idxs).to(args.device)
                    valid_loss = model(batch_idxs)
 
                    total_val_loss += valid_loss.item()
                    cnt += 1

                avg_valid_loss = total_val_loss/max(cnt, 1)
                logger.info('Epoch: {:02d} | '.format(epoch) +
                                    'Validation loss: {:.5f}'.format(avg_valid_loss))
                val_loss_history.append(avg_valid_loss)
                if avg_valid_loss < best_val_loss:
                    best_val_loss = avg_valid_loss
                    
                    torch.save(model.state_dict(), '{}/transe_best_model.ckpt'.format(args.log_dir))
                model.train()
        torch.save(model.state_dict(), '{}/transe_model_sd_epoch_{}.ckpt'.format(args.log_dir, epoch))
    
    makedirs(dataset_name)
    with open(TRANSE_TEST_METRICS_FILE_PATH[dataset_name], 'w') as f:
        json.dump( {'valid_loss': best_val_loss, 
                'valid_loss_history': val_loss_history,
                'train_loss_history':train_loss_history } ,f)
    

def extract_embeddings(args, dataset):
    """Note that last entity embedding is of size [vocab_size+1, d]."""
    dataset_name = args.dataset
    os.makedirs(args.log_dir, exist_ok=True)
    
    model_file = '{}/transe_best_model.ckpt'.format(args.log_dir)
    
    print('Load embeddings', model_file)
    state_dict = torch.load(model_file, map_location=lambda storage, loc: storage)
    embeds = {}
    for entity_name in dataset.entity_names:
        embeds[entity_name] = state_dict[f'{entity_name}.weight'].cpu().data.numpy()[:-1]


    embeds[INTERACTION[dataset_name]] = (
        state_dict[INTERACTION[dataset_name]].cpu().data.numpy()[0],
        state_dict[f'{INTERACTION[dataset_name]}_bias.weight'].cpu().data.numpy()
    )
    for relation_name in dataset.other_relation_names:
            embeds[relation_name] = (
            state_dict[f'{relation_name}'].cpu().data.numpy()[0],
            state_dict[f'{relation_name}_bias.weight'].cpu().data.numpy()
        )
    save_embed(dataset_name, embeds)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, default=LFM1M, help=f'One of [{ML1M}, {LFM1M}, beauty, cd, cell, clothing]')
    parser.add_argument('--name', type=str, default='train_transe_model', help='models name.')
    parser.add_argument('--seed', type=int, default=123, help='random seed.')
    parser.add_argument('--gpu', type=str, default='0', help='gpu device.')
    parser.add_argument('--epochs', type=int, default=30, help='number of epochs to train.')
    parser.add_argument('--batch_size', type=int, default=64, help='batch size.')
    parser.add_argument('--lr', type=float, default=0.5, help='learning rate.')
    parser.add_argument('--weight_decay', type=float, default=0, help='weight decay for adam.')
    parser.add_argument('--l2_lambda', type=float, default=0, help='l2 lambda')
    parser.add_argument('--max_grad_norm', type=float, default=5.0, help='Clipping gradient.')
    parser.add_argument('--embed_size', type=int, default=100, help='knowledge embedding size.')
    parser.add_argument('--num_neg_samples', type=int, default=5, help='number of negative samples.')
    parser.add_argument('--steps_per_checkpoint', type=int, default=200, help='Number of steps for checkpoint.')
    parser.add_argument('--do_validation', type=bool, default=True, help='Whether to perform validation')



    args = parser.parse_args()
    os.makedirs(LOG_DATASET_DIR[args.dataset], exist_ok=True)
    with open(os.path.join(LOG_DATASET_DIR[args.dataset], f'{TRANSE_HPARAMS_FILE}'), 'w') as f:
        import json
        import copy
        args_dict = dict()
        for x,y in copy.deepcopy(args._get_kwargs()):
            args_dict[x] = y
        if 'device' in args_dict:
            del args_dict['device']
        json.dump(args_dict,f)


    os.environ['CUDA_VISIBLE_DEVICES'] = args.gpu
    print(f'Set to gpu:{args.gpu}')
    args.device = torch.device(f'cuda:0') if torch.cuda.is_available() else 'cpu'
    print(TMP_DIR[args.dataset])
    args.log_dir = os.path.join(TMP_DIR[args.dataset], args.name)
    if not os.path.isdir(args.log_dir):
        os.makedirs(args.log_dir)

    global logger
    logger = get_logger(args.log_dir + '/train_log.txt')
    logger.info(args)

    set_random_seed(args.seed)
    dataset = load_dataset(args.dataset)
    train(args)
    extract_embeddings(args, dataset)


if __name__ == '__main__':
    main()
