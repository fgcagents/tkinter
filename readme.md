# 🚇 Gestor de Treballadors - Sistema d'Assignacions

Aplicació de gestió de treballadors amb algorisme genètic per optimitzar assignacions de serveis.

## 📋 Característiques

- **Gestió de Descansos**: Afegir, modificar i eliminar descansos de treballadors
- **Anàlisi de Disponibilitat**: Analitzar cobertura de serveis en períodes específics
- **Algorisme Genètic**: Generació automàtica d'assignacions optimitzades
- **Estadístiques**: Visualització de dades i reports

## 🚀 Instal·lació

### Requisits

- Python 3.8 o superior
- SQLite3 (inclòs amb Python)
- Base de dades `treballadors.db` configurada

### Passos

1. **Clonar o descarregar el projecte**

2. **Crear entorn virtual (recomanat)**
python -m venv venv
source venv/bin/activate # Linux/Mac
venv\Scripts\activate # Windows

text

3. **Instal·lar dependències**
pip install -r requirements.txt

text

4. **Configurar base de dades**
   - Assegura't que `treballadors.db` està al directori principal
   - O modifica `config.py` per apuntar a la teva BD

5. **Copiar mòduls core**
   - Crea el directori `core/`
   - Copia els teus fitxers existents:
     - `genetic_algorithm.py`
     - `data_loader.py`
     - `data_structures.py`
     - `constraints.py`

## ▶️ Execució

python app.py

text

## 📁 Estructura del Projecte

project_root/
├── app.py # Punt d'entrada
├── config.py # Configuració global
├── requirements.txt # Dependències
├── README.md # Aquest fitxer
├── treballadors.db # Base de dades SQLite
│
├── models/ # Capa de dades
│ ├── init.py
│ └── database.py # Gestió de BD
│
├── controllers/ # Lògica de negoci
│ ├── init.py
│ ├── descansos_controller.py
│ ├── disponibilitat_controller.py
│ └── genetic_controller.py
│
├── gui/ # Interfície gràfica
│ ├── init.py
│ ├── main_window.py # Finestra principal
│ ├── styles.py # Estils i tema
│ │
│ ├── views/ # Vistes principals
│ │ ├── init.py
│ │ ├── descansos_view.py
│ │ ├── disponibilitat_view.py
│ │ ├── genetic_view.py
│ │ └── estadistiques_view.py
│ │
│ └── widgets/ # Widgets personalitzats
│ ├── init.py
│ ├── date_picker.py
│ ├── data_table.py
│ └── progress_dialog.py
│
├── core/ # Lògica de l'algorisme
│ ├── genetic_algorithm.py
│ ├── data_loader.py
│ ├── data_structures.py
│ └── constraints.py
│
├── logs/ # Fitxers de log
└── exports/ # Fitxers exportats

text

## 🎯 Ús de l'Aplicació

### Gestió de Descansos

1. Cerca un treballador pel nom, ID o plaça
2. Selecciona'l de la llista de resultats
3. Visualitza els seus descansos per any
4. Afegeix descansos individuals o períodes
5. Elimina descansos si cal

### Anàlisi de Disponibilitat

1. Selecciona el rang de dates a analitzar
2. Clica "Analitzar Disponibilitat"
3. Revisa els resultats (serveis coberts/descoberts)
4. Exporta a CSV si cal

### Algorisme Genètic

1. Configura el període d'assignació
2. Ajusta paràmetres (població, generacions)
3. Executa l'algorisme
4. Revisa i exporta les assignacions generades

### Estadístiques

- Consulta descansos per treballador i any
- Visualitza assignacions generades
- Detecta baixes llargues actives

## ⚙️ Configuració

Edita `config.py` per modificar:

- Ruta de la base de dades
- Paràmetres de l'algorisme genètic
- Colors i estils de la interfície
- Formats de data
- Límits i validacions

## 📝 Logging

Els logs es guarden a `logs/app.log`. Nivell configurable a `config.py`.

## 🐛 Resolució de Problemes

### Error: "No s'ha trobat la base de dades"
- Verifica que `treballadors.db` existeix
- Comprova la ruta a `config.py`

### Error en importar mòduls core
- Assegura't que els fitxers estan a `core/`
- Verifica que `__init__.py` existeix a cada directori

### L'algorisme no s'executa
- Comprova que els mòduls core són compatibles
- Revisa els logs per errors específics

## 📄 Llicència

[Especifica la teva llicència aquí]

## 👤 Autor

[El teu nom]

## 📧 Contacte

[El teu email]