import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from src.configuration.config import MODELS, RESULTS, FEATURE_COLS
from src.metrics.metrics import calculate_metrics
from src.utils.data_utils import get_train_df, get_test_df
from src.utils.results_utils import save_metrics, compare_models


def load_model(model_name: str):
    """Carrega um modelo salvo."""
    model_path = MODELS / f"{model_name}.joblib"
    if not model_path.exists():
        raise FileNotFoundError(f"Modelo não encontrado: {model_path}")
    return joblib.load(model_path)


def evaluate_on_test():
    """
    Avalia todos os modelos no conjunto de teste.
    Salva métricas em results/test_metrics.csv
    """
    test_df = get_test_df()
    train_df = get_train_df()
    
    X_test = test_df[FEATURE_COLS]
    y_test = test_df['target']
    
    print("\n=== Avaliação no Conjunto de TESTE ===\n")
    
    # RandomForest
    try:
        rf = load_model("random_forest")
        y_pred_rf = rf.predict(X_test)
        metrics_rf = calculate_metrics(y_test, y_pred_rf)
        print(f"RandomForest (Test): {metrics_rf}")
        save_metrics('RandomForest', metrics_rf, 'test')
    except FileNotFoundError as e:
        print(f"  Pulando RandomForest: {e}")
    
    # XGBoost
    try:
        xgb = load_model("xgboost")
        y_pred_xgb = xgb.predict(X_test)
        metrics_xgb = calculate_metrics(y_test, y_pred_xgb)
        print(f"XGBoost (Test): {metrics_xgb}")
        save_metrics('XGBoost', metrics_xgb, 'test')
    except FileNotFoundError as e:
        print(f"  Pulando XGBoost: {e}")
    
    # Ridge
    try:
        ridge = load_model("ridge")
        scaler = load_model("ridge_scaler")
        X_test_scaled = scaler.transform(X_test)
        y_pred_ridge = ridge.predict(X_test_scaled)
        metrics_ridge = calculate_metrics(y_test, y_pred_ridge)
        print(f"Ridge (Test): {metrics_ridge}")
        save_metrics('Ridge', metrics_ridge, 'test')
    except FileNotFoundError as e:
        print(f"  Pulando Ridge: {e}")
    
    # Baseline Null Mean
    y_train = train_df['target']
    mean_train = y_train.mean()
    y_pred_null = np.full(len(y_test), mean_train)
    metrics_null = calculate_metrics(y_test, y_pred_null)
    print(f"Baseline Null Mean (Test): {metrics_null}")
    save_metrics('Baseline_NullMean', metrics_null, 'test')
    
    # Baseline Daily Climatology
    doy_mean = train_df.groupby(train_df['data'].dt.dayofyear)['target'].mean()
    y_pred_clim = test_df['data'].dt.dayofyear.map(doy_mean)
    y_pred_clim = y_pred_clim.fillna(y_train.mean())
    metrics_clim = calculate_metrics(y_test, y_pred_clim)
    print(f"Baseline Daily Climatology (Test): {metrics_clim}")
    save_metrics('Baseline_DailyClimatology', metrics_clim, 'test')
    
    print(f"\nMétricas salvas em: {RESULTS / 'test_metrics.csv'}")


def plot_feature_importance(model_name: str = 'random_forest', top_n: int = 15):
    """
    Plota a importância das features para um modelo baseado em árvores.
    
    Args:
        model_name: 'random_forest' ou 'xgboost'
        top_n: Número de features a mostrar
    """
    model = load_model(model_name)
    
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1][:top_n]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    features_top = [FEATURE_COLS[i] for i in indices]
    importances_top = importances[indices]
    
    colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(features_top)))
    
    ax.barh(range(len(features_top)), importances_top, color=colors)
    ax.set_yticks(range(len(features_top)))
    ax.set_yticklabels(features_top)
    ax.invert_yaxis()
    ax.set_xlabel('Importância')
    ax.set_title(f'Feature Importance - {model_name.replace("_", " ").title()}')
    
    plt.tight_layout()
    
    output_path = RESULTS / f"feature_importance_{model_name}.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Gráfico salvo em: {output_path}")
    
    # Retorna DataFrame para análise
    df_importance = pd.DataFrame({
        'feature': FEATURE_COLS,
        'importance': importances
    }).sort_values('importance', ascending=False)
    
    return df_importance


