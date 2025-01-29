from catboost import CatBoostRegressor

from ..config import BASEDIR
from ..utils import load_pickle

MODELS = {
    "price_suggestion": CatBoostRegressor().load_model(BASEDIR / "freelance_website" / "static" / "price_suggestion_model"),
}

VECTORIZERS = {
    "price_suggestion": load_pickle(BASEDIR / "freelance_website" / "static" / "price_vectorizer.pkl")
}


class Model:

    def __init__(self, model_name):
        self.model_name = model_name

    def __call__(self):
        model = MODELS.get(self.model_name)
        if model is None:
            raise ValueError(f"No model with name {self.model_name}")
        
        return model


class Vectorizer:

    def __init__(self, vectorizer_name):
        self.vectorizer_name = vectorizer_name


    def __call__(self):
        tokenizer = VECTORIZERS.get(self.vectorizer_name)
        if tokenizer is None:
            raise ValueError(f"No vectorizer with name {self.vectorizer_name}")
        
        return tokenizer
