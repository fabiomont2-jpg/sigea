# SIGEA - Sistema de Gerenciamento de Agendamentos

Sistema web desenvolvido em **Python/Flask** para gerenciamento de agendamentos de laboratórios e ambientes educacionais.

O projeto foi desenvolvido para substituir o uso de formulários eletrônicos por um sistema integrado, permitindo o controle de reservas, aprovação de solicitações e visualização dos agendamentos em calendário.

---

## Funcionalidades

- Login de supervisores
- Solicitação de agendamento de laboratórios
- Aprovação, rejeição e exclusão de solicitações
- Calendário interativo de reservas
- Organização dos laboratórios por categoria
- Controle de agendamentos por turno
- Banco de dados SQLite

---

## Tecnologias utilizadas

- Python 3
- Flask
- SQLAlchemy
- SQLite
- HTML5
- CSS3
- JavaScript
- Bootstrap

---

## Estrutura do projeto

```
SIGEA/
│
├── app.py
├── requirements.txt
├── static/
│   ├── css/
│   └── js/
├── templates/
├── populate_labs.py
└── README.md
```

---

## Instalação

Clone o repositório:

```bash
git clone https://github.com/SEU_USUARIO/SIGEA.git
```

Acesse a pasta:

```bash
cd SIGEA
```

Crie um ambiente virtual:

```bash
python -m venv venv
```

Ative o ambiente virtual.

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute a aplicação:

```bash
python app.py
```

---

## Usuário administrador

O administrador é responsável por:

- Aprovar solicitações
- Rejeitar solicitações
- Excluir agendamentos
- Visualizar o calendário geral

---

## Banco de dados

O sistema utiliza SQLite através do SQLAlchemy.

As tabelas são criadas automaticamente na primeira execução da aplicação.

---

## Futuras melhorias

- Login para professores
- Notificações por e-mail
- Exportação para PDF
- Dashboard com indicadores
- Integração com PostgreSQL
- Integração com Microsoft 365
- Controle de equipamentos
- Relatórios de utilização dos laboratórios

---

## Autor

**Fábio Pinto Monte**

Professor - SENAI

Mestrando em Engenharia de Controle e Automação - IFES

Especialização em Cidades Inteligentes - UFES

Licenciatura em Informática

---

## Licença

Projeto desenvolvido para fins acadêmicos e institucionais.
