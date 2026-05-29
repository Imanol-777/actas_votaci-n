# ♠ Klondike Solitaire — Flet 0.85.x / Python 3.14

Implementación completa del clásico **Klondike Solitaire** usando
[Flet](https://flet.dev) como framework de UI y Python puro para la lógica.

---

## Estructura del proyecto

```
solitaire_klondike/
├── main.py          ← Punto de entrada + toda la UI (SolitaireApp)
├── game_logic.py    ← Lógica del juego (Card, Deck, GameState)
├── card_widget.py   ← Widgets visuales de cartas (cara, reverso, drag)
├── requirements.txt ← Dependencias
└── README.md        ← Este archivo
```

---

## Instalación y ejecución

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar
python main.py
```

---

## Arquitectura y explicación del código

### `game_logic.py` — Modelo / Lógica pura

Este módulo no importa Flet; es puro Python. Tres clases principales:

#### `Card`
Representa una carta con `suit` (palo), `rank` (valor) y `face_up` (visible).
Propiedades derivadas: `value` (0–12), `is_red`/`is_black`, `color`.

#### `Deck`
Genera las 52 cartas (`Card` × palos × valores) y las baraja con `random.shuffle`.

#### `GameState`
Estado completo de la partida:

| Atributo       | Tipo                  | Descripción                        |
|----------------|-----------------------|------------------------------------|
| `stock`        | `list[Card]`          | Pila de robo (boca abajo)          |
| `waste`        | `list[Card]`          | Descarte (carta superior visible)  |
| `foundations`  | `list[list[Card]] ×4` | Fundaciones A→K por palo           |
| `tableau`      | `list[list[Card]] ×7` | 7 columnas de juego                |

**Reglas implementadas:**
- **Tableau**: solo Rey en columna vacía; alternancia de color + valor consecutivo descendente.
- **Fundación**: As en vacía; mismo palo + valor consecutivo ascendente.
- **Reciclar stock**: cuando se vacía, el waste se invierte de vuelta.
- **Victoria**: las 4 fundaciones tienen 13 cartas cada una.

---

### `card_widget.py` — Vista / Widgets Flet

Funciones que construyen controles Flet para las cartas:

| Función             | Retorna          | Descripción                               |
|---------------------|------------------|-------------------------------------------|
| `_card_face(card)`  | `ft.Container`   | Cara visible: esquinas + símbolo central  |
| `_card_back()`      | `ft.Container`   | Reverso azul con patrón interior          |
| `empty_slot(label)` | `ft.Container`   | Casilla vacía con borde punteado          |
| `make_card_widget()`| `ft.Control`     | Widget final: Draggable o estático        |

**Decisión de diseño**: `make_card_widget` devuelve un `ft.Draggable` si la carta
está boca arriba y `draggable=True`. El `data` del Draggable es un JSON string
con el origen del movimiento (`{"src": "waste"}`, `{"src": "tableau", "col": 2, "idx": 5}`),
que se parsea en los handlers de drop.

**Nota sobre `RotatedBox`**: la esquina inferior derecha de la carta se rota 180°
usando `ft.RotatedBox(quarter_turns=2)`, que es la forma correcta en Flet 0.85+
(no `ft.Transform`).

---

### `main.py` — Controlador / Presentador

#### `SolitaireApp`

Sigue el patrón **Passive View**: la UI no contiene lógica; solo traduce eventos
en llamadas a `GameState` y luego llama a `_refresh()`.

**Ciclo de vida:**
```
__init__
  └─ _setup_page()   ← configura ventana, colores, título
  └─ _build_ui()     ← crea contenedores de referencia (refs vacíos)
        └─ _refresh() ← primera renderización

evento de usuario (tap, drop)
  └─ _on_*()         ← modifica self.state (GameState)
        └─ _refresh() ← re-renderiza todo
```

**`_refresh()`** es el único lugar donde el modelo se traduce a vista.
Re-renderiza: stock → waste → 4 fundaciones → 7 columnas de tableau.

#### Sistema de Drag & Drop

- Cada carta arrastrable es un `ft.Draggable(group="card", data=json_str)`.
- Cada zona de destino es un `ft.DragTarget(group="card", on_accept=handler)`.
- El `data` viaja como JSON string y se parsea en `_on_drop_foundation` /
  `_on_drop_tableau` para saber exactamente qué carta viene de dónde.

#### Renderizado del Tableau (`_render_tableau`)

Las cartas se apilan verticalmente usando `ft.Stack` con posicionamiento
absoluto (`top=y, left=0`). El offset se acumula:
- Carta boca abajo → 20 px visibles.
- Carta boca arriba → 28 px visibles.

Encima de toda la pila se coloca un `ft.DragTarget` transparente para
capturar los drops sobre la columna.

---

## Controles disponibles en el juego

| Acción               | Cómo                                              |
|----------------------|---------------------------------------------------|
| Robar carta          | Click en el mazo (stock)                          |
| Reciclar waste       | Click en el ícono de reciclaje (stock vacío)      |
| Mover carta          | Arrastrar y soltar en columna o fundación         |
| Auto-completar       | Botón "Auto ♠" (mueve lo posible a fundaciones)   |
| Nueva partida        | Botón "Nueva partida"                             |

---

## Versiones requeridas

- **Python** 3.12+ (compatible con 3.14)
- **Flet** 0.85.2 o superior
