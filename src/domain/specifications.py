"""Specification: criterios combinables de disponibilidad."""
from dataclasses import dataclass
from .hotel import Room, RoomStatus, RoomType, DateRange, Reservation, ReservationStatus

class Specification:
    def is_satisfied_by(self, candidate): raise NotImplementedError
    def __and__(self, other): return AndSpecification(self, other)

@dataclass
class AndSpecification(Specification):
    left: Specification
    right: Specification
    def is_satisfied_by(self, candidate):
        return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(candidate)

@dataclass
class CapacitySpecification(Specification):
    guests: int
    def is_satisfied_by(self, room: Room): return 0 < self.guests <= room.capacity

@dataclass
class RoomTypeSpecification(Specification):
    room_type: RoomType
    def is_satisfied_by(self, room: Room): return room.room_type == self.room_type

@dataclass
class ReadyRoomSpecification(Specification):
    # Para check-in la habitación SÍ debe estar lista ahora.
    def is_satisfied_by(self, room: Room): return room.status == RoomStatus.LIMPIA

@dataclass
class BookingRoomSpecification(Specification):
    # Una habitación ocupada puede reservarse para fechas posteriores no solapadas;
    # antes de check-in se volverá a exigir estado LIMPIA.
    def is_satisfied_by(self, room: Room):
        return room.status not in (RoomStatus.SUCIA, RoomStatus.FUERA_SERVICIO)

@dataclass
class NoOverlapSpecification(Specification):
    dates: DateRange
    reservations: list[Reservation]
    def is_satisfied_by(self, room: Room):
        holding = (ReservationStatus.PENDIENTE, ReservationStatus.CONFIRMADA, ReservationStatus.CHECKED_IN)
        return not any(r.room_number == room.number and r.status in holding and r.dates.overlaps(self.dates) for r in self.reservations)
