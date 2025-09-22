from pydantic import BaseModel, Field
from pydantic import ConfigDict




class RegionBase(BaseModel):
    name: str=Field(min_length=1)
    geojson: str=Field(min_length=1)



class RegionOut(RegionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)



class DataCreate(BaseModel):
    title:str=Field(max_length=350)
    value:float=Field(gt=0)



class DataOut(DataCreate):
    id:int
    region_id: int

    model_config = ConfigDict(from_attributes=True)

