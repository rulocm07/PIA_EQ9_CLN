"""API REST académica del Hotel Costa Azul /docs y /openapi.json.
Las operaciones de pago y liberación de garantías son SIMULACIONES, no bancaria.
"""
import asyncio
import hmac
import os
from contextlib import asynccontextmanager
from datetime import date, datetime
from decimal import Decimal
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from src.infrastructure.repository import SQLiteRepository
from src.application.services import HotelService, serialize_folio
from src.domain.hotel import RoomType, nightly_rate, stay_total, DateRange

async def no_show_worker(service):
    while True:
        try:
            service.process_no_shows()
        except Exception:
            import logging
            logging.exception('Error en procesamiento automático de no-show')
        await asyncio.sleep(30)

@asynccontextmanager
async def lifespan(app):
    task=None
    if os.getenv('ENABLE_SCHEDULER','true').lower()=='true':
        task=asyncio.create_task(no_show_worker(app.state.service))
    yield
    if task:
        task.cancel()
        try: await task
        except asyncio.CancelledError: pass

app=FastAPI(title='Hotel Costa Azul API',version='2.0.0',
    description='PIA académico BR-01..BR-20. Pagos y cargos a tarjetas simulados; roles declarativos para la demo. No introducir documentos reales.',
    lifespan=lifespan)
app.state.repo=SQLiteRepository()
app.state.service=HotelService(app.state.repo)

def get_service(): return app.state.service

def fail(e): raise HTTPException(status_code=400,detail=str(e)) from e

class ReservationInput(BaseModel):
    guest_name: str=Field(min_length=2,max_length=160)
    check_in: date
    check_out: date
    room_type: RoomType
    guests: int=Field(ge=1,le=4)

class ConfirmInput(BaseModel):
    deposit: Decimal|None=Field(default=None,ge=0)
    card_guarantee: bool=False

class CancelInput(BaseModel):
    waive_penalty: bool=False
    admin_pin: str|None=None

class CheckInInput(BaseModel):
    document_type: str=Field(description='Solo INE o Pasaporte; NO enviar número ni imagen del documento')
    companions: list[str]=Field(default_factory=list)
    incidental_type: str=Field(description='voucher (1000 MXN) o efectivo (500 MXN); sin datos de tarjeta')

class ConsumptionInput(BaseModel):
    category: str
    description: str=Field(min_length=1)
    amount: Decimal=Field(gt=0)
    signature: str=Field(min_length=1,description='Evidencia de firma; demostración, NO una firma real')
    room_number: str

class PaymentInput(BaseModel):
    amount: Decimal=Field(gt=0)
    method: str

class MaintenanceInput(BaseModel):
    reason: str=Field(min_length=2)
    reactivation: date
    actor_role: str

class ActorInput(BaseModel):
    actor_role: str

class ChangeRoomInput(BaseModel):
    new_room_number: str
    reason: str=Field(description='avería o upgrade')

class EarlyDepartureInput(BaseModel):
    notice_at: datetime
    departure_at: datetime

class AdjustmentInput(BaseModel):
    action: str=Field(description='descuento, condonación, anulación')
    value: Decimal=Field(gt=0,description='Porcentaje para descuento, monto MXN para condonación y anulación')
    admin_pin: str|None=None

class JobInput(BaseModel):
    admin_pin: str

def ensure_maintenance_role(actor_role, token):
    key = {'Administración':'ROLE_TOKEN_ADMIN', 'Supervisor de Mantenimiento':'ROLE_TOKEN_MAINTENANCE'}.get(actor_role)
    if not key: raise ValueError('Rol no autorizado')
    expected=os.getenv(key,'')
    if not expected: raise ValueError(f'Configure {key} en el entorno')
    if not hmac.compare_digest(token or '',expected): raise ValueError('Token de rol inválido')

