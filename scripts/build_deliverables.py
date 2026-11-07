"""Crea reporte y presentación base para defensa. Evidencias reales se deben agregar manualmente.
Requisitos opcionales: pip install -r requirements-docs.txt
"""
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.units import cm
from pypdf import PdfReader, PdfWriter
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/'Reporte_Final_PIA_Hotel_Costa_Azul.pdf'
SLIDES=ROOT/'Presentacion_Defensa_PIA_Hotel_Costa_Azul.pptx'
SOURCE=ROOT/'docs/references/BPMN_U2_original.pdf'
FONT_DIR=Path('/usr/share/fonts/truetype/dejavu')
if FONT_DIR.exists():
    pdfmetrics.registerFont(TTFont('DV',str(FONT_DIR/'DejaVuSans.ttf')))
    pdfmetrics.registerFont(TTFont('DV-Bold',str(FONT_DIR/'DejaVuSans-Bold.ttf')))
    normal,bold='DV','DV-Bold'
else: normal,bold='Helvetica','Helvetica-Bold'
NAVY=colors.HexColor('#112B44'); BLUE=colors.HexColor('#1F678A'); TEAL=colors.HexColor('#168B81')
LIGHT=colors.HexColor('#EFF6F8'); INK=colors.HexColor('#182B3A'); GRAY=colors.HexColor('#637789')
WHITE=colors.white
S={
 'title':ParagraphStyle('title',fontName=bold,fontSize=25,leading=32,textColor=NAVY,spaceAfter=10),
 'subtitle':ParagraphStyle('subtitle',fontName=normal,fontSize=12,leading=18,textColor=BLUE,spaceAfter=12),
 'h1':ParagraphStyle('h1',fontName=bold,fontSize=16,leading=20,textColor=NAVY,spaceBefore=9,spaceAfter=12,keepWithNext=True),
 'h2':ParagraphStyle('h2',fontName=bold,fontSize=11,leading=15,textColor=BLUE,spaceBefore=12,spaceAfter=6,keepWithNext=True),
 'body':ParagraphStyle('body',fontName=normal,fontSize=9,leading=14.5,textColor=INK,spaceAfter=8),
 'small':ParagraphStyle('small',fontName=normal,fontSize=7.7,leading=11,textColor=INK,spaceAfter=5),
 'table':ParagraphStyle('table',fontName=normal,fontSize=7.4,leading=10.5,textColor=INK),
 'thead':ParagraphStyle('thead',fontName=bold,fontSize=8,leading=11,textColor=WHITE),
 'note':ParagraphStyle('note',fontName=normal,fontSize=8,leading=12,textColor=GRAY,spaceAfter=7),
}
def P(s,style='body'):
    return Paragraph(str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;'),S[style])

def tab(rows,widths,header=True):
    data=[[P(x,'thead' if i==0 and header else 'table') for x in row] for i,row in enumerate(rows)]
    t=Table(data,colWidths=widths,repeatRows=1 if header else 0,hAlign='LEFT')
    specs=[('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,-1),(-1,-1),.4,colors.HexColor('#D5E3EA'))]
    if header: specs.extend([('BACKGROUND',(0,0),(-1,0),NAVY),('ROWBACKGROUNDS',(0,1),(-1,-1),[WHITE,LIGHT])])
    t.setStyle(TableStyle(specs));return t

def footer(canvas,doc):
    canvas.saveState();w,h=doc.pagesize
    canvas.setStrokeColor(colors.HexColor('#CBDCE5'));canvas.line(2*cm,1.4*cm,w-2*cm,1.4*cm)
    canvas.setFont(normal,7.5);canvas.setFillColor(GRAY)
    canvas.drawString(2*cm,1.05*cm,'Hotel Costa Azul | PIA | Equipo 9 | Revisión técnica')
    canvas.drawRightString(w-2*cm,1.05*cm,str(doc.page));canvas.restoreState()

story=[]
def add(t,sty='body'):story.append(P(t,sty))
def head(t):add(t,'h1')
def sub(t):add(t,'h2')
def page():story.append(PageBreak())

story.append(Spacer(1,2.5*cm))
add('HOTEL COSTA AZUL','title')
add('Producto Integrador de Aprendizaje | Componentes de Lógica de Negocios','subtitle')
add('Reporte de análisis, arquitectura, implementación y verificación','h1')
story.append(Spacer(1,.8*cm))
story.append(tab([
 ['Proyecto','Implementación de una solución de software basada en lógica de negocio'],
 ['Equipo','9 | Caso Hotel Costa Azul'],
 ['Fecha del documento','6 de noviembre de 2026'],
 ['Stack','Python 3.12 | FastAPI | SQLAlchemy | SQLite / PostgreSQL | pytest | Docker Compose'],
 ['Estado de validación','22 pruebas aprobadas, 1 prueba PostgreSQL omitida sin Docker; 93.41% de cobertura local'],
], [3.7*cm,12.7*cm],header=False))
story.append(Spacer(1,.6*cm))
add('Documento técnico basado en los productos U2/U3 entregados por el equipo. No sustituye la demostración en vivo ni certifica un despliegue público. Las capturas pendientes deben agregarse después de verificar el entorno del equipo.','note')
page()
head('1. Contexto y oportunidad de negocio')
add('Hotel Costa Azul tiene 120 habitaciones (60 Estándar, 40 Dobles, 20 Suites). El proceso principal abarca reservación, confirmación, check-in, estancia, consumos y check-out. Según el BRD de Unidad 2, la operación necesita inventario centralizado, sincronización con limpieza, trazabilidad de cargos y autorizaciones de Administración.')
sub('Objetivos del sistema')
story.append(tab([
 ['Objetivo','Regla de control'],
 ['Sin sobreventa','Cada reserva pendiente aparta habitación concreta por fechas; las escrituras son transaccionales.'],
 ['Tarifas y garantías','Precios base de 1,200 / 1,800 / 3,000 MXN, recargo del 35% en temporada alta, anticipo mínimo del 50% o tarjeta en garantía.'],
 ['Operación hotelera','Registro de identificación por tipo, acompañantes, garantía incidental, consumos, inspección y limpieza.'],
 ['Control y reportes','Estados permitidos, PIN para operaciones especiales, bloqueo de mantenimiento y reportes operativos.'],
], [4.3*cm,12.1*cm]))
sub('Artefactos de origen preservados')
add('BRD_U2_original.pdf, BPMN_U2_original.pdf, User_Stories_U2_original.pdf, Glosario_U2_original.pdf y Arquitectura_U3_original.pdf están en docs/references/. La rúbrica original también se preserva. El alcance y las reglas del sistema no se sustituyen por supuestos externos.')
page()
head('2. Reglas de negocio y trazabilidad')
add('Los 20 requisitos BR y las 16 historias Gherkin provienen del caso Hotel Costa Azul. La matriz completa BR → US → código → test se encuentra en docs/TRACEABILITY.md. Resumen:')
story.append(tab([
 ['Grupo','IDs','Implementación'],
 ['Inventario y precio','BR-01 a BR-04','Room, Money, DateRange, tarifa diaria y configuraciones de Semana Santa.'],
 ['Reservas','BR-05 a BR-07, BR-19','Reserva con garantía, cancelación con penalización, no-show, asignación transaccional sin overbooking.'],
 ['Estancia','BR-08 a BR-13','Check-in, early/late, acompañantes, garantía incidental, cambio y salida anticipada.'],
 ['Folio y habitaciones','BR-14 a BR-17','Consumos firmados, inspección 5 min, limpieza mínimo 35 min, mantenimiento.'],
 ['Control y reportes','BR-18 y BR-20','PIN con hash para operaciones sensibles y reporte diario consultable.'],
], [3.7*cm,3.2*cm,9.5*cm]))
sub('Escenarios observables para la defensa')
add('Caso positivo: consultar fechas → reservar → confirmar con anticipo → check-in → consumir servicios → inspeccionar → liquidar → check-out → limpiar. Casos negativos: reserva 61 del mismo tipo/fechas, confirmación repetida, falta de firma, inspección antes de 5 min, cierre con saldo y mantenimiento sin rol.')
page()
head('3. Arquitectura DDD y componentes')
add('Se utiliza un monolito modular y Domain Model, coherente con la actividad de Unidad 3. La API maneja transporte HTTP; HotelService coordina casos de uso; las entidades protegen invariantes; UnitOfWork persiste cambios y eventos en una única transacción.')
story.append(tab([
 ['Capa','Responsabilidades verificables'],
 ['Domain','Reservation, Room, Folio, Money, DateRange; cálculo de tarifa, cancelación y estados.'],
 ['Specification','Tipo de habitación, capacidad, estado y solapamiento de reservas pendientes/confirmadas/ocupadas.'],
 ['State Machine','Pendiente → Confirmada → Checked-in → Completada; habitación Limpia → Ocupada → Sucia → Limpia.'],
 ['Application','HotelService; creación, confirmación, check-in, salida, cambio, pagos simulados, mantenimiento y reportes.'],
 ['Infrastructure','Repository + UnitOfWork + SQLAlchemy, SQLite local / PostgreSQL en Compose; audit_events.'],
 ['API','FastAPI REST, Pydantic, Swagger UI y exportación de OpenAPI desde el código.'],
], [4.2*cm,12.2*cm]))
sub('Decisiones de arquitectura registradas')
add('ADR-001 Domain Model, ADR-002 SQLite local y PostgreSQL con bloqueo, ADR-003 CQRS ligero, ADR-004 asignación desde Pendiente, ADR-005 PIN y tokens de demostración. La separación respalda los principios SOLID, especialmente responsabilidad única e inversión de dependencias en aplicación.')
page()
head('4. Correcciones al problema crítico')
add('En la versión entregada originalmente, una reserva se guardaba sin room_number y el control de solapamiento no impedía crear múltiples reservas para el mismo inventario. La versión corregida selecciona y asigna habitación dentro de una transacción y mantiene las reservas Pendientes, Confirmadas y Checked-in como intervalos bloqueantes.')
story.append(tab([
 ['Situación','Antes (ZIP del amigo)','Ahora (versión corregida)'],
 ['Disponibilidad','No bloqueaba habitaciones por reserva creada','Filtra solapamiento y considera Pendiente como hold'],
 ['Concurrencia','ID mediante MAX+1, escrituras separadas','IDs generados por BD, BEGIN IMMEDIATE / advisory locks'],
 ['Confirmación','Podía confirmarse repetidamente','State Machine rechaza transiciones repetidas'],
 ['Ciclo de estancia','Dominio aislado sin API integral','Endpoints para check-in/folios/check-out/limpieza'],
 ['Base Docker','Servicio Alpine sin motor de DB','PostgreSQL 16 + App + Tests separados'],
], [3.0*cm,6.0*cm,7.4*cm]))
sub('Limitación operativa declarada')
add('El caso no define el tiempo máximo de una reserva Pendiente. La reserva permanece bloqueada hasta que el negocio determine caducidad, para no crear sobreventa silenciosamente. Es una decisión pendiente de validación; no se fabricó una duración.')
page()
head('5. Calidad y pruebas automatizadas')
add('El resultado local obtenido en el entorno de revisión, con variables de prueba y SQLite temporal, es el siguiente:')
story.append(tab([
 ['Indicador','Resultado'],
 ['Suite local','22 pruebas aprobadas; 1 omitida porque PostgreSQL está disponible solo al ejecutar Compose.'],
 ['Cobertura','93.41% del código src, calculado con pytest-cov.'],
 ['Umbral rubricado','≥80%: superado en la ejecución local.'],
 ['Casos de valor','Sobreventa, concurrencia, garantías, estados, horarios, cambios, limpieza, folios, roles, PIN, API/OpenAPI.'],
 ['Aún por validar','PostgreSQL real, Docker Compose y CI/CD activo en GitHub (no se ejecutaron en este entorno).'],
], [5.3*cm,11.1*cm]))
sub('Comandos reproducibles')
add('python -m pytest -q --cov=src --cov-report=term-missing --cov-fail-under=80')
add('docker compose up -d --build db app  |  docker compose --profile test run --rm tests')
add('Al presentar evidencias no se debe confundir cobertura del código con porcentaje de requisitos implementados. La suite verifica escenarios concretos, mientras la matriz de trazabilidad relaciona el alcance del negocio.')
page()
head('6. Calidad operacional y despliegue')
story.append(tab([
 ['Componente','Artefacto','Validación para entrega'],
 ['API documentada','src/api/main.py, docs/api/openapi.yaml','Probar /docs, /openapi.json y /health local y públicamente.'],
 ['Base y servicios','Dockerfile, docker-compose.yml','Confirmar PostgreSQL healthy + app running + tests correctos.'],
 ['Configuración',' .env.example','Copiar a .env, reemplazar tokens/PIN y no subir secretos.'],
 ['Automatización',' .github/workflows/ci.yml','Subir a GitHub y verificar jobs tests/docker en verde.'],
 ['Entrega online','render.yaml, docs/DESPLIEGUE.md','Desplegar con cuenta propia y adjuntar URL verificada.'],
 ['Defensa','Presentacion_Defensa_PIA_Hotel_Costa_Azul.pptx','Capturas, demostración de flujos y respuestas técnicas.'],
], [3.0*cm,6.0*cm,7.4*cm]))
sub('Evidencias visuales por incorporar')
add('1. Captura de terminal con pytest/coverage. 2. Swagger y caso de sobreventa rechazado. 3. Folio e inspección. 4. Docker Compose con PostgreSQL healthy. 5. GitHub Actions verde. 6. Swagger desde URL del despliegue. Las capturas deben ser auténticas; no se incluyen falsas pantallas de éxito.')
page()
head('7. Riesgos, decisiones pendientes y conclusiones')
add('La aplicación representa reglas documentadas en el BRD. Donde el caso no proporciona un dato operativo o una integración, se marca la ausencia explícitamente:')
story.append(tab([
 ['Pendiente','Acción del equipo'],
 ['Semana Santa / enero-febrero','Confirmar fechas de Semana Santa en el año de la demo y la política de enero-febrero antes de aplicar tarifas definitivas.'],
 ['Reserva sin garantía','Confirmar período de expiración de Pendiente.'],
 ['Pagos reales','El código registra operaciones simuladas; solicitar proveedor y procedimiento si el alcance exige cobranza real.'],
 ['Corte histórico','Reportes consultables a medianoche, pero snapshots inmutables y tratamiento contable del anticipo requieren definición.'],
 ['Seguridad y privacidad','Tokens de rol y PIN son suficientes para una simulación controlada, no para un sistema público con datos personales.'],
 ['GitHub, Docker, Render','Faltan evidencia externa, publicación y URL verificada.'],
], [5.0*cm,11.4*cm]))
sub('Conclusión')
add('Se preservó la continuidad del caso Hotel Costa Azul y se corrigió el fallo que permitía sobreventa; el servicio integra dominios, Specifications, State Machines, API REST, persistencia transaccional y pruebas. El avance técnico es verificable mediante una suite local superior al 80% de cobertura, pero la entrega final debe completarse con validación de Docker/PostgreSQL, repositorio y pipeline activos, despliegue, política de negocio faltante y capturas reales.')
add('Fuentes: BRD, User Stories y Gherkin, Glosario, BPMN de Unidad 2; arquitectura de Unidad 3 y rúbrica del PIA. Se anexan páginas visuales del BPMN original sin alterar su contenido.','note')

raw=ROOT/'docs/_reporte_base_temporal.pdf'
doc=SimpleDocTemplate(str(raw),pagesize=(21*cm,29.7*cm),rightMargin=2*cm,leftMargin=2*cm,topMargin=1.7*cm,bottomMargin=1.9*cm,title='Reporte Final PIA - Hotel Costa Azul',author='Equipo 9')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
writer=PdfWriter()
for pg in PdfReader(str(raw)).pages: writer.add_page(pg)
if SOURCE.exists():
    src=PdfReader(str(SOURCE))
    # Página 3-6: recortes grandes del BPMN, mejor legibilidad que imagen de la página 2.
    for idx in (2,3,4,5):
        if idx<len(src.pages): writer.add_page(src.pages[idx])
with DOC.open('wb') as f: writer.write(f)
raw.unlink(missing_ok=True)

# ----- POWERPOINT ------
prs=Presentation();prs.slide_width=Inches(13.33);prs.slide_height=Inches(7.5)
BG=(12,34,55); PRIMARY=(28,112,137); GREEN=(15,150,131); WHITE3=(242,247,250); LIGHT3=(171,196,207)
def rgb(v): return RGBColor(*v)
def rect(slide,x,y,w,h,color, radius=False):
    shp=slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
    shp.fill.solid();shp.fill.fore_color.rgb=rgb(color);shp.line.fill.background();return shp

def textbox(slide,x,y,w,h,t,size=22,bold=False,color=WHITE3):
    sh=slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
    tf=sh.text_frame;tf.word_wrap=True
    for i,line in enumerate(t.split('\n')):
        par=tf.paragraphs[0] if i==0 else tf.add_paragraph()
        par.text=line;par.font.name='Aptos';par.font.size=Pt(size);par.font.bold=bold;par.font.color.rgb=rgb(color)
        par.space_after=Pt(12)
    return sh

def slide(title,kicker='HOTEL COSTA AZUL  ·  PIA'):
    s=prs.slides.add_slide(prs.slide_layouts[6]);rect(s,0,0,13.33,7.5,BG)
    rect(s,.6,.52,.08,.53,GREEN)
    textbox(s,.82,.40,11.8,.4,kicker,size=12,bold=True,color=LIGHT3)
    textbox(s,.82,1.07,11.8,.85,title,size=32,bold=True)
    rect(s,.82,6.86,11.68,.015,PRIMARY)
    textbox(s,.82,6.97,11,.25,f'Equipo 9  •  06 NOV 2026  •  {len(prs.slides):02}',size=10,color=LIGHT3)
    return s

def bullet_slide(title,lines):
    s=slide(title);y=2.1
    for l in lines:
        rect(s,.9,y+.11,.11,.11,GREEN)
        textbox(s,1.23,y,11.2,.72,l,size=20)
        y+=.9
    return s

s=slide('De las reglas del negocio al software','UNIVERSIDAD AUTÓNOMA DE NUEVO LEÓN  ·  FIME')
textbox(s,.93,2.35,11.7,1.1,'Producto Integrador de Aprendizaje',size=27,bold=True)
textbox(s,.93,3.75,11.2,.8,'Análisis  •  DDD  •  Specification  •  State Machine  •  API REST',size=18,color=LIGHT3)
rect(s,.93,5.35,5.1,.8,PRIMARY,True);textbox(s,1.2,5.51,4.5,.4,'Hotel Costa Azul - Equipo 9',size=17,bold=True)
bullet_slide('Problema y oportunidad del hotel',[
 '120 habitaciones; tarifas por tipo y temporada.',
 'Riesgo de sobreventa y errores de disponibilidad.',
 'Cargos dispersos, limpieza y mantenimiento sin coordinación.',
 'Meta: reglas verificables y trazabilidad hasta pruebas.'
])
s=slide('Inventario y tarifas del BRD')
for i,(title1,detail1) in enumerate([('Estándar','60 habitaciones\n2 adultos\n$1,200/noche'),('Doble','40 habitaciones\n4 personas\n$1,800/noche'),('Suite','20 habitaciones\n4 personas\n$3,000/noche')]):
    x=.86+i*4.15;rect(s,x,2.2,3.75,3.65,(20,65,88),True)
    textbox(s,x+.25,2.53,3.3,.5,title1,size=24,bold=True)
    textbox(s,x+.25,3.4,3.4,2.3,detail1,size=21)
textbox(s,.92,6.08,11.5,.5,'Temporada alta: +35%  |  Reserva: anticipo 50% o tarjeta',size=17,color=LIGHT3)
bullet_slide('Arquitectura modular y DDD',[
 'Dominio: Habitación, Reserva, Folio, Money, DateRange.',
 'Aplicación: HotelService organiza casos de uso.',
 'Infraestructura: Repository + UnitOfWork + SQLAlchemy.',
 'API: FastAPI REST + OpenAPI + Swagger UI.'
])
bullet_slide('Specification: disponibilidad real',[
 'Tipo de habitación correcto.',
 'Capacidad suficiente y habitación habilitada.',
 'No solapar ninguna reserva Pendiente, Confirmada o Checked-in.',
 'Bloqueo y asignación atómica: sobreventa igual a cero.'
])
bullet_slide('State Machine: reglas de transición',[
 'Reserva: Pendiente → Confirmada → Checked-in → Completada.',
 'Desde Confirmada: Cancelada o No-Show según reglas.',
 'Habitación: Limpia → Ocupada → Sucia → Limpia.',
 'Fuera de Servicio exige reactivación y nueva limpieza.'
])
bullet_slide('Proceso principal implementado',[
 'Consulta → Reserva con habitación → Garantía → Confirmación.',
 'Check-in: tipo de documento, acompañantes, garantía incidental.',
 'Estancia: consumos firmados, pagos, cambios de habitación.',
 'Inspección 5 min → check-out → limpieza mínimo 35 min.'
])
bullet_slide('Casos de excepción y políticas',[
 'Cancelación: regla de 48 horas; no-show a las 23:59.',
 'Early check-in 30%; late check-out 30% o noche.',
 'Avería: cambio sin costo; upgrade: diferencia prorrateada.',
 'PIN con hash para descuentos >10%, condonaciones y anulaciones.'
])
s=slide('Calidad: resultado local verificable')
rect(s,.9,2.1,5.4,3.5,(20,65,88),True);rect(s,6.55,2.1,5.8,3.5,(20,65,88),True)
textbox(s,1.25,2.55,4.6,1,'22 de 22',size=37,bold=True)
textbox(s,1.25,3.65,4.7,.8,'pruebas ejecutadas OK\n1 test PostgreSQL omitido local',size=16,color=LIGHT3)
textbox(s,6.95,2.55,4.6,1,'93.41%',size=37,bold=True)
textbox(s,6.95,3.65,4.8,.7,'cobertura src\nmínimo exigido: 80%',size=16,color=LIGHT3)
textbox(s,.94,6.08,11.6,.3,'Evidencia externa de Docker y GitHub Actions aún pendiente',size=15,color=LIGHT3)
bullet_slide('Docker, CI/CD y publicación',[
 'Docker Compose: PostgreSQL + aplicación + tests (configurado).',
 'GitHub Actions: pytest, cobertura, OpenAPI, build y smoke test.',
 'Blueprint de Render incluido como guía de despliegue.',
 'Falta ejecutar Docker, activar CI y publicar URL real.'
])
bullet_slide('Pendientes para entrega y defensa',[
 'Verificar rango anual de Semana Santa y caducidad de Pendiente.',
 'Tomar capturas reales: Swagger, pytest, Docker, GitHub, hosting.',
 'Subir commits del equipo; comprobar pipeline verde.',
 'Agregar enlace público y concluir reporte con evidencias.'
])
bullet_slide('Conclusión',[
 'Reglas del Hotel Costa Azul conectadas a código y pruebas.',
 'Corregida la sobreventa mediante asignación transaccional.',
 'API, modelos y pruebas listos para validación en el equipo.',
 'La defensa exige demostrar funcionamiento, decisiones y límites.'
])
prs.save(str(SLIDES))
print('Report:',DOC,'pages',len(PdfReader(str(DOC)).pages))
print('Slides:',SLIDES,'count',len(prs.slides))
