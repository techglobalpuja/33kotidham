import os
import sys
from sqlalchemy.orm import joinedload

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import models, database, crud, schemas


def main():
    db = database.SessionLocal()

    # Ensure at least one chadawa exists
    ch = db.query(models.Chadawa).first()
    if not ch:
        ch = models.Chadawa(name='Test Chadawa', description='test', price=0)
        db.add(ch)
        db.commit()
        db.refresh(ch)
    print('Using chadawa id', ch.id)

    # create a puja with the chadawa
    puja_in = schemas.PujaCreate(
        name='Temp Puja For Chadawa Test',
        sub_heading='test',
        description='testing chadawa associations',
        category=['general'],
        plan_ids=[],
        chadawa_ids=[ch.id]
    )

    new_puja = crud.PujaCRUD.create_puja(db, puja_in)
    print('Created puja id', new_puja.id)

    # Fetch puja with joined load
    puja = crud.PujaCRUD.get_puja(db, new_puja.id)
    print('puja.puja_chadawas len =', len(puja.puja_chadawas))
    for pc in puja.puja_chadawas:
        print('  assoc id', pc.id, 'chadawa id', pc.chadawa_id, 'chadawa name', pc.chadawa.name)


if __name__ == '__main__':
    main()
