
from contextlib import contextmanager

from sqlalchemy import create_engine, Column, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from constants import NUMBER_COLUMNS

# Database configuration
DATABASE_URL = "sqlite:///quini6.db"

Base = declarative_base()

class Sorteo(Base):
    __tablename__ = 'sorteos'

    id = Column(Integer, primary_key=True)
    fecha = Column(String)
    sorteo_id = Column(Integer, index=True)
    modalidad = Column(String)
    n1 = Column(Integer)
    n2 = Column(Integer)
    n3 = Column(Integer)
    n4 = Column(Integer)
    n5 = Column(Integer)
    n6 = Column(Integer)

    # Constraint to prevent duplicates for the same modality in the same draw
    __table_args__ = (
        UniqueConstraint('sorteo_id', 'modalidad', name='uix_sorteo_modalidad'),
    )

    def __repr__(self):
        return f"<Sorteo(id={self.sorteo_id}, mod={self.modalidad})>"

# Setup DB connection
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def session_scope():
    """Yields a session and always closes it afterwards."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def init_db():
    """Initializes the database tables."""
    Base.metadata.create_all(bind=engine)

def guardar_sorteo(datos):
    """
    Saves a draw result to the database.
    Checks for duplicates based on (sorteo_id, modalidad).
    
    Args:
        datos (dict): Dictionary containing draw data.
    """
    with session_scope() as session:
        try:
            # Check if already exists
            exists = session.query(Sorteo).filter_by(
                sorteo_id=datos['sorteo_id'],
                modalidad=datos['modalidad']
            ).first()

            if exists:
                print(f"  [DB] Skipped duplicate: Draw {datos['sorteo_id']} - {datos['modalidad']}")
                return

            # Create new record
            nuevo_sorteo = Sorteo(
                fecha=datos['fecha'],
                sorteo_id=datos['sorteo_id'],
                modalidad=datos['modalidad'],
                **{col: datos[col] for col in NUMBER_COLUMNS}
            )
            session.add(nuevo_sorteo)
            session.commit()
            print(f"  [DB] Saved: Draw {datos['sorteo_id']} - {datos['modalidad']}")

        except Exception as e:
            print(f"  [DB] Error saving: {e}")
            session.rollback()

# Initialize tables on import
init_db()
