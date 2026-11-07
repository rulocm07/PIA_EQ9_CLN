"""Transiciones de habitación y reserva, empleadas por entidades reales."""
from .hotel import RoomStatus, ReservationStatus

ROOM_TRANSITIONS = {
    RoomStatus.LIMPIA: {RoomStatus.OCUPADA, RoomStatus.FUERA_SERVICIO},
    RoomStatus.OCUPADA: {RoomStatus.SUCIA},
    RoomStatus.SUCIA: {RoomStatus.LIMPIA, RoomStatus.FUERA_SERVICIO},
    RoomStatus.FUERA_SERVICIO: {RoomStatus.SUCIA},
}
RESERVATION_TRANSITIONS = {
    ReservationStatus.PENDIENTE: {ReservationStatus.CONFIRMADA},
    ReservationStatus.CONFIRMADA: {ReservationStatus.CANCELADA, ReservationStatus.NO_SHOW, ReservationStatus.CHECKED_IN},
    ReservationStatus.CHECKED_IN: {ReservationStatus.COMPLETADA},
    ReservationStatus.CANCELADA: set(), ReservationStatus.NO_SHOW: set(), ReservationStatus.COMPLETADA: set(),
}
def transition(current, target, transitions):
    if target not in transitions[current]: raise ValueError(f'Transición inválida: {current} -> {target}')
    return target

def room_transition(current, target): return transition(current, target, ROOM_TRANSITIONS)
def reservation_transition(current, target): return transition(current, target, RESERVATION_TRANSITIONS)