@app.get('/health',tags=['Sistema'])
def health(): return {'status':'ok','service':'hotel-costa-azul','version':'2.0.0'}

@app.get('/rooms',tags=['Habitaciones'])
def rooms(service:HotelService=Depends(get_service)):
    return [{'number':r.number,'type':r.room_type.value,'capacity':r.capacity,'status':r.status.value,
             'reason':r.out_of_service_reason,'reactivation_date':r.reactivation_date} for r in service.repo.rooms()]

@app.get('/availability',tags=['Reservaciones'])
def availability(check_in:date,check_out:date,room_type:RoomType,guests:int,service:HotelService=Depends(get_service)):
    try: return service.availability(str(check_in),str(check_out),room_type.value,guests)
    except ValueError as e: fail(e)

@app.get('/pricing/quote',tags=['Reservaciones'])
def quote(check_in:date,check_out:date,room_type:RoomType):
    try:
        dates=DateRange(check_in,check_out)
        return {'room_type':room_type.value,'nights':dates.nights,'total_mxn':str(stay_total(room_type,dates).amount)}
    except ValueError as e: fail(e)

@app.post('/reservations',status_code=201,tags=['Reservaciones'])
def create_reservation(p:ReservationInput,service:HotelService=Depends(get_service)):
    try:
        r=service.create_reservation({'guest_name':p.guest_name,'check_in':str(p.check_in),
            'check_out':str(p.check_out),'room_type':p.room_type.value,'guests':p.guests})
        return reservation_dict(r)
    except ValueError as e: fail(e)

@app.get('/reservations',tags=['Reservaciones'])
def reservations(service:HotelService=Depends(get_service)):
    return [reservation_dict(r) for r in service.repo.reservations()]

def reservation_dict(r):
    return {'id':r.id,'guest_name':r.guest_name,'check_in':r.dates.check_in,'check_out':r.dates.check_out,
       'room_type':r.room_type.value,'guests':r.guests,'room_number':r.room_number,
       'total_mxn':str(r.total.amount),'deposit_mxn':str(r.deposit.amount),
       'card_guarantee':r.card_guarantee,'status':r.status.value}

@app.post('/reservations/{reservation_id}/confirm',tags=['Reservaciones'])
def confirm(reservation_id:int,p:ConfirmInput,service:HotelService=Depends(get_service)):
    try: return reservation_dict(service.confirm(reservation_id,p.deposit,p.card_guarantee))
    except ValueError as e: fail(e)

@app.post('/reservations/{reservation_id}/cancel',tags=['Reservaciones'])
def cancel(reservation_id:int,p:CancelInput|None=None,service:HotelService=Depends(get_service)):
    try: return service.cancel(reservation_id,waive_penalty=p.waive_penalty if p else False,admin_pin=p.admin_pin if p else None)
    except ValueError as e: fail(e)

@app.post('/reservations/{reservation_id}/check-in',tags=['Estancia'])
def check_in(reservation_id:int,p:CheckInInput,service:HotelService=Depends(get_service)):
    try: return service.check_in(reservation_id,p.document_type,p.companions,p.incidental_type)
    except ValueError as e: fail(e)

@app.post('/reservations/{reservation_id}/change-room',tags=['Estancia'])
def change_room(reservation_id:int,p:ChangeRoomInput,service:HotelService=Depends(get_service)):
    try: return service.change_room(reservation_id,p.new_room_number,p.reason)
    except ValueError as e: fail(e)

@app.post('/reservations/{reservation_id}/early-departure',tags=['Estancia'])
def early_departure(reservation_id:int,p:EarlyDepartureInput,service:HotelService=Depends(get_service)):
    try: return service.early_departure(reservation_id,p.notice_at,p.departure_at)
    except ValueError as e: fail(e)

@app.get('/reservations/{reservation_id}/checkout-preview',tags=['Estancia'])
def checkout_preview(reservation_id:int,service:HotelService=Depends(get_service)):
    try: return service.preview_checkout(reservation_id)
    except ValueError as e: fail(e)

