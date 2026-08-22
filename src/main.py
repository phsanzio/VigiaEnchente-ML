import sys
from src.processing.database_processor import process_database
from src.processing.feature_engineering import create_features
from src.training.models_training import train_all_models, retrain_best_models
from src.training.hyperparameter_tuning import run_tuning
from src.evaluate.evaluate import evaluate_on_test, run_full_evaluation


def print_help():
    print("""
Uso: python -m src.main <comando>

Comandos disponíveis:
  process     - Processa os dados brutos
  features    - Cria as features
  train       - Treina todos os modelos (params default) -> salva métricas de validação
  tune        - Roda hyperparameter tuning (RF e XGB) -> salva best_params.json
  retrain     - Retreina RF e XGB com os melhores params -> salva métricas de validação
  evaluate    - Avalia modelos no conjunto de TESTE -> salva métricas de teste + gráficos
  all         - Executa pipeline completo (process -> features -> train -> tune -> retrain -> evaluate)

Exemplo:
  python -m src.main train
  python -m src.main evaluate
""")


def main():
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'process':
        process_database()
    
    elif command == 'features':
        create_features()
    
    elif command == 'train':
        train_all_models()
    
    elif command == 'tune':
        run_tuning()
    
    elif command == 'retrain':
        retrain_best_models()
    
    elif command == 'evaluate':
        run_full_evaluation()
    
    elif command == 'all':
        print("=== Pipeline Completo ===\n")
        process_database()
        create_features()
        train_all_models()
        run_tuning()
        retrain_best_models()
        run_full_evaluation()
    
    elif command in ['help', '-h', '--help']:
        print_help()
    
    else:
        print(f"Comando desconhecido: {command}")
        print_help()


if __name__ == "__main__":
    main()
