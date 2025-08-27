# -*- coding: utf-8 -*-
import pandas as pd

def load_meteo(path_csv: str) -> pd.DataFrame:
    """
    Charge un CSV avec colonnes: datetime (ISO) , t_ext (°C)
    Retourne un DataFrame indexé par datetime (pd.DatetimeIndex).
    """
    df = pd.read_csv(path_csv)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.set_index("datetime").sort_index()
    return df
