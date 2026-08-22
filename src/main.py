from src.processing.database_processor import process_database
from src.processing.feature_engineering import create_features
from src.training.models_training import train_all_models
from src.training.hyperparameter_tuning import run_tuning

def main():
    process_database()
    create_features()
    train_all_models()
    run_tuning()


if __name__ == "__main__":
    main()