def plot_predictions_vs_actual(model_name: str = 'random_forest'):
    """
    Plota previsões vs valores reais no conjunto de teste.
    """
    test_df = get_test_df()
    X_test = test_df[FEATURE_COLS]
    y_test = test_df['target']
    
    if model_name == 'ridge':
        model = load_model(model_name)
        scaler = load_model("ridge_scaler")
        X_test_scaled = scaler.transform(X_test)
        y_pred = model.predict(X_test_scaled)
    else:
        model = load_model(model_name)
        y_pred = model.predict(X_test)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Scatter plot
    ax1 = axes[0]
    ax1.scatter(y_test, y_pred, alpha=0.5, s=10)
    
    min_val = min(y_test.min(), y_pred.min())
    max_val = max(y_test.max(), y_pred.max())
    ax1.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Ideal')
    
    ax1.set_xlabel('Vazão Real (m³/s)')
    ax1.set_ylabel('Vazão Prevista (m³/s)')
    ax1.set_title(f'Previsto vs Real - {model_name.replace("_", " ").title()}')
    ax1.legend()
    
    # Série temporal
    ax2 = axes[1]
    ax2.plot(test_df['data'], y_test, label='Real', alpha=0.7)
    ax2.plot(test_df['data'], y_pred, label='Previsto', alpha=0.7)
    ax2.set_xlabel('Data')
    ax2.set_ylabel('Vazão (m³/s)')
    ax2.set_title('Série Temporal - Teste')
    ax2.legend()
    ax2.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    
    output_path = RESULTS / f"predictions_{model_name}.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Gráfico salvo em: {output_path}")


def plot_metrics_comparison():
    """
    Plota comparação de métricas entre modelos (validação e teste).
    """
    df_val = compare_models('validation')
    df_test = compare_models('test')
    
    if df_val.empty and df_test.empty:
        print("Nenhuma métrica encontrada para comparar.")
        return
    
    metrics = ['KGE', 'R2', 'RMSE', 'MAE']
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()
    
    for i, metric in enumerate(metrics):
        ax = axes[i]
        
        models = []
        val_values = []
        test_values = []
        
        all_models = set()
        if not df_val.empty:
            all_models.update(df_val['model'].tolist())
        if not df_test.empty:
            all_models.update(df_test['model'].tolist())
        
        for model in sorted(all_models):
            models.append(model)
            
            if not df_val.empty and model in df_val['model'].values:
                val_values.append(df_val[df_val['model'] == model][metric].values[0])
            else:
                val_values.append(0)
            
            if not df_test.empty and model in df_test['model'].values:
                test_values.append(df_test[df_test['model'] == model][metric].values[0])
            else:
                test_values.append(0)
        
        x = np.arange(len(models))
        width = 0.35
        
        ax.bar(x - width/2, val_values, width, label='Validação', alpha=0.8)
        ax.bar(x + width/2, test_values, width, label='Teste', alpha=0.8)
        
        ax.set_ylabel(metric)
        ax.set_title(f'{metric}')
        ax.set_xticks(x)
        ax.set_xticklabels(models, rotation=45, ha='right')
        ax.legend()
        ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    
    output_path = RESULTS / "metrics_comparison.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Gráfico salvo em: {output_path}")


def run_full_evaluation():
    """Executa avaliação completa: métricas + gráficos."""
    print("=" * 60)
    print("AVALIAÇÃO COMPLETA DOS MODELOS")
    print("=" * 60)
    
    # 1. Avaliar no teste
    evaluate_on_test()
    
    # 2. Feature importance
    print("\n--- Gerando Feature Importance ---")
    try:
        plot_feature_importance('random_forest')
        plot_feature_importance('xgboost')
    except FileNotFoundError as e:
        print(f"  Erro: {e}")
    
    # 3. Previsões vs Real
    print("\n--- Gerando Gráficos de Previsões ---")
    try:
        plot_predictions_vs_actual('random_forest')
        plot_predictions_vs_actual('xgboost')
    except FileNotFoundError as e:
        print(f"  Erro: {e}")
    
    # 4. Comparação de métricas
    print("\n--- Gerando Comparação de Métricas ---")
    plot_metrics_comparison()
    
    # 5. Resumo
    print("\n" + "=" * 60)
    print("RESUMO - MÉTRICAS DE TESTE")
    print("=" * 60)
    df_test = compare_models('test')
    if not df_test.empty:
        print(df_test[['model', 'KGE', 'R2', 'RMSE', 'MAE']].to_string(index=False))
    
    print(f"\nResultados salvos em: {RESULTS}")


if __name__ == "__main__":
    run_full_evaluation()
