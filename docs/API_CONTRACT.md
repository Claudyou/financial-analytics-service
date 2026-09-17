# API Contract — Financial Analytics Service

**Scop:** definesc comportamentul endpointurilor înainte de implementare: intrări, ieșiri, coduri HTTP și erori.

Un contract API este promisiunea publică a unui endpoint. El spune clientului ce trimite, ce primește și ce se întâmplă când datele sunt invalide, fără să expună implementarea internă.

---

## 1. Health check

### Request

```http
GET /health
```

### Răspuns reușit

**Status:** `200 OK`

```json
{
  "status": "ok"
}
```

### Decizie

Endpointul răspunde la întrebarea: „Rulează procesul API?”

Nu verifică încă baza de date sau Redis. Mai târziu pot adăuga un readiness check separat pentru dependențele externe.

---

## 2. Crearea unui import

### Scop

Utilizatorul încarcă un fișier CSV fictiv cu tranzacții.

### Request conceptual

```http
POST /imports
Content-Type: multipart/form-data

file: transactions.csv
```

### Răspuns reușit în MVP-ul sincron

**Status:** `201 Created`

```json
{
  "created": 42,
  "duplicates_skipped": 3,
  "invalid_rows": 1
}
```

### Erori posibile

Fișierul lipsește:

**Status:** `400 Bad Request`

```json
{
  "code": "file_missing",
  "message": "Fișierul CSV este obligatoriu."
}
```

Fișierul este gol:

**Status:** `400 Bad Request`

```json
{
  "code": "file_empty",
  "message": "Fișierul CSV este gol."
}
```

Tipul de conținut nu este acceptat:

**Status:** `415 Unsupported Media Type`

```json
{
  "code": "unsupported_media_type",
  "message": "Tipul de conținut al fișierului nu este acceptat."
}
```

Fișierul depășește dimensiunea maximă permisă:

**Status:** `413 Payload Too Large`

```json
{
  "code": "file_too_large",
  "message": "Fișierul CSV depășește dimensiunea maximă permisă."
}
```

CSV-ul nu conține coloanele obligatorii:

**Status:** `422 Unprocessable Entity`

```json
{
  "code": "invalid_csv_columns",
  "message": "Fișierul CSV nu conține toate coloanele obligatorii.",
  "details": {
    "missing_columns": ["amount", "transaction_date"]
  }
}
```

### Evoluția către procesare asincronă

În MVP, API-ul citește și procesează CSV-ul în timpul requestului, apoi întoarce statisticile. Este simplu de implementat și de testat, dar poate ține requestul ocupat pentru fișiere mari.

Ulterior, `POST /imports` acceptă fișierul, creează un job și răspunde imediat:

**Status:** `202 Accepted`

```json
{
  "import_id": "import_123",
  "status": "pending"
}
```

Un worker procesează CSV-ul în fundal, iar clientul urmărește starea prin `GET /imports/{import_id}`.

---

## 3. Consultarea unui import

### Request

```http
GET /imports/import_123
```

### Răspuns pentru import finalizat

**Status:** `200 OK`

```json
{
  "import_id": "import_123",
  "status": "completed",
  "created": 42,
  "duplicates_skipped": 3,
  "invalid_rows": 1
}
```

### Eroare: import inexistent sau inaccesibil

**Status:** `404 Not Found`

```json
{
  "code": "import_not_found",
  "message": "Importul nu există sau nu este disponibil pentru utilizatorul curent."
}
```

### Stări pentru versiunea asincronă

- `pending`: jobul a fost creat, dar worker-ul nu a început procesarea;
- `processing`: worker-ul citește și procesează fișierul;
- `completed`: procesarea s-a terminat cu succes;
- `failed`: procesarea nu s-a putut termina; răspunsul poate conține un mesaj sigur pentru client.

---

## Întrebare de verificare

### De ce avem `GET /imports/{import_id}` dacă MVP-ul este sincron?

> În MVP, endpointul poate exista chiar dacă `POST /imports` întoarce direct statisticile, deoarece oferă un contract stabil pentru istoricul importurilor. Când procesarea devine asincronă, același endpoint oferă statusul `pending`, `processing`, `completed` sau `failed`, fără ca clientul să învețe un API nou.

---

## Formulare de reținut

> Un contract API definește intrările, ieșirile, codurile HTTP și erorile unui endpoint, independent de implementarea internă.
