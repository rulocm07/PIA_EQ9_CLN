from datetime import date, datetime, timedelta
from decimal import Decimal
import pytest
from src.domain.hotel import (
    DateRange, Money, Room, RoomStatus, RoomType, Reservation, ReservationStatus,
    Folio, is_high_season, nightly_rate, stay_total
)
from src.domain.specifications import CapacitySpecification, ReadyRoomSpecification, NoOverlapSpecification
from src.domain.state_machine import room_transition, reservation_transition

def reservation():
    return Reservation(1,'Ana',DateRange(date(2026,11,6),date(2026,11,8)),RoomType.ESTANDAR,2,Money(2400),room_number='001')

def test_value_objects_and_tariffs(monkeypatch):
    with pytest.raises(ValueError): Money(-2)
    with pytest.raises(ValueError): DateRange(date(2026,11,8),date(2026,11,8))
    assert DateRange(date(2026,11,6),date(2026,11,8)).nights == 2
    assert nightly_rate(RoomType.ESTANDAR,date(2026,7,1)).amount == Decimal('1620.00')
    assert nightly_rate(RoomType.ESTANDAR,date(2026,5,1)).amount == Decimal('1200.00')
    assert stay_total(RoomType.ESTANDAR,DateRange(date(2026,6,30),date(2026,7,2))).amount == Decimal('2820.00')
    monkeypatch.setenv('HOLY_WEEK_RANGES','2027-03-20:2027-03-29')
    assert is_high_season(date(2027,3,22))
    with pytest.raises(ValueError): is_high_season(date(2027,3,22),'bad')

def test_reservation_state_and_confirmation():
    r=reservation()
    with pytest.raises(ValueError): r.confirm()
    with pytest.raises(ValueError): r.confirm(Money(1100))
    r.confirm(Money(1200))
    with pytest.raises(ValueError): r.confirm(Money(1200))
    assert r.status==ReservationStatus.CONFIRMADA
    assert r.cancel(datetime(2026,11,4,10)).amount == Decimal('1200.00')
    with pytest.raises(ValueError): r.cancel(datetime(2026,11,4,11))

def test_cancel_under_48_and_no_show():
    r=reservation();r.confirm(Money(1200))
    assert r.cancel(datetime(2026,11,5,11)).amount==Decimal('600.00')
    n=reservation();n.confirm(card_guarantee=True)
    with pytest.raises(ValueError):n.declare_no_show(datetime(2026,11,6,23,58))
    assert n.declare_no_show(datetime(2026,11,7,0)).amount == Decimal('1200.00')

def test_room_states_and_cleaning():
    r=Room('001',RoomType.ESTANDAR,2)
    assert CapacitySpecification(2).is_satisfied_by(r)
    assert not CapacitySpecification(3).is_satisfied_by(r)
    assert ReadyRoomSpecification().is_satisfied_by(r)
    r.occupy()
    assert not ReadyRoomSpecification().is_satisfied_by(r)
    r.mark_dirty(datetime(2026,11,8,12))
    with pytest.raises(ValueError):r.mark_clean_inspected(datetime(2026,11,8,12,34))
    r.mark_clean_inspected(datetime(2026,11,8,12,35))
    r.block('fuga',date(2026,11,10))
    with pytest.raises(ValueError):r.mark_clean_inspected()
    r.reactivate();r.mark_clean_inspected()
    assert r.status==RoomStatus.LIMPIA
    with pytest.raises(ValueError):room_transition(RoomStatus.SUCIA,RoomStatus.OCUPADA)
    with pytest.raises(ValueError):reservation_transition(ReservationStatus.PENDIENTE,ReservationStatus.NO_SHOW)

def test_overlap_includes_pending_hold():
    r=reservation()
    spec=NoOverlapSpecification(r.dates,[r])
    assert not spec.is_satisfied_by(Room('001',RoomType.ESTANDAR,2))
    assert spec.is_satisfied_by(Room('002',RoomType.ESTANDAR,2))
    assert DateRange(date(2026,11,8),date(2026,11,9)).overlaps(r.dates) is False

def test_folio_requires_signature_inspection_and_payment():
    f=Folio(1,'001','Ana')
    with pytest.raises(ValueError):f.add_charge('Cena',Money(200),'')
    f.add_charge('Cena',Money(200),'firma de prueba')
    with pytest.raises(ValueError):f.close()
    with pytest.raises(ValueError):f.inspect(datetime(2026,11,8,12,5))
    f.request_inspection(datetime(2026,11,8,12))
    with pytest.raises(ValueError):f.inspect(datetime(2026,11,8,12,4))
    f.inspect(datetime(2026,11,8,12,5))
    with pytest.raises(ValueError):f.close()
    f.pay(Money(200),'efectivo');f.close()
    with pytest.raises(ValueError):f.pay(Money(10),'efectivo')
