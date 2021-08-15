from utils.database_tools import *


class Page(Base):
    __tablename__ = "page"
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True)

    @none_as_null
    def __init__(self,
                 url: str):
        self.url = url


class Relationship(Base):
    __tablename__ = "relationship"
    id = Column(Integer, primary_key=True)
    parent_page_id = Column(Integer)
    child_page_id = Column(Integer)

    def __init__(self,
                 parent_page: Page,
                 child_page: Page):
        self.parent_page_id = parent_page.id
        self.child_page_id = child_page.id
