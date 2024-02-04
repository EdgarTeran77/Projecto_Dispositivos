from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from transformers import DistilBertTokenizer, DistilBertModel
import torch
import numpy as np

Base = declarative_base()

# Definir una tabla para los eventos
class Event(Base):
    __tablename__ = 'events'
    id = Column(String, primary_key=True)
    description = Column(String)

# Definir una tabla para los gustos de los usuarios
class UserPreferences(Base):
    __tablename__ = 'user_preferences'
    id = Column(String, primary_key=True)
    preferences = Column(String)

class EventRecommender:
    def __init__(self, db_params):
        self.db_params = db_params
        self.engine = None
        self.Session = None

    def connect_to_database(self):
        try:
            self.engine = create_engine(self.db_params)
            self.Session = sessionmaker(bind=self.engine)
            print("Conexión exitosa a la base de datos.")
        except Exception as e:
            print("Error al conectarse a la base de datos:", e)

    def get_user_preferences(self, user_id):
        try:
            session = self.Session()
            user = session.query(UserPreferences).filter_by(id=user_id).first()
            session.close()
            if user:
                return user.preferences
            else:
                print("No se encontraron gustos para el usuario.")
                return None
        except Exception as e:
            print("Error al obtener los gustos del usuario:", e)
            return None

    def get_all_events(self):
        try:
            session = self.Session()
            events = session.query(Event).all()
            session.close()
            return {event.id: event.description for event in events}
        except Exception as e:
            print("Error al obtener los detalles de los eventos:", e)
            return {}

    def get_embedding(self, text):
        tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
        model = DistilBertModel.from_pretrained('distilbert-base-uncased')
        encoded_text = tokenizer.encode(text, add_special_tokens=True, max_length=512, truncation=True, return_tensors="pt")
        with torch.no_grad():
            embedding = model(encoded_text)[0][:, 0, :].numpy()
        return embedding

    def cosine_similarity(self, vector1, vector2):
        return np.dot(vector1, vector2.T) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))

    def recommend_events_for_user(self, user_id, num_recommendations=5):
        # Paso 1: Obtener los gustos del usuario
        user_preferences = self.get_user_preferences(user_id)
        if user_preferences is None:
            return []

        # Paso 2: Recuperar los detalles de todos los eventos disponibles
        all_events = self.get_all_events()

        # Paso 3: Procesar los datos utilizando DistilBERT para obtener representaciones vectoriales
        user_embedding = self.get_embedding(user_preferences)
        event_embeddings = {event_id: self.get_embedding(event_description) for event_id, event_description in all_events.items()}

        # Paso 4: Calcular la similitud del coseno entre los gustos del usuario y los detalles de cada evento
        event_similarities = {event_id: self.cosine_similarity(user_embedding, event_embedding) for event_id, event_embedding in event_embeddings.items()}

        # Paso 5: Ordenar los eventos por similitud
        sorted_events = sorted(event_similarities.items(), key=lambda x: x[1], reverse=True)

        # Paso 6: Seleccionar los eventos recomendados
        recommended_events = [event_id for event_id, _ in sorted_events[:num_recommendations]]

        return recommended_events

# Ejemplo de uso
if __name__ == "__main__":
    db_params = 'postgresql://usuario:contraseña@localhost:puerto/nombre_de_base_de_datos'
    event_recommender = EventRecommender(db_params)
    event_recommender.connect_to_database()

    user_id = "123"
    recommended_events = event_recommender.recommend_events_for_user(user_id)
    print("Eventos recomendados para el usuario:", recommended_events)
