from app import app, db, Laboratorio, User
from werkzeug.security import generate_password_hash

def populate():
    with app.app_context():
        # Limpar laboratórios existentes para evitar duplicatas
        db.session.query(Laboratorio).delete()
        
        # Categorias e Laboratórios conforme solicitado
        data = {
            'Informática': ['Laboratório Grande', 'Laboratório Pequeno'],
            'Elétrica': ['Predial', 'Industrial', 'PLC', 'Ensaios Elétricos', 'Eletrônica', 'SEP - Externo', 'Renováveis'],
            'Mecânica': ['Manutenção', 'Hidráulica', 'Pneumática', 'Ferramentaria', 'Tornearia', 'Caldeiraria', 'Solda', 'Metrologia', 'Metalografia'],
            'Outros': ['Auditório', 'Sala Maker']
        }
        
        for cat, names in data.items():
            for name in names:
                db.session.add(Laboratorio(nome=name, categoria=cat, capacidade=25))
        
        # Usuários (Apenas Administrador, já que professores não têm mais login)
        if not User.query.filter_by(email='admin@senai.br').first():
            db.session.add(User(
                nome='Supervisor SENAI', 
                email='admin@senai.br', 
                senha=generate_password_hash('admin123'), 
                tipo='supervisor'
            ))
            
        db.session.commit()
        print("Banco de dados atualizado com sucesso!")

if __name__ == "__main__":
    populate()
