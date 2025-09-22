from fastapi import FastAPI,Depends,status,HTTPException,Request
from fastapi.responses import JSONResponse
from database import Base,engine,get_db,AsyncSession
from sqlalchemy import select
from models import *
from schemas import *
from typing import List
from contextlib import asynccontextmanager
import logging



# Создаем логгер как в fastapi с временем

# Устанавливаем формат
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:\t  %(name)s:\t  %(message)s\t  %(asctime)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("main")
logger.setLevel(logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("База данных готова к работе!")
    yield
    logger.info("Приложение завершает работу")

app = FastAPI(lifespan=lifespan)


@app.post("/regions",status_code=status.HTTP_201_CREATED,response_model=RegionOut)
async def create_region(region:RegionBase,db: AsyncSession = Depends(get_db)):
    new_region = Region(name=region.name, geojson=region.geojson)
    db.add(new_region)
    await db.commit()
    await db.refresh(new_region)
    return new_region



@app.post("/regions/{region_id}/data/",status_code=status.HTTP_201_CREATED,response_model=DataOut)
async def add_data(region_id: int, dbdata:DataCreate, db:AsyncSession = Depends(get_db)):
    result = await db.execute(select(Region).where(Region.id == region_id))
    region=result.scalars().first()
    if region is None:
        raise HTTPException(status_code=404, detail="Region not found")
    region_data=DbData(title=dbdata.title, value=dbdata.value,region_id=region_id)
    db.add(region_data)
    await db.commit()
    await db.refresh(region_data)
    return region_data



@app.get("/regions",response_model=List[RegionOut])
async def get_regions(db: AsyncSession = Depends(get_db)):
    regions = await db.execute(select(Region))
    result=regions.scalars().all()
    return result




@app.get("/regions/{region_id}/data/",response_model=List[DataOut])
async def read_all_data(region_id:int,db:AsyncSession=Depends(get_db)):
    result=await db.execute(select(DbData).where(Region.id==region_id))
    dbdata=result.scalars().all()
    if dbdata is None:
        raise HTTPException(status_code=404, detail="dbdata is empty")
    return dbdata





@app.delete("/regions/{region_id}/data/{data_id}")
async def delete_data(region_id:int,data_id:int, db:AsyncSession=Depends(get_db)):
    result = await db.execute(select(DbData).where(
    DbData.id == data_id,
    DbData.region_id == region_id))
    data= result.scalars().first()
    if data is None:
        raise HTTPException(status_code=404,detail="data not found")
    await db.delete(data)
    await db.commit()
    return {"message":"data deleted successfully"}





@app.get("/regions/{region_id}",response_model=RegionOut)
async def get_region(region_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Region).where(Region.id==region_id))
    region=result.scalars().first()
    if region is None:
        raise HTTPException(status_code=404, detail="Region not found")
    return region



@app.put("/regions/{region_id}",response_model=RegionOut)
async def update_region(region_id:int,region_update:RegionBase,db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Region).where(Region.id==region_id))
    region = result.scalars().first()
    if region is None:
        raise HTTPException(status_code=404, detail="Region not found")
    region.name = region_update.name
    region.geojson = region_update.geojson
    await db.commit()
    await db.refresh(region)
    return region



@app.delete("/regions/{region_id}")
async def delete_region(region_id:int,db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Region).where(Region.id==region_id))
    region=result.scalars().first()
    if region is None:
        raise HTTPException(status_code=404, detail="Region not found")
    await db.delete(region)
    await db.commit()
    return {"message":"region deleted successfully"}