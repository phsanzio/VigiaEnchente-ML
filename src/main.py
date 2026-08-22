from processing.database_processor import process_database
from processing.feature_engineering import create_features
from training.models_training import train_all_models
from training.hyperparameter_tuning import run_tuning

def main():
    process_database()
    create_features()
    train_all_models()
    run_tuning()


if __name__ == "__main__":
    main()
