from typing import Union, List

import utils.database as db
from database.tables.page import Page, Relationship
from utils.database_tools import *


class PagesDatabase(db.Database):
    def __init__(self,
                 sqlite_file: str):
        super().__init__(sqlite_file=sqlite_file)
        Page.__table__.create(bind=self.engine, checkfirst=True)
        Relationship.__table__.create(bind=self.engine, checkfirst=True)

    def get_page_entry_by_url(self,
                              url: str) -> Page:
        return self.session.query(Page).filter(Page.url == url).first()

    def get_page_entry_by_id(self,
                             entry_id: int) -> Page:
        return self.session.query(Page).filter(Page.id == entry_id).first()

    def get_relationship(self,
                         parent_page: Page,
                         child_page: Page):
        return self.session.query(Relationship).filter(
            and_(Relationship.parent_page_id == parent_page.id, Relationship.child_page_id == child_page.id)).first()

    def add_page(self,
                 url: str) -> Union[Page, None]:
        new_page = Page(url=url)
        try:
            self.add(new_page)
            self.commit()  # need to commit first to have id generated
            new_page = self.get_page_entry_by_url(url=url)
            return new_page
        except:  # if link can't be saved (not unique)
            return None

    def add_relationship(self,
                         parent_page: Page,
                         child_page: Page) -> bool:
        r = Relationship(parent_page=parent_page, child_page=child_page)
        self.add(r)
        self.commit()
        return True

    def page_visited(self,
                     url: str) -> bool:
        return len(self.session.query(Page).filter(Page.url == url).all()) > 0

    def add_page_and_relationship(self,
                                  url: str,
                                  parent_page: Page = None) -> Union[Page, None]:
        page = self.get_page_entry_by_url(url=url)
        if not page:
            print(f"Adding {url} to database.")
            page = self.add_page(url=url)
        else:
            print(f"{url} exists in database.")

        if parent_page:
            r = self.get_relationship(parent_page=parent_page, child_page=page)
            if not r:
                print(f"Noting relationship.\nParent: {parent_page.url}\nChild: {url}")
                self.add_relationship(parent_page=parent_page, child_page=page)

        return page

    def get_parents(self,
                    page: Page) -> List[Page]:
        parent_page_ids = self.session.query(Relationship.parent_page_id).filter(
            Relationship.child_page_id == page.id).all()
        return self.session.query(Page).filter(Page.id.in_(parent_page_ids)).all()

    def get_children(self,
                     page: Page) -> List[Page]:
        child_page_ids = self.session.query(Relationship.child_page_id).filter(
            Relationship.parent_page_id == page.id).all()
        return self.session.query(Page).filter(Page.id.in_(child_page_ids)).all()
