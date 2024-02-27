from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import numpy as np
from transformers import DistilBertTokenizer, DistilBertModel
import torch
from dotenv import load_dotenv
import os
from sqlalchemy import or_


# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Ahora puedes acceder a las variables de entorno como si fueran variables regulares de Python
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_PORT = os.getenv("DB_PORT")


Base = declarative_base()

# Definir una tabla para los eventos
class Event(Base):
    __tablename__ = 'eventos'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    fecha = Column(Date)
    descripcion = Column(Text)
    foto = Column(String(255))
    lugar = Column(String(100))
    aprobado = Column(Boolean)

# Definir una tabla para los gustos de los usuarios
class UserPreferences(Base):
    __tablename__ = 'usuario_gusto'
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    gusto_id = Column(Integer, ForeignKey('gustos.id'))

    gusto = relationship("Gusto", back_populates="usuarios")

class Gusto(Base):
    __tablename__ = 'gustos'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(50))
    descripcion = Column(String(255))

    usuarios = relationship("UserPreferences", back_populates="gusto")

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
            user_preferences = session.query(UserPreferences).filter_by(usuario_id=user_id).all()
            for up in user_preferences:
                up.gusto  # Cargar explícitamente la relación gusto
            session.close()
            if user_preferences:
                return [up.gusto.descripcion for up in user_preferences]
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
            return {str(event.id): event.descripcion for event in events}
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


    # Dentro de la clase EventRecommender
    def recommend_events_for_user(self, user_id, num_recommendations=5):
        user_preferences = self.get_user_preferences(user_id)
    
        if user_preferences is None:
            return []

        all_events = self.get_all_events()
        user_event_embeddings = self.get_embedding(" ".join(user_preferences))

        event_similarities = {}
        for event_id, event_description in all_events.items():
            event_embedding = self.get_embedding(event_description)
            similarity = self.cosine_similarity(user_event_embeddings, event_embedding)
            event_similarities[event_id] = similarity

        sorted_events = sorted(event_similarities.items(), key=lambda x: x[1], reverse=True)
        recommended_event_ids = [int(event_id) for event_id, _ in sorted_events[:num_recommendations]]
        print(recommended_event_ids)
   
        return recommended_event_ids
         