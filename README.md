# Employee Time Tracking API

DEMO einer REST-API, mit der Arbeitszeiten von Mitarbeiter:innen erfasst und
ausgewertet werden können. gzip komprimierte Ausgabe & Manipulation von Mitarbeiter- und Schichtdaten. Nur Responses größer als 1000 Bytes werden komprimiert.

CRUD-Endpoints sind enthalten (siehe Beispiel-Requests).
Außerdem: Ausgabe von Einzel-Statistiken und Gesamtüberblick.


**Demo-Hinweis:** `.env` Datei ist für Demozwecke im Repository enthalten.
Die DB ist ebenfalls inkludiert.

**PRÄSENTATION:** https://excalidraw.com/#json=aNhQEsAFSwcvjRkEqzepC,31kN60fbPW81vzRPt_tU1A


## API-Features:

- Mitarbeiter:innen verwalten (CRUD)
- Arbeitszeiten für Mitarbeiter erfassen (CRUD)
- Validierungen:
    - keine überlappenden Schichten (VALIDATION 1)
    - maximale Anzahl aufeinander folgender Arbeitstage: 5 (VALIDATION 2)
    - maximale Tagesarbeitszeit: nicht mehr als 10 Stunden (VALIDATION 3)
    - simpler Check über das pydantic-SCHEMA ob korrekte Zeitangaben gemacht wurden (Schichtbeginn vor Schichtende) (VALIDATION 4)
- Auswertungen pro Mitarbeiter, u.a. mit:
    - Anzahl der Schichten und gearbeiteten Tage
    - Durchschnittliche Pause pro Schicht
    - Durchschnittliche Schichtlänge
- Statistik über alle Mitarbeiter


## Stack

- FastAPI mit GZipMiddleware
- SQLite (async sqlite-Connector "aiosqlite")
- async DB Logik mit sqlalchemy
- uvicorn mit uvloop
- pytest, pytest-asyncio & httpx für Tests


## Installation

### mit uv (empfohlen)
`uv sync`

### mit pip
`pip install -e .`

### BONUS: mit docker
- `docker build -t demoapi .`
- `docker run -p 4567:4567 demoapi`

-> START der APP durch Ausführung der main.py im Projekt-Root oder durch Starten des Docker Containers

## BONUS: Tests
Basis Tests mit in-memory DB für /employees und /shifts (siehe Ordner tests)

Ausführung der Tests im Projekt-Root:
`pytest -v`

## Beispiel-Requests

Für einen gesamten Überblick einfach die docs aufrufen:
http://localhost:4567/docs

### Auswahl an CRUD-Endpoints
- `POST /employees/                  → Mitarbeiter anlegen`
- `GET    /employees/                 → Mitarbeiter-Liste`
- `GET    /employees/{id}/summary     → Statistik eines Mitarbeiters via ID abrufen`
- `GET    /employees/{employee_id}    → Mitarbeiter via ID abrufen`
- `PATCH  /employees/{employee_id}    → Mitarbeiter via ID aktualisieren`
- `DELETE /employees/{employee_id}    → Mitarbeiter via ID löschen`

ähnlich verhält es sich mit den shift-Endpoints für die Schichten der Mitarbeiter (siehe /docs)

#### Summary Endpoint: Mitarbeiter-Einzelstatistik
Mitarbeiter ID 1:
`http://localhost:4567/employees/1/summary`


### BONUS: Gesamt-Statistik
`http://localhost:4567/statistics`


#### Mitarbeiterin anlegen:
`curl -X 'POST' \
  'http://localhost:4567/employees/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "employee_number": "DE0002",
  "first_name": "agnes",
  "last_name": "müller",
  "is_active": true
}'`

#### alle Mitarbeiter abfragen (mit pagination-Option durch skip & limit Parameter)
`curl -X 'GET' \
  'http://localhost:4567/employees/?skip=0&limit=100' \
  -H 'accept: application/json'`
