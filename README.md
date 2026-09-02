# Financial Analytics Service

**Financial Analytics Service** este un backend API pentru importul, clasificarea și analiza tranzacțiilor financiare personale. Aplicația transformă fișiere CSV în date structurate, elimină duplicatele, aplică reguli configurabile de categorisire și oferă rapoarte utile despre cheltuieli, venituri și bugete.

Proiectul este conceput ca un exemplu de backend Python de nivel Middle/Senior: combină API design, modelare de date, logică de business, procesare asincronă și practici de fiabilitate.

> Datele din proiect sunt exclusiv fictive. Repository-ul nu conține extrase bancare reale, parole, token-uri sau alte informații sensibile.

## Problema rezolvată

Analiza manuală a extraselor bancare este repetitivă și predispusă la erori. Serviciul permite importul controlat al tranzacțiilor, clasificarea lor consecventă și consultarea rapidă a rapoartelor financiare. Importurile sunt tratate ca operațiuni care pot fi lente sau repetate, astfel încât sistemul este proiectat pentru validare, deduplicare și urmărirea stării procesării.

## Ce demonstrează proiectul

- proiectarea unui REST API în FastAPI;
- modelare relațională pentru conturi, tranzacții, categorii, reguli și bugete;
- import CSV cu validare, deduplicare și urmărirea stării;
- procesare asincronă și mecanisme de retry pentru operațiuni lente;
- rapoarte SQL, indexare și cache pentru interogări agregate;
- testare automată, containerizare, CI și observability;
- decizii de arhitectură explicate prin trade-off-uri concrete.

## Funcționalități principale

- import de tranzacții din CSV;
- normalizare și validare a datelor importate;
- detectarea dublurilor pentru importuri repetate;
- categorisire automată prin reguli configurabile, cu priorități;
- rapoarte lunare și distribuția cheltuielilor pe categorii;
- urmărirea bugetelor și a limitelor configurate de utilizator;
- autentificare și izolare a datelor per utilizator;
- urmărirea progresului pentru importurile procesate în fundal.

## Arhitectură

Aplicația pornește ca un **monolith modular**: API-ul, logica de business și accesul la date sunt separate în module clare, fără complexitatea operațională prematură a microserviciilor. Importurile mari sunt mutate către worker-e asincrone pentru ca requesturile HTTP să rămână rapide.

```text
Client -> FastAPI API -> Service layer -> PostgreSQL
						 |
						 -> Redis -> Worker de import
```

Această arhitectură permite evoluția controlată către cache, worker-e multiple și observability, păstrând în același timp dezvoltarea locală simplă.

## Tehnologii

| Zonă | Tehnologie |
|---|---|
| API | Python + FastAPI |
| Validare | Pydantic |
| Persistență | PostgreSQL + SQLAlchemy |
| Migration-uri | Alembic |
| Cache / broker | Redis |
| Joburi de fundal | Celery, RQ sau Arq — decizia se ia la implementare |
| Testare | Pytest |
| Rulare locală | Docker + Docker Compose |
| CI | GitHub Actions |

MVP-ul este construit incremental cu SQLite și procesare sincronă, iar PostgreSQL, Redis și worker-ele sunt introduse pe măsură ce fluxul de import devine stabil și testat.

## Fluxul principal

1. Utilizatorul încarcă un CSV către API.
2. API-ul validează dimensiunea, tipul și structura fișierului.
3. Se creează un `ImportJob` cu statusul `pending`.
4. Un worker procesează fișierul în fundal.
5. Tranzacțiile sunt normalizate, validate și deduplicate.
6. Se aplică regulile de categorisire.
7. Datele sunt salvate, iar jobul devine `completed` sau `failed`.
8. Utilizatorul poate consulta starea importului și rapoartele rezultate.

## API overview

```text
POST   /auth/register
POST   /auth/login

POST   /accounts
GET    /accounts

POST   /imports
GET    /imports/{import_id}

GET    /transactions
POST   /transactions
PATCH  /transactions/{transaction_id}

GET    /categories
POST   /categorization-rules

GET    /reports/monthly?year=2026&month=8
GET    /reports/category-breakdown?from=2026-01-01&to=2026-08-31
GET    /budgets/status

GET    /health
```

API-ul va furniza documentație OpenAPI generată automat de FastAPI. Endpointurile sunt implementate gradual și pot fi ajustate odată cu evoluția modelului de date.

## Roadmap

- [ ] API FastAPI, health check, tranzacții și categorii;
- [ ] import CSV sincron, validare și teste;
- [ ] PostgreSQL, migration-uri, autentificare și rapoarte;
- [ ] reguli de categorisire, bugete și Docker Compose;
- [ ] import asincron prin Redis și worker-e;
- [ ] retry, idempotency, cache, rate limiting și observability;
- [ ] CI, date fictive de demonstrație și documentație de rulare.

## Stare curentă

Proiectul este în faza inițială de implementare. Elementele din secțiunile de funcționalități, arhitectură și API reprezintă direcția țintă și vor fi actualizate pe măsură ce componentele devin funcționale.

## Rulare locală

### Cerințe

- Python 3.13 sau mai nou;
- `pip`.

### Instalare

Din directorul proiectului, creează și activează un mediu virtual, apoi instalează proiectul cu dependențele de dezvoltare:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### Pornirea API-ului

```powershell
uvicorn app.main:app --reload
```

API-ul va fi disponibil la `http://127.0.0.1:8000`.

- health check: `GET http://127.0.0.1:8000/health` răspunde cu `{"status":"ok"}`;
- documentație OpenAPI interactivă: `http://127.0.0.1:8000/docs`;
- schemă OpenAPI: `http://127.0.0.1:8000/openapi.json`.

### Teste

```powershell
pytest
```