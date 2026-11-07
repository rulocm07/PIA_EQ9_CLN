"""Repository + Unit of Work transaccional para SQLite (local) / PostgreSQL (Compose).

SQLite usa BEGIN IMMEDIATE para serializar la asignación; PostgreSQL usa
pg_advisory_xact_lock por categoría. Nunca reutilizar IDs con MAX(id)+1.
"""
import json
import os
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, ForeignKey, select, func, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import NullPool
from src.domain.hotel import (
    Room, RoomType, RoomStatus, Reservation, ReservationStatus, DateRange, Money, Folio
)

class Base(DeclarativeBase): pass

class RoomRow(Base):
    __tablename__ = 'rooms'
    number = Column(String(8), primary_key=True)
    room_type = Column(String(24), nullable=False)
    capacity = Column(Integer, nullable=False)
    status = Column(String(32), nullable=False)
    reason = Column(Text)
    reactivation = Column(String(10))
    dirty_since = Column(String(32))

class ReservationRow(Base):
    __tablename__ = 'reservations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    guest = Column(String(160), nullable=False)
    check_in = Column(String(10), nullable=False)
    check_out = Column(String(10), nullable=False)
    room_type = Column(String(24), nullable=False)
    guests = Column(Integer, nullable=False)
    total = Column(String(32), nullable=False)
    status = Column(String(24), nullable=False)
    deposit = Column(String(32), nullable=False)
    card_guarantee = Column(Boolean, nullable=False)
    room_number = Column(String(8), ForeignKey('rooms.number'), nullable=False)

class FolioRow(Base):
    __tablename__ = 'folios'
    id = Column(Integer, primary_key=True, autoincrement=True)
    reservation_id = Column(Integer, ForeignKey('reservations.id'), unique=True, nullable=False)
    room_number = Column(String(8), nullable=False)
    guest = Column(String(160), nullable=False)
    charges = Column(Text, nullable=False)
    payments = Column(Text, nullable=False)
    inspected = Column(Boolean, nullable=False)
    closed = Column(Boolean, nullable=False)
    incidental = Column(String(32))
    inspection_requested_at = Column(String(32))
    inspection_completed_at = Column(String(32))
    document_type = Column(String(16))
    companions = Column(Text, nullable=False)

class EventRow(Base):
    __tablename__ = 'audit_events'
    id = Column(Integer, primary_key=True, autoincrement=True)
    at = Column(String(32), nullable=False)
    event_type = Column(String(80), nullable=False)
    entity_id = Column(String(32), nullable=False)
    detail = Column(Text, nullable=False)

class SQLiteRepository:
    """Nombre de compatibilidad; dialecto configurado mediante DATABASE_URL."""
    def __init__(self, db_path=None, database_url=None):
        # Prioridad: URL explícita > ruta explícita > variable de entorno > SQLite local.
        # Las pruebas unitarias proporcionan db_path para aislar cada caso, incluso
        # cuando Docker define DATABASE_URL para las pruebas de integración.
        if database_url is not None:
            url = database_url
        elif db_path is not None:
            path = str(db_path)
            if path != ':memory:':
                Path(path).parent.mkdir(parents=True, exist_ok=True)
            url = f'sqlite:///{path}'
        else:
            url = os.getenv('DATABASE_URL')
            if not url:
                path = os.getenv('DATABASE_PATH', './hotel_v2.db')
                if path != ':memory:':
                    Path(path).parent.mkdir(parents=True, exist_ok=True)
                url = f'sqlite:///{path}'
        if url.startswith('postgres://'):
            url = 'postgresql+psycopg://' + url[len('postgres://'):]
        elif url.startswith('postgresql://'):
            url = 'postgresql+psycopg://' + url[len('postgresql://'):]
        # Un archivo nuevo v2 evita reescribir la BD heredada; ver README (migración).
        kwargs = {'connect_args':{'timeout':30, 'check_same_thread':False}, 'poolclass':NullPool} if url.startswith('sqlite:') else {'pool_pre_ping':True}
        self.engine = create_engine(url, **kwargs)
        self.is_sqlite = self.engine.dialect.name == 'sqlite'
        self.Session = sessionmaker(self.engine, expire_on_commit=False)
        self.initialize()

    def initialize(self):
        Base.metadata.create_all(self.engine)
        with self.uow() as u:
            if not u.session.scalar(select(func.count()).select_from(RoomRow)):
                for i in range(1,121):
                    rt = RoomType.ESTANDAR if i<=60 else RoomType.DOBLE if i<=100 else RoomType.SUITE
                    u.session.add(RoomRow(number=f'{i:03}',room_type=rt.value,capacity=2 if i<=60 else 4,status=RoomStatus.LIMPIA.value))

    @contextmanager
    def uow(self, lock_type=None):
        with self.Session() as session:
            with session.begin():
                if self.is_sqlite:
                    session.connection().exec_driver_sql('BEGIN IMMEDIATE')
                else:
                    # Todas las mutaciones comparten un bloqueo global corto: consistente entre réplicas.
                    session.execute(text('SELECT pg_advisory_xact_lock(90)'))
                if not self.is_sqlite and lock_type:
                    # Bloqueo serializable por categoría para evitar asignaciones simultáneas.
                    lock_id = {RoomType.ESTANDAR: 91, RoomType.DOBLE: 92, RoomType.SUITE: 93}[RoomType(lock_type)]
                    session.execute(text('SELECT pg_advisory_xact_lock(:key)'), {'key':lock_id})
                yield UnitOfWork(session)

    def rooms(self):
        with self.Session() as s: return [to_room(x) for x in s.scalars(select(RoomRow).order_by(RoomRow.number))]
    def reservations(self):
        with self.Session() as s: return [to_reservation(x) for x in s.scalars(select(ReservationRow).order_by(ReservationRow.id))]
    def folios(self):
        with self.Session() as s: return [to_folio(x) for x in s.scalars(select(FolioRow).order_by(FolioRow.id))]
    def events(self):
        with self.Session() as s: return [{'at':x.at,'type':x.event_type,'entity_id':x.entity_id,'detail':json.loads(x.detail)} for x in s.scalars(select(EventRow).order_by(EventRow.id))]

