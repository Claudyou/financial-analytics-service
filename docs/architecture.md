# Arhitectură: monolith modular

## Fluxul curent

```text
Client
  -> API / router
      -> service
          -> repository
              -> database
```

## Limite și responsabilități

| Modul | Responsabilitate |
| --- | --- |
| API / router | Primește requesturile HTTP, validează forma datelor și produce răspunsuri HTTP. |
| Service | Aplică regulile de business și coordonează operațiile, fără dependență directă de FastAPI. |
| Repository | Citește și scrie datele și ascunde detaliile SQLite, SQLAlchemy sau PostgreSQL. |
| Model / schema | Definește datele validate pentru API și, ulterior, modelele persistate. |

## Aplicare în Financial Analytics Service

| Modul | Exemplu planificat |
| --- | --- |
| API | `POST /imports` primește un fișier CSV. |
| Service | Validează și normalizează datele, apoi decide dacă o tranzacție este duplicată. |
| Repository | Caută și salvează tranzacții. |
| Worker | Va procesa importurile mari după MVP. |

## De ce monolith modular, nu microservicii?

Proiectul începe ca monolith modular deoarece produsul este la început, iar funcționalitățile au nevoie de dezvoltare rapidă și tranzacții simple între module. Separarea API–service–repository menține limite clare și permite extragerea ulterioară a unui worker de import dacă încărcarea sau nevoile de scalare o justifică. Microserviciile introduse prea devreme ar adăuga deployment, observability și comunicare distribuită fără beneficii proporționale.