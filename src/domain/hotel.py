"""Dominio del Hotel Costa Azul. Sin dependencia de SQL ni HTTP.
Reglas de negocio: BR-01...BR-20 (ver docs/BRD.md).
"""
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
import os

CENT = Decimal('0.01')

def money(value):
    result = Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)
    if not result.is_finite():
        raise ValueError('Monto no válido')
    return result

class RoomType(str, Enum):
    ESTANDAR = 'Estándar'
    DOBLE = 'Doble'
    SUITE = 'Suite'

class RoomStatus(str, Enum):
    LIMPIA = 'Limpia/Inspeccionada'
    SUCIA = 'Sucia'
    OCUPADA = 'Ocupada'
    FUERA_SERVICIO = 'Fuera de Servicio'

class ReservationStatus(str, Enum):
    PENDIENTE = 'Pendiente'
    CONFIRMADA = 'Confirmada'
    CANCELADA = 'Cancelada'
    NO_SHOW = 'No-Show'
    CHECKED_IN = 'Checked-in'
    COMPLETADA = 'Completada'

BASE_RATES = {RoomType.ESTANDAR: Decimal('1200'), RoomType.DOBLE: Decimal('1800'), RoomType.SUITE: Decimal('3000')}
CAPACITIES = {RoomType.ESTANDAR: 2, RoomType.DOBLE: 4, RoomType.SUITE: 4}
ROOM_RANK = {RoomType.ESTANDAR: 0, RoomType.DOBLE: 1, RoomType.SUITE: 2}

@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = 'MXN'
    def __post_init__(self):
        value = money(self.amount)
        if value < 0: raise ValueError('El monto no puede ser negativo')
        if self.currency != 'MXN': raise ValueError('Solo MXN')
        object.__setattr__(self, 'amount', value)

@dataclass(frozen=True)
class DateRange:
    check_in: date
    check_out: date
    def __post_init__(self):
        if self.check_out <= self.check_in: raise ValueError('La salida debe ser posterior a la llegada')
    @property
    def nights(self): return (self.check_out - self.check_in).days
    def overlaps(self, other): return self.check_in < other.check_out and other.check_in < self.check_out

@dataclass
class Room:
    number: str
    room_type: RoomType
    capacity: int
    status: RoomStatus = RoomStatus.LIMPIA
    out_of_service_reason: str | None = None
    reactivation_date: date | None = None
    dirty_since: datetime | None = None
    def block(self, reason: str, reactivation_date: date):
        from .state_machine import room_transition
        if not reason.strip(): raise ValueError('Debe indicar motivo de mantenimiento')
        self.status = room_transition(self.status, RoomStatus.FUERA_SERVICIO)
        self.out_of_service_reason = reason.strip()
        self.reactivation_date = reactivation_date
    def reactivate(self):
        from .state_machine import room_transition
        self.status = room_transition(self.status, RoomStatus.SUCIA)
        self.out_of_service_reason = None
        self.reactivation_date = None
        self.dirty_since = None
    def occupy(self):
        from .state_machine import room_transition
        self.status = room_transition(self.status, RoomStatus.OCUPADA)
    def mark_dirty(self, now):
        from .state_machine import room_transition
        self.status = room_transition(self.status, RoomStatus.SUCIA)
        self.dirty_since = now
    def mark_clean_inspected(self, now=None):
        from .state_machine import room_transition
        if self.dirty_since is not None:
            if now is None: now = datetime.now()
            if now < self.dirty_since + timedelta(minutes=35):
                raise ValueError('La limpieza requiere un mínimo de 35 minutos desde la salida')
        self.status = room_transition(self.status, RoomStatus.LIMPIA)
        self.dirty_since = None

