from sqlalchemy import Column, Integer, String, MetaData, Table, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import NoSuchTableError, SQLAlchemyError
from .database import engine
import sqlite3

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    identifiant = Column(String, unique=True, index=True)
    password = Column(String)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fonction pour obtenir la table "contacts" d'un utilisateur
def get_contacts_table(username: str, metadata: MetaData):
    return Table(f'contacts_{username}', metadata, autoload_with=engine)

# Créer la table de contacts pour un utilisateur si elle n'existe pas
def create_contacts_table(username: str):
    metadata = MetaData(bind=engine)
    
    # Création de la table avec les colonnes id et username
    contacts_table = Table(
        f"contacts_{username}", metadata,
        Column('id', Integer, primary_key=True),
        Column('username', String(50), nullable=False)
    )
    
    try:
        contacts_table.create(bind=engine)
        print(f"Table 'contacts_{username}' créée avec succès.")
    except SQLAlchemyError as e:
        print(f"Erreur lors de la création de la table : {e}")

# Fonction pour insérer un contact
def insert_contact(username: str, contact_name: str):
    metadata = MetaData(bind=engine)
    
    # Vérifier si la table existe, sinon la créer
    contacts_table = Table(f"contacts_{username}", metadata, autoload_with=engine)
    
    if not contacts_table.exists():
        create_contacts_table(username)
        contacts_table = Table(f"contacts_{username}", metadata, autoload_with=engine)
    
    # Création de la session
    session = Session()

    try:
        # Insertion du contact
        session.execute(contacts_table.insert().values(contact_name=contact_name))
        session.commit()
        print(f"Contact '{contact_name}' ajouté avec succès dans la table 'contacts_{username}'.")
    except SQLAlchemyError as e:
        print(f"Erreur lors de l'insertion du contact : {e}")
        session.rollback()
    finally:
        session.close()