"""Se ejecuta en Docker Compose; se omite sin POSTGRES_TEST_URL."""
import os
from datetime import date, timedelta
import pytest
from src.application.services import HotelService
from src.infrastructure.repository import SQLiteRepository

@pytest.mark.skipif(not os.getenv('POSTGRES_TEST_URL'), reason='PostgreSQL disponible solo en Docker/CI')
def test_postgres_real_transaction():
    repo=SQLiteRepository(database_url=os.environ['POSTGRES_TEST_URL'])
    service=HotelService(repo)
    # No toca los datos de producción. La base postgres es hotel_test, separada.
    start=date(2038,7,1)
    end=start+timedelta(days=1)
    a=service.create_reservation({'guest_name':'Prueba PG','check_in':str(start),'check_out':str(end),'room_type':'Suite','guests':2})
    assert a.room_number
    service.confirm(a.id,card_guarantee=True)
    assert all(x['number']!=a.room_number for x in service.availability(str(start),str(end),'Suite',2))
