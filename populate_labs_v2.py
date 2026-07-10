from app import app, db, Laboratorio, User
from werkzeug.security import generate_password_hash


def populate():

    with app.app_context():

        print("Inicializando banco...")

        db.create_all()


        # ============================
        # LIMPAR DADOS EXISTENTES
        # ============================

        db.session.query(Laboratorio).delete()

        db.session.commit()



        # ============================
        # CADASTRO DOS LABORATÓRIOS
        # ============================


        laboratorios = {


            "Informática": [

                "Laboratório Grande",
                "Laboratório Pequeno"

            ],


            "Elétrica": [

                "Predial",
                "Industrial",
                "PLC",
                "Ensaios Elétricos",
                "Eletrônica",
                "SEP - Externo",
                "Renováveis"

            ],


            "Mecânica": [

                "Manutenção",
                "Hidráulica",
                "Pneumática",
                "Ferramentaria",
                "Tornearia",
                "Caldeiraria",
                "Solda",
                "Metrologia",
                "Metalografia"

            ],


            "Outros": [

                "Auditório",
                "Sala Maker"

            ]

        }



        for categoria, nomes in laboratorios.items():


            for nome in nomes:


                laboratorio = Laboratorio(

                    nome=nome,

                    categoria=categoria,

                    capacidade=25

                )


                db.session.add(
                    laboratorio
                )



        # ============================
        # CRIAR ADMINISTRADOR
        # ============================


        admin = User.query.filter_by(
            email="admin@senai.br"
        ).first()



        if not admin:


            admin = User(

                nome="Supervisor SENAI",

                email="admin@senai.br",

                senha=generate_password_hash(
                    "admin123"
                ),

                tipo="supervisor"

            )


            db.session.add(
                admin
            )



        db.session.commit()



        print(
            "Banco populado com sucesso!"
        )

        print(
            "Usuário administrador:"
        )

        print(
            "Email: admin@senai.br"
        )

        print(
            "Senha: admin123"
        )



if __name__ == "__main__":

    populate()
