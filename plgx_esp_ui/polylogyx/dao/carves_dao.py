from polylogyx.models import db, CarveSession

def get_carves_by_node_id(node_id):
    return db.session.query(CarveSession).filter(CarveSession.node_id == node_id).all()

def get_carves_all():
    return db.session.query(CarveSession).all()

def get_carves_by_session_id(session_id):
    return CarveSession.query.filter(CarveSession.session_id == session_id).first()