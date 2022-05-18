import json

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from sqlalchemy import exc
from sqlalchemy.orm import Session

import database_util.schemas
from database_util import models, crud
from database_util.database_config import fake_users_db
from database_util.database_config import engine, SessionLocal
from token_utils import *
from user_utils import *

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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


ACCESS_TOKEN_EXPIRE_MINUTES = 30


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.get("/families")
async def get_all_families(limit: int = 100, offset: int = 0, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    response = {"limit": limit, "offset": offset, "data": crud.get_all_families(db, limit, offset)}
    return response


@app.get("/hashes/{hash_value}/family")
async def get_family_by_hash(hash_value: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    response = crud.get_family_by_hash_value(db, hash_value)
    if not response:
        raise HTTPException(status_code=404, detail="Hash not found")
    return response


@app.get("/families/{family_name}/hashes")
async def get_hashes_by_family(family_name: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    response = crud.get_hashes_by_family_name(db, family_name)
    if not response:
        raise HTTPException(status_code=404, detail="Family not found")
    return response


@app.post("/families")
async def add_families_and_hashes(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    test_counter, counter = 5, 0
    try:
        data = await request.json()
        data = json.loads(json.dumps(data))
    except():
        raise HTTPException(status_code=400, detail="JSON not formatted correctly")

    for key in data.keys():
        try:
            family = crud.get_family_by_name(db, key)
        except exc.NoResultFound:
            family = crud.add_family(db, key)

        if counter < test_counter:
            list_of_hashes = data[key]
            for curr_hash in list_of_hashes:
                if not crud.get_hash_by_name(db, curr_hash[0].split(".")[0]):
                    try:
                        crud.add_hash_to_family(db, database_util.schemas.CreateAndUpdateHash(family_id=family.id, name=curr_hash[0].split(".")[0],
                                                                                              filesize=curr_hash[1], date=curr_hash[2]))
                    except():
                        print("Current row has incomplete data")
                        continue

            counter += 1
    return data


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Se da site-ul web https://samples.vx-underground.org/samples/Families/ care reprezinta o colectie de samples malware categorisite dupa familia malware din
# care acestea fac parte. Pasul 1 Se doreste realizarea unui Scraper Web care sa parcurga structura site-ului si sa parseze informatiile din site. Prin
# informatie se face referire la hash-ul unui sample si familia din care face parte. *Scraper-ul Web nu va descarca arhivele hostate de site!!! Pasul 2 Se
# doreste realizarea unui API - scrapperul va apela o ruta a API-ului printr-o metoda de tip POST prin care va trimite informatiile parsate. API-ul va stoca
# informatiile oferite prin metoda HTTP intr-un DB. Pasul 3 Se doreste extinderea API-ului de la pasul 2 cu inca 2 rute: O ruta care primeste ca parametru un
# hash iar raspsnul va fi reprezentat de familia din care sample-ul cu hash-ul respectiv face parte O ruta care primeste ca parametru o familie iar raspunsul
# va fi reprezentat de o lista de hash-uri ale sample-urilor care fac parte din familia respectiva.
