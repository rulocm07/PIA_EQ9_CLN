"""Casos de uso del Hotel Costa Azul; cada comando escribe en un Unit of Work.
Se inyecta repositorio. No hay referencias HTTP ni SQL en dominio.
"""
from datetime import datetime, date, time, timedelta
from decimal import Decimal
import hashlib
import hmac
import os
from src.domain.hotel import (
    RoomType, RoomStatus, ReservationStatus, Money, DateRange, Reservation, Folio,
    CAPACITIES, ROOM_RANK, nightly_rate, stay_total, money
)
from src.domain.specifications import (
    RoomTypeSpecification, CapacitySpecification, BookingRoomSpecification,
    ReadyRoomSpecification, NoOverlapSpecification
)

class HotelService:
    def __init__(self, repository): self.repo = repository

    @staticmethod
    def _dates(check_in, check_out):
        return DateRange(date.fromisoformat(str(check_in)),date.fromisoformat(str(check_out)))

    @staticmethod
    def _eligible(rooms,reservations,dates,room_type,guests,checkin=False):
        spec=(RoomTypeSpecification(room_type)&CapacitySpecification(guests)&
              (ReadyRoomSpecification() if checkin else BookingRoomSpecification()) &
              NoOverlapSpecification(dates,reservations))
        return [r for r in rooms if spec.is_satisfied_by(r)]

    def availability(self, check_in, check_out, room_type, guests):
        dates=self._dates(check_in,check_out); room_type=RoomType(room_type);guests=int(guests)
        if guests<1: raise ValueError('Mínimo un huésped')
        valid=self._eligible(self.repo.rooms(),self.repo.reservations(),dates,room_type,guests)
        return [{'number':r.number,'type':r.room_type.value,'capacity':r.capacity,
                 'rate_per_night_mxn':str(nightly_rate(r.room_type,dates.check_in).amount),
                 'total_mxn':str(stay_total(r.room_type,dates).amount)} for r in valid]

    def create_reservation(self, payload):
        dates=self._dates(payload['check_in'],payload['check_out'])
        room_type=RoomType(payload['room_type']); guests=int(payload['guests'])
        name=payload['guest_name'].strip()
        if len(name)<2: raise ValueError('Nombre de huésped requerido')
        if guests<1 or guests>CAPACITIES[room_type]: raise ValueError('La capacidad del tipo de habitación es insuficiente')
        # Bloqueo del tipo de habitación por toda la transacción: evita overbooking bajo concurrencia.
        with self.repo.uow(lock_type=room_type) as u:
            eligible=self._eligible(u.rooms(),u.reservations(),dates,room_type,guests)
            if not eligible: raise ValueError('Sin habitaciones disponibles para ese intervalo')
            room=eligible[0]
            r=Reservation(0,name,dates,room_type,guests,stay_total(room_type,dates),room_number=room.number)
            u.save_reservation(r)
            u.audit('ReservaCreada',r.id,{'room':room.number,'dates':[str(dates.check_in),str(dates.check_out)]})
        return r

    def confirm(self, reservation_id, deposit=None, card_guarantee=False):
        with self.repo.uow() as u:
            r=u.reservation(reservation_id)
            r.confirm(Money(money(deposit)) if deposit is not None else None,card_guarantee)
            u.save_reservation(r);u.audit('ReservaConfirmada',r.id,{'room':r.room_number})
        return r

    def cancel(self, reservation_id, now=None, waive_penalty=False, admin_pin=None):
        now=now or datetime.now()
        with self.repo.uow() as u:
            r=u.reservation(reservation_id);refund=r.cancel(now)
            if waive_penalty:
                self.verify_admin_pin(admin_pin or '')
                refund=Money(r.deposit.amount)
            u.save_reservation(r)
            u.audit('ReservaCancelada',r.id,{'refund_mxn':str(refund.amount),'penalty_mxn':str(money(r.deposit.amount-refund.amount)),'penalty_waived':waive_penalty},now)
        # Reembolso registrado de forma lógica; NO se transfiere dinero desde API.
        return {'id':r.id,'status':r.status.value,'refund_mxn':str(refund.amount),'penalty_mxn':str(money(r.deposit.amount-refund.amount)),'settlement':'simulado'}

    def process_no_shows(self, now=None):
        now=now or datetime.now()
        processed=[]
        with self.repo.uow() as u:
            for r in u.reservations():
                threshold=datetime.combine(r.dates.check_in,time(23,59))
                if r.status==ReservationStatus.CONFIRMADA and threshold<=now:
                    charge=r.declare_no_show(now)
                    u.save_reservation(r)
                    u.audit('NoShowDeclarado',r.id,{'charge_first_night_mxn':str(charge.amount),'card_charge':'simulado' if r.card_guarantee else 'pendiente-sin-tarjeta'},now)
                    processed.append({'reservation_id':r.id,'charge_first_night_mxn':str(charge.amount),'card_charge':'simulado' if r.card_guarantee else 'pendiente-sin-tarjeta'})
        return processed

    def check_in(self, reservation_id, document_type, companions, incidental_type, now=None):
        now=now or datetime.now()
        if document_type not in ('INE','Pasaporte'): raise ValueError('Documento debe ser INE o Pasaporte')
        if incidental_type not in ('voucher','efectivo'): raise ValueError('Garantía incidental voucher o efectivo')
        with self.repo.uow() as u:
            r=u.reservation(reservation_id)
            if r.status!=ReservationStatus.CONFIRMADA: raise ValueError('La reserva debe estar confirmada')
            if now.date()!=r.dates.check_in: raise ValueError('Check-in solo en fecha de llegada; revisar fechas o no-show')
            if len(companions)!=r.guests-1 or any(not c.strip() for c in companions):
                raise ValueError('Deben registrarse los nombres de los acompañantes')
            room=u.room(r.room_number)
            if room.status!=RoomStatus.LIMPIA: raise ValueError('Habitación debe estar limpia e inspeccionada')
            room.occupy();r.check_in_guest()
            folio=Folio(0,room.number,r.guest_name,document_type=document_type,
                        companions=companions,incidental_guarantee=Money(1000 if incidental_type=='voucher' else 500))
            folio.adjustment('Hospedaje',r.total.amount)
            if r.deposit.amount: folio.pay(r.deposit,'anticipo',now=now)
            # Before 12:00, 30% daily rate. From 12:00 onward, zero early fee (BR-09).
            if now.time()<time(12,0):
                folio.adjustment('Early check-in 30%',money(nightly_rate(r.room_type,r.dates.check_in).amount*Decimal('0.30')))
            u.save_room(room);u.save_reservation(r);u.save_folio(folio,r.id)
            u.audit('CheckInCompletado',r.id,{'room':room.number,'folio_id':folio.id},now)
        return {'reservation_id':r.id,'room_number':room.number,'status':r.status.value,'folio_id':folio.id,'balance_mxn':str(folio.balance)}

    def add_consumption(self, folio_id, category, description, amount, signature, room_number, now=None):
        if category not in ('restaurante/bar','lavandería','estacionamiento'):
            raise ValueError('Consumo debe ser de restaurante/bar, lavandería o estacionamiento')
        amount=Money(money(amount))
        if amount.amount<=0: raise ValueError('El monto debe ser mayor a cero')
        with self.repo.uow() as u:
            folio=u.folio(folio_id)
            if folio.room_number!=room_number: raise ValueError('El número de habitación no corresponde al folio')
            folio.add_charge(f'{category}: {description}',amount,signature)
            reservation_id=self._reservation_id_of_folio(u,folio.id)
            u.save_folio(folio,reservation_id)
            u.audit('ConsumoRegistrado',folio.id,{'amount_mxn':str(amount.amount),'category':category},now)
        return self.folio(folio.id)

    @staticmethod
    def _reservation_id_of_folio(u, folio_id):
        from sqlalchemy import select
        from src.infrastructure.repository import FolioRow
        return u.session.scalar(select(FolioRow.reservation_id).where(FolioRow.id==folio_id))

    def pay_folio(self, folio_id, amount, method, now=None):
        now=now or datetime.now()
        if method not in ('efectivo','terminal','transferencia'):
            raise ValueError('Método de pago válido: efectivo, terminal o transferencia')
        with self.repo.uow() as u:
            f=u.folio(folio_id)
            f.pay(Money(money(amount)),method,now=now)
            u.save_folio(f,self._reservation_id_of_folio(u,folio_id))
            u.audit('PagoRegistrado',folio_id,{'amount_mxn':str(money(amount)),'method':method},now)
        return self.folio(folio_id)

    def request_inspection(self, folio_id, now=None):
        now=now or datetime.now()
        with self.repo.uow() as u:
            f=u.folio(folio_id);f.request_inspection(now)
            u.save_folio(f,self._reservation_id_of_folio(u,folio_id))
            u.audit('InspeccionSolicitada',f.id,{},now)
        return self.folio(folio_id)

    def complete_inspection(self, folio_id, now=None):
        now=now or datetime.now()
        with self.repo.uow() as u:
            f=u.folio(folio_id);f.inspect(now)
            u.save_folio(f,self._reservation_id_of_folio(u,folio_id))
            u.audit('InspeccionCompletada',f.id,{},now)
        return self.folio(folio_id)

    def preview_checkout(self, reservation_id, now=None):
        now=now or datetime.now()
        with self.repo.uow() as u:
            r=u.reservation(reservation_id); f=u.folio_for_reservation(r.id)
            if r.status!=ReservationStatus.CHECKED_IN or not f: raise ValueError('Reserva sin estancia activa')
            fee=self._late_checkout_fee(r,now)
            return {'folio_id':f.id,'late_fee_mxn':str(fee),'balance_with_late_fee_mxn':str(money(f.balance+fee)),'inspection_complete':f.inspected}

    @staticmethod
    def _late_checkout_fee(r,now):
        if now.date()!=r.dates.check_out: return Decimal('0')
        daily=nightly_rate(r.room_type,r.dates.check_out-timedelta(days=1)).amount
        if now.time()>time(15,0): return daily
        if now.time()>time(12,0): return money(daily*Decimal('0.30'))
        return Decimal('0')

    def check_out(self,reservation_id,now=None):
        now=now or datetime.now()
        with self.repo.uow() as u:
            r=u.reservation(reservation_id)
            if r.status!=ReservationStatus.CHECKED_IN: raise ValueError('Se requiere check-in previo')
            f=u.folio_for_reservation(r.id)
            if not f: raise ValueError('Folio no encontrado')
            if now.date()!=r.dates.check_out: raise ValueError('Check-out fuera de la fecha prevista; registre primero una salida anticipada o regularice la extensión')
            fee=self._late_checkout_fee(r,now)
            if fee: f.adjustment('Late check-out',fee)
            f.close()  # inspección y saldo pagado. Rollback también del cargo tardío.
            room=u.room(r.room_number);room.mark_dirty(now);r.complete()
            u.save_folio(f,r.id);u.save_room(room);u.save_reservation(r)
            u.audit('CheckOutCompletado',r.id,{'folio_id':f.id,'late_fee_mxn':str(fee)},now)
        return {'status':r.status.value,'folio_id':f.id,'room_status':room.status.value,'total_mxn':str(f.total)}

    def clean_room(self,room_number,now=None):
        now=now or datetime.now()
        with self.repo.uow() as u:
            room=u.room(room_number);room.mark_clean_inspected(now);u.save_room(room)
            u.audit('HabitacionLimpia',room.number,{},now)
        return room

    def block_room(self,room_number,reason,reactivation,actor_role,now=None):
        if actor_role not in ('Administración','Supervisor de Mantenimiento'):
            raise ValueError('Solo Administración o Supervisor de Mantenimiento')
        with self.repo.uow() as u:
            room=u.room(room_number)
            if room.status==RoomStatus.OCUPADA: raise ValueError('Primero reubique al huésped')
            if any(r.room_number==room_number and r.status in (ReservationStatus.PENDIENTE,ReservationStatus.CONFIRMADA) for r in u.reservations()):
                raise ValueError('La habitación tiene reservas futuras; se requiere reasignarlas antes del bloqueo')
            room.block(reason,date.fromisoformat(str(reactivation)));u.save_room(room)
            u.audit('HabitacionFueraServicio',room.number,{'reason':reason,'actor_role':actor_role},now)
        return room

    def reactivate_room(self,room_number,actor_role,now=None):
        if actor_role not in ('Administración','Supervisor de Mantenimiento'):
            raise ValueError('Solo Administración o Supervisor de Mantenimiento')
        with self.repo.uow() as u:
            room=u.room(room_number);room.reactivate();u.save_room(room)
            u.audit('HabitacionReactivada',room.number,{'actor_role':actor_role},now)
        return room

    def change_room(self,reservation_id,new_room_number,reason,now=None):
        now=now or datetime.now()
        if reason not in ('avería','upgrade'): raise ValueError('Cambio por avería o upgrade')
        with self.repo.uow() as u:
            r=u.reservation(reservation_id)
            if r.status!=ReservationStatus.CHECKED_IN: raise ValueError('Cambio exige estancia activa')
            old=u.room(r.room_number);new=u.room(new_room_number)
            if old.number==new.number: raise ValueError('La nueva habitación debe ser distinta')
            if new.status!=RoomStatus.LIMPIA: raise ValueError('La nueva habitación debe estar lista')
            if new.capacity<r.guests: raise ValueError('Capacidad insuficiente')
            if ROOM_RANK[new.room_type]<ROOM_RANK[old.room_type]: raise ValueError('No se permite bajar categoría')
            remaining=DateRange(now.date(),r.dates.check_out) if now.date()<r.dates.check_out else None
            if remaining:
                # Ignora temporalmente la reserva propia al comprobar ocupación.
                overlapping=NoOverlapSpecification(remaining,[x for x in u.reservations() if x.id!=r.id])
                if not overlapping.is_satisfied_by(new): raise ValueError('Nueva habitación ya reservada')
            f=u.folio_for_reservation(r.id)
            if not f: raise ValueError('No hay folio')
            extra=Decimal('0')
            if reason=='upgrade' and remaining:
                extra=money(sum((max(Decimal('0'),nightly_rate(new.room_type,remaining.check_in+timedelta(days=i)).amount-
                        nightly_rate(old.room_type,remaining.check_in+timedelta(days=i)).amount) for i in range(remaining.nights)),Decimal('0')))
                if extra: f.adjustment('Upgrade voluntario',extra)
            old.mark_dirty(now);new.occupy()
            r.room_number=new.number;r.room_type=new.room_type;f.room_number=new.number
            u.save_room(old);u.save_room(new);u.save_reservation(r);u.save_folio(f,r.id)
            u.audit('HabitacionCambiada',r.id,{'from':old.number,'to':new.number,'reason':reason,'extra_mxn':str(extra)},now)
        return {'reservation_id':r.id,'old_room':old.number,'new_room':new.number,'charge_mxn':str(extra)}

    def early_departure(self,reservation_id,notice_at,departure_at):
        if departure_at<=notice_at: raise ValueError('Salida debe ser posterior al aviso')
        with self.repo.uow() as u:
            r=u.reservation(reservation_id)
            if r.status!=ReservationStatus.CHECKED_IN: raise ValueError('Se requiere estancia activa')
            if u.has_event('SalidaAnticipada',r.id): raise ValueError('Salida anticipada ya registrada')
            if not (r.dates.check_in < departure_at.date() < r.dates.check_out):
                raise ValueError('La salida debe ser anticipada y posterior a la fecha de ingreso')
            f=u.folio_for_reservation(r.id)
            nights_used=(departure_at.date()-r.dates.check_in).days
            used=stay_total(r.room_type,DateRange(r.dates.check_in,departure_at.date())).amount
            daily=nightly_rate(r.room_type,departure_at.date()).amount
            enough_notice=(departure_at-notice_at)>=timedelta(hours=24)
            penalty=money(daily*(Decimal('0.50') if enough_notice else Decimal('1')))
            revised=money(used+penalty)
            # BR-13: con aviso el mismo día, no reembolsar alojamiento ya pagado.
            if not enough_notice:
                revised=max(revised,min(r.total.amount, f.paid))
            adjustment=money(revised-r.total.amount)
            f.adjustment('Ajuste salida anticipada',adjustment)
            r.dates=DateRange(r.dates.check_in,departure_at.date());r.total=Money(revised)
            u.save_reservation(r);u.save_folio(f,r.id)
            u.audit('SalidaAnticipada',r.id,{'penalty_mxn':str(penalty),'revised_lodging_mxn':str(revised)},departure_at)
        return {'reservation_id':r.id,'penalty_mxn':str(penalty),'adjustment_mxn':str(adjustment),'folio_id':f.id,'new_checkout_date':str(departure_at.date())}

    @staticmethod
    def verify_admin_pin(pin):
        configured=os.getenv('ADMIN_PIN_HASH','')
        if not configured: raise ValueError('Configure ADMIN_PIN_HASH para autorizar operaciones especiales')
        try:
            iterations,salt,digest=configured.split('$')
            expected=bytes.fromhex(digest)
            actual=hashlib.pbkdf2_hmac('sha256',pin.encode(),bytes.fromhex(salt),int(iterations))
        except (ValueError,TypeError):
            raise ValueError('Formato ADMIN_PIN_HASH inválido')
        if not hmac.compare_digest(actual,expected): raise ValueError('PIN de Administración inválido')

    def authorize_adjustment(self,folio_id,action,value,admin_pin=None,now=None):
        if action not in ('descuento','condonación','anulación'):
            raise ValueError('Operación inválida')
        with self.repo.uow() as u:
            f=u.folio(folio_id)
            if f.closed: raise ValueError('Folio cerrado')
            amount=Decimal('0')
            if action=='descuento':
                percent=Decimal(str(value))
                if not (0<percent<=100): raise ValueError('Porcentaje fuera de rango')
                if percent>10: self.verify_admin_pin(admin_pin or '')
                amount=money(f.total*percent/100)
            else:
                self.verify_admin_pin(admin_pin or '')
                amount=money(value)
                if amount<=0: raise ValueError('Monto requerido')
                if amount>f.total: raise ValueError('Monto excede cargos')
            f.adjustment(f'{action} autorizado',-amount)
            u.save_folio(f,self._reservation_id_of_folio(u,f.id))
            u.audit('AjusteAutorizado',f.id,{'type':action,'amount_mxn':str(amount)},now)
        return self.folio(folio_id)

    def folio(self,folio_id):
        for f in self.repo.folios():
            if f.id==folio_id: return serialize_folio(f)
        raise ValueError('Folio no encontrado')

    def daily_reports(self,day):
        day=date.fromisoformat(str(day))
        reservations=self.repo.reservations();rooms=self.repo.rooms();folios=self.repo.folios();events=self.repo.events()
        cash={'efectivo':Decimal('0'),'terminal':Decimal('0'),'transferencia':Decimal('0')}
        for f in folios:
            for payment in f.payments:
                at=payment.get('at')
                if at and date.fromisoformat(at[:10])==day and payment['method'] in cash:
                    cash[payment['method']]+=Decimal(payment['amount'])
        daily_events=[e for e in events if e['at'][:10]==str(day)]
        return {'date':str(day),'cash_mxn':{k:str(money(v)) for k,v in cash.items()},
                'cash_total_mxn':str(money(sum(cash.values()))),
                'open_folios':[{'id':f.id,'room_number':f.room_number,'balance_mxn':str(f.balance)} for f in folios if not f.closed],
                'occupancy':{'entries':sum(e['type']=='CheckInCompletado' for e in daily_events),
                            'exits':sum(e['type']=='CheckOutCompletado' for e in daily_events),
                            'out_of_service':sum(r.status==RoomStatus.FUERA_SERVICIO for r in rooms),
                            'active_reservations':sum(r.status==ReservationStatus.CHECKED_IN for r in reservations)},
                'generated_on_demand':True}

def serialize_folio(f):
    return {'id':f.id,'room_number':f.room_number,'guest_name':f.guest_name,'charges':f.charges,
            'payments':f.payments,'total_mxn':str(f.total),'paid_mxn':str(f.paid),
            'balance_mxn':str(f.balance),'inspected':f.inspected,'closed':f.closed,
            'inspection_requested_at':str(f.inspection_requested_at) if f.inspection_requested_at else None,
            'inspection_completed_at':str(f.inspection_completed_at) if f.inspection_completed_at else None,
            'incidental_guarantee_mxn':str(f.incidental_guarantee.amount) if f.incidental_guarantee else None,
            'incidental_release':'simulada' if f.closed else 'pendiente'}
