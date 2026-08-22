import pandas as pd
from datetime import datetime
from src.configuration.config import RESULTS


def save_metrics(model_name: str, metrics: dict, stage: str, params: dict = None):
    filename = RESULTS / f"{stage}_metrics.csv"
    
    row = {
        'timestamp': datetime.now().isoformat(),
        'model': model_name,
        **metrics
    }
    
    if params:
        row['params'] = str(params)
    
    df_new = pd.DataFrame([row])
    
    if filename.exists():
        df_existing = pd.read_csv(filename)
        df = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df = df_new
    
    df.to_csv(filename, index=False)
    print(f"  -> Métricas salvas em {filename}")


def load_metrics(stage: str) -> pd.DataFrame:
    """
    Carrega métricas salvas.
    
    Args:
        stage: 'validation' ou 'test'
    
    Returns:
        DataFrame com todas as métricas salvas
    """
    filename = RESULTS / f"{stage}_metrics.csv"
    
    if not filename.exists():
        print(f"Arquivo {filename} não encontrado.")
        return pd.DataFrame()
    
    return pd.read_csv(filename)


def get_best_run(stage: str, metric: str = 'KGE', model: str = None) -> pd.Series:
    """
    Retorna a melhor execução baseada em uma métrica.
    
    Args:
        stage: 'validation' ou 'test'
        metric: Métrica para ordenar (default: KGE)
        model: Filtrar por modelo específico (opcional)
    
    Returns:
        Series com os dados da melhor execução
    """
    df = load_metrics(stage)
    
    if df.empty:
        return pd.Series()
    
    if model:
        df = df[df['model'] == model]
    
    if df.empty:
        return pd.Series()
    
    return df.loc[df[metric].idxmax()]


def compare_models(stage: str) -> pd.DataFrame:
    """
    Compara o melhor resultado de cada modelo.
    
    Args:
        stage: 'validation' ou 'test'
    
    Returns:
        DataFrame com o melhor resultado de cada modelo
    """
    df = load_metrics(stage)
    
    if df.empty:
        return pd.DataFrame()
    
    best_per_model = df.loc[df.groupby('model')['KGE'].idxmax()]
    return best_per_model.sort_values('KGE', ascending=False)
