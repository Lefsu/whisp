from sqlalchemy import Column, Integer, String, MetaData, Table, inspect
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
    metadata = MetaData()
    
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
    metadata = MetaData()
    
    # Vérifier si la table existe, sinon la créer
    contacts_table = Table(f"contacts_{username}", metadata, autoload_with=engine)
    
    inspector = inspect(engine)
    if not inspector.has_table(f"contacts_{username}"):
        create_contacts_table(username)
        contacts_table = Table(f"contacts_{username}", metadata, autoload_with=engine)
    
    # Création de la session
    session = SessionLocal()

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

def delete_contact(username: str, contact_name: str):
    metadata = MetaData()
    
    # Vérifier si la table des contacts de l'utilisateur existe
    contacts_table_name = f"contacts_{username}"
    inspector = inspect(engine)
    if not inspector.has_table(contacts_table_name):
        print(f"La table '{contacts_table_name}' n'existe pas.")
        return
    
    contacts_table = Table(contacts_table_name, metadata, autoload_with=engine)
    
    session = SessionLocal()
    try:
        # Suppression du contact
        delete_stmt = contacts_table.delete().where(contacts_table.c.contact_name == contact_name)
        result = session.execute(delete_stmt)
        
        if result.rowcount > 0:
            session.commit()
            print(f"Contact '{contact_name}' supprimé avec succès de la table 'contacts_{username}'.")
        else:
            print(f"Contact '{contact_name}' introuvable dans la table 'contacts_{username}'.")
    except SQLAlchemyError as e:
        print(f"Erreur lors de la suppression du contact : {e}")
        session.rollback()
    finally:
        session.close()