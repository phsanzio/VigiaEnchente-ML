import pandas as pd
from src.configuration.config import PROCESSED, RAW, TRAIN_START, TRAIN_END, VAL_START, VAL_END, TEST_START


def get_final_database():
    df = pd.read_csv(PROCESSED / "final_database.csv", parse_dates=['data'])
    return df.sort_values('data').reset_index(drop=True)

def get_train_df():
    df = get_final_database()
    return df[df['data'].between(TRAIN_START, TRAIN_END)].copy()

def get_val_df():
    df = get_final_database()
    return df[df['data'].between(VAL_START, VAL_END)].copy()

def get_test_df():
    df = get_final_database()
    return df[df['data'] >= TEST_START].copy()

def get_chuva_raw():
    return pd.read_csv(RAW / "ana_chuva_sabara_1943006.csv", parse_dates=['data'])

def get_vazao_raw():
    return pd.read_csv(RAW / "glofas_vazao_sabara.csv", parse_dates=['data'])

def get_meteo_raw():
    return pd.read_csv(RAW / "inmet_meteo_bh_83587.csv", parse_dates=['data'])
