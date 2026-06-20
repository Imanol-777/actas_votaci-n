CARD_W, CARD_H = 90, 130
MARGIN = 20
GAP = 16
TOP_Y = MARGIN                       
TABLEAU_Y = TOP_Y + CARD_H + 25      
FD_OFF = 14                          
FU_OFF = 30                          
CANVAS_W = MARGIN * 2 + 7 * CARD_W + 6 * GAP   # 766
CANVAS_H = 840

# --- Tamaño máximo de la imagen personalizada del rey ---
KING_IMG_W = CARD_W - 14
KING_IMG_H = CARD_H - 46

# --- Tamaño máximo de la imagen personalizada del as ---
ACE_IMG_W = CARD_W - 14
ACE_IMG_H = CARD_H - 46

# --- Tamaño máximo de la imagen personalizada de la reina ---
QUEEN_IMG_W = CARD_W - 14
QUEEN_IMG_H = CARD_H - 46

# --- Tamaño máximo de la imagen personalizada del jota ---
JACK_IMG_W = CARD_W - 14
JACK_IMG_H = CARD_H - 46

# --- Colores ---
COL_FELT = "#0a6b3b"      
COL_CARD = "#fdfdf7"      
COL_BACK = "#1d3b8b"      
COL_BACK2 = "#3a5fc0"
COL_SLOT = "#0d5c34"      
COL_SLOT_LINE = "#1c8a52"
COL_RED = "#c81e1e"
COL_BLACK = "#1a1a1a"
COL_GOLD = "#d4af37"      # borde de un rey con imagen personalizada
COL_BLUE = "#270bc5"    # borde de un as con imagen personalizada
COL_RED = "#ff0000"  # borde de una reina con imagen personalizada
COL_PURPLE = "#9C149C"  # borde de un jota con imagen personalizada

def col_x(i):
    """Coordenada X de la columna i (0..6)."""
    return MARGIN + i * (CARD_W + GAP)
