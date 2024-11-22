# tars

Application to manage IOTINGA registry, and much more

## Upgrade



## Prerequisiti

- Python 3.12.3
- Django 5.0.4
- psql (PostgreSQL) 16.4 (Ubuntu 16.4-0ubuntu0.24.04.2)



## Installazione

```sh

# 1. Crea una chiave SSH (usa il tuo indirizzo email di github)
ssh-keygen -t ed25519 -C "your_email@example.com"

# 2. Visualizza la chiave pubblica e copia l'output (Incolla questa chiave nelle impostazioni SSH di GitHub per consentire il clonaggio.)  
cat ~/.ssh/id_ed25519.pub

# 3. Clona il repository da GitHub usando il protocollo SSH
git clone git@github.com:username/progetto.git

# 4. Crea un ambiente virtuale per isolare le dipendenze
python3 -m venv venv

# 5. Attiva l'ambiente virtuale
source venv/bin/activate

# 6. Entra nella cartella del progetto
cd progetto

# 7. Installa le dipendenze necessarie dal file requirements.txt
pip install -r requirements.txt

# 8. Accedi a PostgreSQL
sudo -u postgres psql

```

## Database and role setup

```sql

-- 1. Crea il database per il progetto
CREATE DATABASE nome_database;

-- 2. Crea un utente dedicato e imposta una password
CREATE USER nome_utente WITH PASSWORD 'password';

-- 3. Esci da PostgreSQL
\q
```

```sh

# 9. Esegui le migrazioni per configurare il database
./manage.py migrate

# 10. Crea un superuser per l'accesso amministrativo
./manage.py createsuperuser

# 11. Avvia il server
./manage.py runserver

```

## DOCUMENTATION

# In views.py are all the API that return a JSON value

# In settings.py have been set all the necessary installations

# In urls.py are the corrisponding urls for every API in views.py
