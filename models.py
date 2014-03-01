from sqlalchemy import Column, Integer, String

from orm import Base


class ResponseMap(Base):
    __tablename__ = 'response_map'

    id = Column(Integer, primary_key=True)
    pattern = Column(String)
    response = Column(String)

    def search(self, x):
        if re.search(pattern, x):
            return response
