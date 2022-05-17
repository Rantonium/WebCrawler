from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import json

import database_util.schemas
from database_util import models, crud
from database_util.database_config import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/families")
async def get_all_families(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    response = {"limit": 100, "offset": 0, "data": crud.get_all_families(db, limit, offset)}
    return response


@app.get("/family")
async def get_family_by_hash(hash_value: str, db: Session = Depends(get_db)):
    response = crud.get_family_by_hash_value(db, hash_value)
    return response


@app.get("/family/hashes")
async def get_hashes_by_family(family_name: str, db: Session = Depends(get_db)):
    response = crud.get_hashes_by_family_name(db, family_name)
    return response


@app.post("/families")
async def add_families_and_hashes(request: Request, db: Session = Depends(get_db)):
    test_counter = 5
    counter = 0
    data = await request.json()
    data = json.loads(json.dumps(data))
    for key in data.keys():
        # key is the name
        family = crud.add_family(db, key)
        print(family.id)
        if counter < test_counter:
            list_of_hashes = data[key]
            for curr_hash in list_of_hashes:
                crud.add_hash_to_family(db, database_util.schemas.CreateAndUpdateHash(family_id=family.id, name=curr_hash[0].split(".")[0],
                                                                                      filesize=curr_hash[1], date=curr_hash[2]))
            counter += 1
    return data

# Se da site-ul web https://samples.vx-underground.org/samples/Families/ care reprezinta o colectie de samples malware categorisite dupa familia malware din
# care acestea fac parte. Pasul 1 Se doreste realizarea unui Scraper Web care sa parcurga structura site-ului si sa parseze informatiile din site. Prin
# informatie se face referire la hash-ul unui sample si familia din care face parte. *Scraper-ul Web nu va descarca arhivele hostate de site!!! Pasul 2 Se
# doreste realizarea unui API - scrapperul va apela o ruta a API-ului printr-o metoda de tip POST prin care va trimite informatiile parsate. API-ul va stoca
# informatiile oferite prin metoda HTTP intr-un DB. Pasul 3 Se doreste extinderea API-ului de la pasul 2 cu inca 2 rute: O ruta care primeste ca parametru un
# hash iar raspsnul va fi reprezentat de familia din care sample-ul cu hash-ul respectiv face parte O ruta care primeste ca parametru o familie iar raspunsul
# va fi reprezentat de o lista de hash-uri ale sample-urilor care fac parte din familia respectiva.
