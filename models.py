from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey,Float
from sqlalchemy.orm import Mapped, relationship
from database import Base

class Region(Base):
    __tablename__ = "regions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    geojson=Column(String, index=True, nullable=False)
    dbdata:Mapped[list["DbData"]]=relationship(back_populates="region") #еще можно сделать cascade="all будет рабтать также



class DbData(Base):
    __tablename__="dbdata"
    id=Column(Integer, primary_key=True, index=True)
    title=Column(String,nullable=False)
    value=Column(Float,nullable=False)
    region_id = Column(Integer, ForeignKey("regions.id"))

    region:Mapped["Region"]=relationship("Region",back_populates="dbdata")