@dataclass
class Reservation:
    id: int
    guest_name: str
    dates: DateRange
    room_type: RoomType
    guests: int
    total: Money
    status: ReservationStatus = ReservationStatus.PENDIENTE
    deposit: Money = field(default_factory=lambda: Money(Decimal('0')))
    card_guarantee: bool = False
    room_number: str | None = None
    def confirm(self, deposit: Money | None = None, card_guarantee: bool = False):
        from .state_machine import reservation_transition
        if not deposit and not card_guarantee: raise ValueError('Se requiere anticipo del 50% o tarjeta en garantía')
        if deposit and deposit.amount < money(self.total.amount * Decimal('0.50')):
            raise ValueError('El anticipo debe ser al menos el 50%')
        if deposit and deposit.amount > self.total.amount:
            raise ValueError('El anticipo excede la estancia')
        self.status = reservation_transition(self.status, ReservationStatus.CONFIRMADA)
        self.deposit = deposit or Money(Decimal('0'))
        self.card_guarantee = card_guarantee
    def cancel(self, now: datetime):
        from .state_machine import reservation_transition
        if self.status != ReservationStatus.CONFIRMADA: raise ValueError('Solo se cancela una reserva confirmada')
        hours = (datetime.combine(self.dates.check_in, time(15)) - now).total_seconds() / 3600
        if hours < 0: raise ValueError('Ya comenzó el día de llegada; se aplica la política de no-show')
        refund = self.deposit.amount if hours > 48 else money(self.deposit.amount * Decimal('0.50'))
        self.status = reservation_transition(self.status, ReservationStatus.CANCELADA)
        return Money(refund)
    def declare_no_show(self, now: datetime):
        from .state_machine import reservation_transition
        if now < datetime.combine(self.dates.check_in,time(23,59)):
            raise ValueError('No-show solo a partir de las 23:59 del día de llegada')
        self.status = reservation_transition(self.status, ReservationStatus.NO_SHOW)
        return Money(nightly_rate(self.room_type, self.dates.check_in).amount)
    def check_in_guest(self):
        from .state_machine import reservation_transition
        self.status = reservation_transition(self.status, ReservationStatus.CHECKED_IN)
    def complete(self):
        from .state_machine import reservation_transition
        self.status = reservation_transition(self.status, ReservationStatus.COMPLETADA)

@dataclass
class Folio:
    id: int
    room_number: str
    guest_name: str
    charges: list = field(default_factory=list)
    inspected: bool = False
    closed: bool = False
    incidental_guarantee: Money | None = None
    payments: list = field(default_factory=list)
    inspection_requested_at: datetime | None = None
    inspection_completed_at: datetime | None = None
    document_type: str | None = None
    companions: list = field(default_factory=list)
    def add_charge(self, description: str, amount: Money, signature: str):
        if self.closed: raise ValueError('El folio está cerrado')
        if not description.strip(): raise ValueError('Descripción obligatoria')
        if not signature or not signature.strip(): raise ValueError('El consumo requiere firma')
        self.charges.append({'description':description.strip(), 'amount':str(amount.amount), 'signature':signature.strip()})
    def adjustment(self, description: str, value: Decimal):
        if self.closed: raise ValueError('El folio está cerrado')
        self.charges.append({'description':description, 'amount':str(money(value)), 'signature':'ajuste-sistema'})
    @property
    def total(self): return money(sum((Decimal(x['amount']) for x in self.charges), Decimal('0')))
    @property
    def paid(self): return money(sum((Decimal(x['amount']) for x in self.payments), Decimal('0')))
    @property
    def balance(self): return money(self.total - self.paid)
    def pay(self, amount: Money, method: str, now=None):
        if self.closed: raise ValueError('Folio cerrado')
        if amount.amount <= 0: raise ValueError('Pago debe ser positivo')
        if method not in ('efectivo', 'terminal', 'transferencia', 'anticipo'): raise ValueError('Método de pago inválido')
        self.payments.append({'amount':str(amount.amount), 'method':method, 'at':(now or datetime.now()).isoformat()})
    def request_inspection(self, now):
        if self.closed: raise ValueError('Folio cerrado')
        self.inspected = False; self.inspection_requested_at = now; self.inspection_completed_at = None
    def inspect(self, now):
        if self.inspection_requested_at is None: raise ValueError('Debe solicitarse la inspección')
        if now < self.inspection_requested_at + timedelta(minutes=5):
            raise ValueError('La inspección exprés requiere 5 minutos')
        self.inspected = True; self.inspection_completed_at = now
    def close(self):
        if not self.inspected: raise ValueError('Se requiere inspección exprés antes de cerrar')
        if self.balance > 0: raise ValueError('El folio tiene saldo pendiente')
        self.closed = True

def is_high_season(day: date, ranges: str | None = None):
    # Semana Santa no tiene fechas fijas; el calendario es una configuración explícita.
    if day.month in (7,8,12): return True
    if ranges is None: ranges = os.getenv('HOLY_WEEK_RANGES', '')
    for item in filter(None, ranges.split(',')):
        try:
            start, end = item.strip().split(':')
            if date.fromisoformat(start) <= day <= date.fromisoformat(end): return True
        except (ValueError, TypeError):
            raise ValueError('HOLY_WEEK_RANGES debe usar YYYY-MM-DD:YYYY-MM-DD')
    return False

def nightly_rate(room_type: RoomType, day: date):
    base = BASE_RATES[room_type]
    return Money(base * (Decimal('1.35') if is_high_season(day) else Decimal('1')))

def stay_total(room_type: RoomType, dates: DateRange):
    return Money(sum((nightly_rate(room_type, dates.check_in + timedelta(days=i)).amount for i in range(dates.nights)), Decimal('0')))
