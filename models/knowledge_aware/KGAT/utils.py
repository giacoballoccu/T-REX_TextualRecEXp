from easydict import EasyDict as edict
import wandb
import os

ML1M = 'ml1m'
LFM1M = 'lfm1m'
CELL = 'cellphones'
MODEL = 'kgat'
ROOT_DIR = os.environ('TREX_DATA_ROOT') if 'TREX_DATA_ROOT' in os.environ else '../../..'
# Dataset directories.
DATA_DIR = {
    ML1M: f'{ROOT_DIR}/data/{ML1M}/preprocessed/{MODEL}',
    LFM1M: f'{ROOT_DIR}/data/{LFM1M}/preprocessed/{MODEL}',
    CELL: f'{ROOT_DIR}/data/{CELL}/preprocessed/{MODEL}'
}
# Model result directories.
TMP_DIR = {
    ML1M: f'{DATA_DIR[ML1M]}/tmp',
    LFM1M: f'{DATA_DIR[LFM1M]}/tmp',
    CELL: f'{DATA_DIR[CELL]}/tmp',
}



OPTIM_HPARAMS_METRIC = 'valid_ndcg'
VALID_METRICS_FILE_NAME = 'valid_metrics.json'

LOG_DIR = f'{ROOT_DIR}/results'

CFG_DIR = {
    ML1M: f'{LOG_DIR}/{ML1M}/{MODEL}/hparams_cfg',
    LFM1M: f'{LOG_DIR}/{LFM1M}/{MODEL}/hparams_cfg',
    CELL: f'{LOG_DIR}/{CELL}/{MODEL}/hparams_cfg',
}
BEST_CFG_DIR = {
    ML1M: f'{LOG_DIR}/{ML1M}/{MODEL}/best_hparams_cfg',
    LFM1M: f'{LOG_DIR}/{LFM1M}/{MODEL}/best_hparams_cfg',
    CELL: f'{LOG_DIR}/{CELL}/{MODEL}/best_hparams_cfg',
}
TEST_METRICS_FILE_NAME = 'test_metrics.json'
TEST_METRICS_FILE_PATH = {
    ML1M: f'{CFG_DIR[ML1M]}/{TEST_METRICS_FILE_NAME}',
    LFM1M: f'{CFG_DIR[LFM1M]}/{TEST_METRICS_FILE_NAME}',
    CELL: f'{CFG_DIR[CELL]}/{TEST_METRICS_FILE_NAME}',
}
BEST_TEST_METRICS_FILE_PATH = {
    ML1M: f'{BEST_CFG_DIR[ML1M]}/{TEST_METRICS_FILE_NAME}',
    LFM1M: f'{BEST_CFG_DIR[LFM1M]}/{TEST_METRICS_FILE_NAME}',
    CELL: f'{BEST_CFG_DIR[CELL]}/{TEST_METRICS_FILE_NAME}',
}


CONFIG_FILE_NAME = 'config.json'
CFG_FILE_PATH = {
    ML1M: f'{CFG_DIR[ML1M]}/{CONFIG_FILE_NAME}',
    LFM1M: f'{CFG_DIR[LFM1M]}/{CONFIG_FILE_NAME}',
    CELL: f'{CFG_DIR[CELL]}/{CONFIG_FILE_NAME}',
}
BEST_CFG_FILE_PATH = {
    ML1M: f'{BEST_CFG_DIR[ML1M]}/{CONFIG_FILE_NAME}',
    LFM1M: f'{BEST_CFG_DIR[LFM1M]}/{CONFIG_FILE_NAME}',
    CELL: f'{BEST_CFG_DIR[CELL]}/{CONFIG_FILE_NAME}',
}



def makedirs(dataset_name):
    os.makedirs(BEST_CFG_DIR[dataset_name], exist_ok=True)
    os.makedirs(CFG_DIR[dataset_name], exist_ok=True)


