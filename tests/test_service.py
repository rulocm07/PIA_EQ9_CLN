from datetime import date, datetime, timedelta
from decimal import Decimal
import hashlib
import pytest
from concurrent.futures import ThreadPoolExecutor
from src.domain.hotel import ReservationStatus, RoomStatus

def make(service, check_in='2026-11-06',check_out='2026-11-08',room_type='Estándar',guests=2):
    return service.create_reservation({'guest_name':'Ana López','check_in':check_in,'check_out':check_out,'room_type':room_type,'guests':guests})

def test_no_overbooking_even_with_pending(service):
    all_res=[make(service) for _ in range(60)]
    assert len(set(r.room_number for r in all_res))==60
    assert service.availability('2026-11-06','2026-11-08','Estándar',2)==[]
    with pytest.raises(ValueError,match='Sin habitaciones'): make(service)
    assert len(service.repo.reservations())==60

def test_atomic_parallel_booking(service):
    def book(_): return make(service).room_number
    with ThreadPoolExecutor(max_workers=4) as pool:
        numbers=list(pool.map(book,range(16)))
    assert len(set(numbers))==16

def test_cancel_frees_room_and_duplicate_rejected(service):
    r=make(service);service.confirm(r.id,1200)
    with pytest.raises(ValueError):service.confirm(r.id,1200)
    canceled=service.cancel(r.id,datetime(2026,11,1,10))
    assert canceled['refund_mxn']=='1200.00'
    again=make(service)
    assert again.room_number==r.room_number

def test_no_show_next_day_releases_room(service):
    r=make(service);service.confirm(r.id,card_guarantee=True)
    assert service.process_no_shows(datetime(2026,11,6,23,58))==[]
    processed=service.process_no_shows(datetime(2026,11,7,0))
    assert processed[0]['charge_first_night_mxn']=='1200.00'
    assert service.process_no_shows(datetime(2026,11,7,0))==[]
    assert make(service).room_number==r.room_number

def test_full_checkin_charges_inspection_checkout_clean(service):
    r=make(service)
    service.confirm(r.id,1200)
    start=datetime(2026,11,6,11,15)
    result=service.check_in(r.id,'INE',['Luis'],'voucher',start)
    folio_id=result['folio_id'];assert result['status']=='Checked-in'
    assert result['balance_mxn']=='1560.00' # 2400 lodging - 1200 deposit + 360 early
    with pytest.raises(ValueError):service.check_in(r.id,'INE',['Luis'],'voucher',start)
    service.add_consumption(folio_id,'lavandería','Camisa',100,'firma','001',start)
    with pytest.raises(ValueError):service.add_consumption(folio_id,'lavandería','Camisa',100,'firma','002',start)
    service.request_inspection(folio_id,datetime(2026,11,8,11,50))
    with pytest.raises(ValueError):service.complete_inspection(folio_id,datetime(2026,11,8,11,54))
    service.complete_inspection(folio_id,datetime(2026,11,8,11,55))
    with pytest.raises(ValueError):service.check_out(r.id,datetime(2026,11,8,12))
    service.pay_folio(folio_id,1660,'terminal',datetime(2026,11,8,11,56))
    out=service.check_out(r.id,datetime(2026,11,8,12))
    assert out['room_status']=='Sucia'
    with pytest.raises(ValueError):service.clean_room('001',datetime(2026,11,8,12,34))
    service.clean_room('001',datetime(2026,11,8,12,36))
    assert service.repo.rooms()[0].status==RoomStatus.LIMPIA
    report=service.daily_reports('2026-11-08')
    assert report['cash_mxn']['terminal']=='1660.00'
    assert report['occupancy']['exits']==1

def test_late_checkout_fee(service):
    r=make(service);service.confirm(r.id,card_guarantee=True)
    s=service.check_in(r.id,'Pasaporte',['Beto'],'efectivo',datetime(2026,11,6,15))
    assert service.preview_checkout(r.id,datetime(2026,11,8,14))['late_fee_mxn']=='360.00'
    assert service.preview_checkout(r.id,datetime(2026,11,8,15,1))['late_fee_mxn']=='1200.00'
    service.request_inspection(s['folio_id'],datetime(2026,11,8,14))
    service.complete_inspection(s['folio_id'],datetime(2026,11,8,14,5))
    service.pay_folio(s['folio_id'],2760,'terminal',datetime(2026,11,8,14,5))
    o=service.check_out(r.id,datetime(2026,11,8,14,7))
    assert o['total_mxn']=='2760.00'

