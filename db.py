from sqlmodel import Session, SQLModel, create_engine
import models

DATABASE_FILE_NAME = "links.db"
DATABASE_URL = f"sqlite:///{DATABASE_FILE_NAME}"

engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})

def create_tables() -> None:
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session