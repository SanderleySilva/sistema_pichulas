🏆 Sistema de Gestão de Associações

Sistema web desenvolvido para gerenciamento de associações, permitindo controle de associados, eventos, mensalidades e relatórios financeiros.

O sistema foi projetado com arquitetura multi-tenant, garantindo isolamento de dados por associação.

🚀 Tecnologias Utilizadas

Python

Django

Django ORM

SQLite (ambiente de desenvolvimento)

ReportLab (geração de PDF)

Git

Deploy em PythonAnywhere

🧠 Arquitetura

O projeto segue arquitetura baseada em:

Separação de responsabilidades

Camada de Services para regras de negócio

Isolamento de dados por associação (multi-tenant)

Autenticação e autorização via Django

Estrutura principal:

core → Associação e Perfil

associados → Cadastro de associados

eventos → Gestão de eventos

financeiro → Controle de pagamentos

🔐 Funcionalidades

Cadastro de associações

Controle de usuários vinculados à associação

Criação e finalização de eventos

Geração automática de participantes por evento

Controle de pagamento por participante

Relatório em PDF do evento

Isolamento total de dados por associação

⚙️ Como rodar o projeto localmente

Clone o repositório:

git clone https://github.com/seuusuario/sistema_pichulas.git

Entre na pasta:

cd sistema_pichulas

Crie o ambiente virtual:

python -m venv .venv

Ative o ambiente:

Windows:

.venv\Scripts\activate

Linux/Mac:

source .venv/bin/activate

Instale as dependências:

pip install -r requirements.txt

Execute as migrações:

python manage.py migrate

Crie superusuário:

python manage.py createsuperuser

Rode o servidor:

python manage.py runserver
🌍 Deploy

O sistema está configurado para deploy na plataforma PythonAnywhere.

Passos principais:

Push para GitHub

Pull no servidor

Executar migrate

Executar collectstatic

Reload da aplicação

📈 Melhorias Futuras

Implementação de API REST

Integração com gateway de pagamento

Dashboard com gráficos financeiros

Controle de permissões por tipo de usuário

Deploy com PostgreSQL

Testes automatizados

👨‍💻 Autor

Desenvolvido por Sanderley José
Desenvolvedor Backend Python