def test_block_maintenance_and_reactivate(service):
    with pytest.raises(ValueError):service.block_room('001','fuga','2026-11-10','Recepción')
    r=service.block_room('001','fuga','2026-11-10','Supervisor de Mantenimiento')
    assert r.status==RoomStatus.FUERA_SERVICIO
    assert len(service.availability('2026-11-06','2026-11-08','Estándar',2))==59
    with pytest.raises(ValueError):service.clean_room('001')
    service.reactivate_room('001','Administración')
    service.clean_room('001')
    assert len(service.availability('2026-11-06','2026-11-08','Estándar',2))==60

def test_change_room_upgrade_and_failure(service):
    r=make(service);service.confirm(r.id,card_guarantee=True)
    d=datetime(2026,11,6,15)
    fid=service.check_in(r.id,'INE',['L'],'voucher',d)['folio_id']
    changed=service.change_room(r.id,'101','upgrade',d)
    assert changed['charge_mxn']=='3600.00' # (3000-1200)*2 nights
    assert service.repo.rooms()[0].status==RoomStatus.SUCIA
    assert service.repo.reservations()[0].room_number=='101'
    with pytest.raises(ValueError):service.change_room(r.id,'002','avería',d)
    assert service.folio(fid)['total_mxn']=='6000.00'


def test_change_room_due_to_failure_no_fee(service):
    r=make(service);service.confirm(r.id,card_guarantee=True)
    d=datetime(2026,11,6,15)
    service.check_in(r.id,'INE',['L'],'voucher',d)
    changed=service.change_room(r.id,'061','avería',d)
    assert changed['charge_mxn']=='0'


def test_early_departure_policy(service):
    r=make(service,check_out='2026-11-10')
    service.confirm(r.id,card_guarantee=True)
    service.check_in(r.id,'INE',['L'],'voucher',datetime(2026,11,6,15))
    result=service.early_departure(r.id,datetime(2026,11,6,12),datetime(2026,11,8,12))
    assert result['penalty_mxn']=='600.00'
    assert result['new_checkout_date']=='2026-11-08'


def test_sensitive_operations_require_pin(service,monkeypatch):
    r=make(service);service.confirm(r.id,card_guarantee=True)
    fid=service.check_in(r.id,'INE',['L'],'voucher',datetime(2026,11,6,15))['folio_id']
    salt=b'0123456789abcdef';key=hashlib.pbkdf2_hmac('sha256',b'9371',salt,200000)
    monkeypatch.setenv('ADMIN_PIN_HASH',f'200000${salt.hex()}${key.hex()}')
    service.authorize_adjustment(fid,'descuento',10)
    with pytest.raises(ValueError):service.authorize_adjustment(fid,'descuento',20,'bad')
    service.authorize_adjustment(fid,'descuento',20,'9371')
    service.authorize_adjustment(fid,'condonación',50,'9371')
    with pytest.raises(ValueError):service.authorize_adjustment(fid,'anulación',99999,'9371')


def test_cancellation_penalty_waiver_requires_admin_pin(service,monkeypatch):
    r=make(service);service.confirm(r.id,1200)
    salt=b'0123456789abcdef'; key=hashlib.pbkdf2_hmac('sha256',b'12345678',salt,200000)
    monkeypatch.setenv('ADMIN_PIN_HASH',f'200000${salt.hex()}${key.hex()}')
    with pytest.raises(ValueError):service.cancel(r.id,datetime(2026,11,5,12),waive_penalty=True,admin_pin='wrong')
    # Rollback: el fallo de PIN no modifica la reserva.
    assert service.repo.reservations()[0].status==ReservationStatus.CONFIRMADA
    result=service.cancel(r.id,datetime(2026,11,5,12),waive_penalty=True,admin_pin='12345678')
    assert result['refund_mxn']=='1200.00'
    assert result['penalty_mxn']=='0.00'


def test_early_departure_same_day_never_refunds_prepaid_lodging(service):
    r=make(service,check_out='2026-11-11');service.confirm(r.id,3000)
    service.check_in(r.id,'INE',['L'],'voucher',datetime(2026,11,6,15))
    out=service.early_departure(r.id,datetime(2026,11,7,8),datetime(2026,11,7,10))
    assert out['penalty_mxn']=='1200.00'
    assert service.folio(out['folio_id'])['total_mxn']>='3000.00'
