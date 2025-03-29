from sqlalchemy import Column, Integer, String, MetaData, Table, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from .database import engine

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    identifiant = Column(String, unique=True, index=True)
    password = Column(String)

# Création des tables si elles n'existent pas
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Vérifie si une table existe
def table_exists(table_name: str):
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

# Fonction pour obtenir la table "contacts" d'un utilisateur
def get_contacts_table(username: str, metadata: MetaData):
    return Table(f'contacts_{username}', metadata, autoload_with=engine)

# Créer la table de contacts pour un utilisateur si elle n'existe pas
def create_contacts_table(username: str):
    metadata = MetaData()  # Supprimé bind=engine
    contacts_table_name = f"contacts_{username}"
    
    if table_exists(contacts_table_name):
        return
    
    contacts_table = Table(
        contacts_table_name, metadata,
        Column('id', Integer, primary_key=True),
        Column('contact_name', String(50), nullable=False)
    )
    
    try:
        metadata.create_all(engine)  # Passer engine explicitement ici
        print(f"Table '{contacts_table_name}' créée avec succès.")
    except SQLAlchemyError as e:
        print(f"Erreur lors de la création de la table : {e}")

# Fonction pour insérer un contact
def insert_contact(username: str, contact_name: str):
    metadata = MetaData()  # Supprimé bind=engine
    contacts_table_name = f"contacts_{username}"
    
    if not table_exists(contacts_table_name):
        create_contacts_table(username)
    
    contacts_table = Table(contacts_table_name, metadata, autoload_with=engine)
    session = SessionLocal()
    
    try:
        session.execute(contacts_table.insert().values(contact_name=contact_name))
        session.commit()
        print(f"Contact '{contact_name}' ajouté avec succès dans la table '{contacts_table_name}'.")
    except SQLAlchemyError as e:
        print(f"Erreur lors de l'insertion du contact : {e}")
        session.rollback()
    finally:
        session.close()

# Fonction pour supprimer un contact
def delete_contact(username: str, contact_name: str):
    contacts_table_name = f"contacts_{username}"
    
    if not table_exists(contacts_table_name):
        print(f"La table '{contacts_table_name}' n'existe pas.")
        return
    
    metadata = MetaData()  # Supprimé bind=engine
    contacts_table = Table(contacts_table_name, metadata, autoload_with=engine)
    session = SessionLocal()
    
    try:
        delete_stmt = contacts_table.delete().where(contacts_table.c.contact_name == contact_name)
        result = session.execute(delete_stmt)
        
        if result.rowcount > 0:
            session.commit()
            print(f"Contact '{contact_name}' supprimé avec succès de la table '{contacts_table_name}'.")
        else:
            print(f"Contact '{contact_name}' introuvable dans la table '{contacts_table_name}'.")
    except SQLAlchemyError as e:
        print(f"Erreur lors de la suppression du contact : {e}")
        session.rollback()
    finally:
        session.close()
