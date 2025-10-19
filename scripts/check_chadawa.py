import os
import sys
from sqlalchemy.orm import joinedload

# Ensure project root is on sys.path so 'app' package can be imported when running from scripts/
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import models, database

def main():
    db = database.SessionLocal()
    puja_id = 48

    print('Querying PujaChadawa rows for puja_id=', puja_id)
    rows = db.query(models.PujaChadawa).filter(models.PujaChadawa.puja_id == puja_id).all()
    print('PujaChadawa count =', len(rows))
    for r in rows:
        ch = getattr(r, 'chadawa', None)
        print('PujaChadawa id=', getattr(r,'id',None), 'chadawa_id=', r.chadawa_id, 'chadawa_obj=', bool(ch))
        if ch:
            # attempt to print some identifying fields
            print('  chadawa: id=', ch.id, 'name=', getattr(ch, 'name', getattr(ch, 'title', None)))

    print('\nQuerying Puja with joinedload of puja_chadawas -> chadawa')
    puja = db.query(models.Puja).options(joinedload(models.Puja.puja_chadawas).joinedload(models.PujaChadawa.chadawa)).filter(models.Puja.id==puja_id).first()
    if not puja:
        print('No Puja found with id', puja_id)
        return
    print('Puja found id=', puja.id, 'title=', getattr(puja,'name', getattr(puja,'title', None)))
    print('puja.puja_chadawas length =', len(puja.puja_chadawas))
    for pc in puja.puja_chadawas:
        ch = pc.chadawa
        print(' association id=', getattr(pc,'id',None), 'chadawa_id=', pc.chadawa_id, 'chadawa_obj=', bool(ch))
        if ch:
            print('   chadawa: id=', ch.id, 'name=', getattr(ch, 'name', getattr(ch, 'title', None)))

if __name__ == '__main__':
    main()