class UnitOfWork:
    def __init__(self, session): self.session = session
    def rooms(self): return [to_room(x) for x in self.session.scalars(select(RoomRow).order_by(RoomRow.number))]
    def room(self, number):
        x = self.session.get(RoomRow, number)
        if not x: raise ValueError('Habitación no encontrada')
        return to_room(x)
    def reservations(self): return [to_reservation(x) for x in self.session.scalars(select(ReservationRow).order_by(ReservationRow.id))]
    def reservation(self, reservation_id):
        x = self.session.get(ReservationRow, int(reservation_id))
        if not x: raise ValueError('Reserva no encontrada')
        return to_reservation(x)
    def save_room(self, room):
        r = self.session.get(RoomRow, room.number)
        if r is None: raise ValueError('Habitación no encontrada')
        r.status=room.status.value; r.reason=room.out_of_service_reason
        r.reactivation=room.reactivation_date.isoformat() if room.reactivation_date else None
        r.dirty_since=room.dirty_since.isoformat() if room.dirty_since else None
    def save_reservation(self, r):
        row = self.session.get(ReservationRow, r.id) if r.id else None
        if row is None:
            row = ReservationRow(); self.session.add(row)
        row.guest=r.guest_name; row.check_in=r.dates.check_in.isoformat();row.check_out=r.dates.check_out.isoformat()
        row.room_type=r.room_type.value;row.guests=r.guests;row.total=str(r.total.amount)
        row.status=r.status.value;row.deposit=str(r.deposit.amount);row.card_guarantee=r.card_guarantee;row.room_number=r.room_number
        self.session.flush()
        r.id=row.id
    def folio_for_reservation(self, reservation_id):
        row = self.session.scalar(select(FolioRow).where(FolioRow.reservation_id==reservation_id))
        return to_folio(row) if row else None
    def folio(self, folio_id):
        row = self.session.get(FolioRow, int(folio_id))
        if not row: raise ValueError('Folio no encontrado')
        return to_folio(row)
    def save_folio(self, folio, reservation_id):
        row = self.session.get(FolioRow, folio.id) if folio.id else None
        if row is None:
            row=FolioRow(reservation_id=reservation_id); self.session.add(row)
        row.room_number=folio.room_number;row.guest=folio.guest_name
        row.charges=json.dumps(folio.charges,ensure_ascii=False);row.payments=json.dumps(folio.payments,ensure_ascii=False)
        row.inspected=folio.inspected;row.closed=folio.closed
        row.incidental=str(folio.incidental_guarantee.amount) if folio.incidental_guarantee else None
        row.inspection_requested_at=folio.inspection_requested_at.isoformat() if folio.inspection_requested_at else None
        row.inspection_completed_at=folio.inspection_completed_at.isoformat() if folio.inspection_completed_at else None
        row.document_type=folio.document_type;row.companions=json.dumps(folio.companions,ensure_ascii=False)
        self.session.flush();folio.id=row.id
    def has_event(self,event_type,entity_id):
        return self.session.scalar(select(func.count()).select_from(EventRow).where(EventRow.event_type==event_type,EventRow.entity_id==str(entity_id)))>0
    def audit(self, event_type, entity_id, detail=None, now=None):
        self.session.add(EventRow(at=(now or datetime.now()).isoformat(),event_type=event_type,entity_id=str(entity_id),detail=json.dumps(detail or {},ensure_ascii=False)))

def to_room(row):
    return Room(row.number,RoomType(row.room_type),row.capacity,RoomStatus(row.status),row.reason,date.fromisoformat(row.reactivation) if row.reactivation else None,datetime.fromisoformat(row.dirty_since) if row.dirty_since else None)
def to_reservation(row):
    return Reservation(row.id,row.guest,DateRange(date.fromisoformat(row.check_in),date.fromisoformat(row.check_out)),RoomType(row.room_type),row.guests,Money(Decimal(row.total)),ReservationStatus(row.status),Money(Decimal(row.deposit)),bool(row.card_guarantee),row.room_number)
def to_folio(row):
    return Folio(row.id,row.room_number,row.guest,json.loads(row.charges),row.inspected,row.closed,Money(Decimal(row.incidental)) if row.incidental else None,json.loads(row.payments),datetime.fromisoformat(row.inspection_requested_at) if row.inspection_requested_at else None,datetime.fromisoformat(row.inspection_completed_at) if row.inspection_completed_at else None,row.document_type,json.loads(row.companions))