@app.post('/reservations/{reservation_id}/check-out',tags=['Estancia'])
def check_out(reservation_id:int,service:HotelService=Depends(get_service)):
    try: return service.check_out(reservation_id)
    except ValueError as e: fail(e)

@app.get('/folios',tags=['Folios'])
def folios(service:HotelService=Depends(get_service)):
    return [serialize_folio(f) for f in service.repo.folios()]

@app.get('/folios/{folio_id}',tags=['Folios'])
def folio(folio_id:int,service:HotelService=Depends(get_service)):
    try: return service.folio(folio_id)
    except ValueError as e: fail(e)

@app.post('/folios/{folio_id}/consumptions',tags=['Folios'])
def consumption(folio_id:int,p:ConsumptionInput,service:HotelService=Depends(get_service)):
    try: return service.add_consumption(folio_id,p.category,p.description,p.amount,p.signature,p.room_number)
    except ValueError as e: fail(e)

@app.post('/folios/{folio_id}/payments',tags=['Folios'])
def payment(folio_id:int,p:PaymentInput,service:HotelService=Depends(get_service)):
    try: return service.pay_folio(folio_id,p.amount,p.method)
    except ValueError as e: fail(e)

@app.post('/folios/{folio_id}/inspection/request',tags=['Folios'])
def inspection_request(folio_id:int,service:HotelService=Depends(get_service)):
    try: return service.request_inspection(folio_id)
    except ValueError as e: fail(e)

@app.post('/folios/{folio_id}/inspection/complete',tags=['Folios'])
def inspection_complete(folio_id:int,service:HotelService=Depends(get_service)):
    try: return service.complete_inspection(folio_id)
    except ValueError as e: fail(e)

@app.post('/rooms/{room_number}/clean',tags=['Habitaciones'])
def clean(room_number:str,service:HotelService=Depends(get_service)):
    try:
        r=service.clean_room(room_number)
        return {'number':r.number,'status':r.status.value}
    except ValueError as e: fail(e)

@app.post('/rooms/{room_number}/out-of-service',tags=['Habitaciones'])
def block(room_number:str,p:MaintenanceInput,x_role_token:str|None=Header(default=None),service:HotelService=Depends(get_service)):
    try:
        ensure_maintenance_role(p.actor_role,x_role_token)
        r=service.block_room(room_number,p.reason,p.reactivation,p.actor_role)
        return {'number':r.number,'status':r.status.value,'reason':r.out_of_service_reason,'reactivation_date':r.reactivation_date}
    except ValueError as e: fail(e)

@app.post('/rooms/{room_number}/reactivate',tags=['Habitaciones'])
def reactivate(room_number:str,p:ActorInput,x_role_token:str|None=Header(default=None),service:HotelService=Depends(get_service)):
    try:
        ensure_maintenance_role(p.actor_role,x_role_token)
        r=service.reactivate_room(room_number,p.actor_role)
        return {'number':r.number,'status':r.status.value}
    except ValueError as e: fail(e)

@app.post('/folios/{folio_id}/adjustments',tags=['Administración'])
def adjustments(folio_id:int,p:AdjustmentInput,service:HotelService=Depends(get_service)):
    try: return service.authorize_adjustment(folio_id,p.action,p.value,p.admin_pin)
    except ValueError as e: fail(e)

@app.get('/reports/daily',tags=['Reportes'])
def daily(day:date,service:HotelService=Depends(get_service)):
    try: return service.daily_reports(day)
    except ValueError as e: fail(e)

@app.post('/jobs/process-no-shows',tags=['Sistema'])
def run_no_shows(p:JobInput,service:HotelService=Depends(get_service)):
    try:
        service.verify_admin_pin(p.admin_pin)
        return {'processed':service.process_no_shows()}
    except ValueError as e: fail(e)
