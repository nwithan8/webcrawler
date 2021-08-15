from sqlalchemy import create_engine, MetaData
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class Database:
    def __init__(self,
                 sqlite_file: str):

        self.engine = None
        self.base = None
        self.meta = None
        self.session = None
        self.url = f'sqlite:///{sqlite_file}'

        self._setup()

    def _setup(self):
        if not self.url:
            return

        self.engine = create_engine(self.url)

        if not self.engine:
            return

        if not database_exists(self.engine.url):
            create_database(self.engine.url)

        self.base = declarative_base(bind=self.engine)
        self.meta = MetaData()
        self.meta.create_all(self.engine)

        Session = sessionmaker()
        Session.configure(bind=self.engine)
        self.session = Session()

    def add(self, item):
        self.session.add(item)

    def commit(self):
        self.session.commit()

    def close(self):
        self.session.close()
