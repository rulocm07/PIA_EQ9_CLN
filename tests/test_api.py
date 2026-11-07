def test_health_docs_and_rooms(client):
    assert client.get('/health').json()['status']=='ok'
    assert len(client.get('/rooms').json())==120
    assert client.get('/openapi.json').status_code==200
    assert client.get('/docs').status_code==200


def test_rest_reservation_lifecycle_and_invalid_input(client):
    p={'guest_name':'Ana López','check_in':'2026-11-06','check_out':'2026-11-08','room_type':'Estándar','guests':2}
    assert len(client.get('/availability',params={k:v for k,v in p.items() if k in ('check_in','check_out','room_type','guests')}).json())==60
    resp=client.post('/reservations',json=p)
    assert resp.status_code==201,resp.text
    r=resp.json();assert r['room_number']=='001'
    assert client.post(f"/reservations/{r['id']}/confirm",json={'deposit':500}).status_code==400
    assert client.post(f"/reservations/{r['id']}/confirm",json={'deposit':1200}).status_code==200
    assert client.post(f"/reservations/{r['id']}/confirm",json={'deposit':1200}).status_code==400
    assert len(client.get('/reservations').json())==1
    assert client.get('/pricing/quote',params={'check_in':'2026-07-01','check_out':'2026-07-02','room_type':'Estándar'}).json()['total_mxn']=='1620.00'
    assert client.get('/availability',params={'check_in':'2026-11-08','check_out':'2026-11-08','room_type':'Estándar','guests':2}).status_code==400


def test_error_api_roles_payments_and_reports(client,monkeypatch):
    monkeypatch.setenv('ROLE_TOKEN_ADMIN','admin-secret-test')
    assert client.post('/rooms/001/out-of-service',json={'reason':'fuga','reactivation':'2026-11-10','actor_role':'Recepción'}).status_code==400
    assert client.post('/rooms/001/out-of-service',json={'reason':'fuga','reactivation':'2026-11-10','actor_role':'Administración'},headers={'X-Role-Token':'admin-secret-test'}).status_code==200
    assert client.post('/rooms/001/reactivate',json={'actor_role':'Administración'},headers={'X-Role-Token':'admin-secret-test'}).status_code==200
    assert client.post('/rooms/001/clean').status_code==200
    assert 'cash_mxn' in client.get('/reports/daily',params={'day':'2026-11-06'}).json()
    assert client.get('/folios/99999').status_code==400
    assert client.post('/jobs/process-no-shows',json={'admin_pin':'1234'}).status_code==400
