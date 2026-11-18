
# ============================================================
# Cálculo del Índice Herfindahl-Hirschman (HHI) - Sector bancario
# ============================================================
import pandas as pd
import numpy as np

ARCHIVO   = "BASE DE DATOS MODELO.xlsx"
HOJA      = "Activo"
SALIDA    = "resultado_HHI.xlsx"

# ---------- 1. Cargar datos ----------
df = pd.read_excel(ARCHIVO, sheet_name=HOJA)

# ---------- 2. Definir columnas (AJUSTA a tus nombres reales) ----------
col_periodo = "PERIODO"                       # o "PERIODO"

bancos = {
    "BBVA":  "BBVA",
    "SANT":  "SANT",
    "BANAM": "BANAN",
    "BANOR": "BANOR",
    "HSBC":  "HSBC",
}

col_total = "TOTAL"                # todos los bancos
col_resto = "TOTAL_SOBR"           # todos menos los 5 grandes
col_top5  = "TOTAL_CINCO"          # solo los 5 más grandes

# ---------- 3. Limpieza ----------
df[col_periodo] = pd.to_datetime(df[col_periodo], errors="coerce")
df = df.sort_values(col_periodo).reset_index(drop=True)

# ---------- 4. Participaciones de mercado (%) ----------
for nombre, col in bancos.items():
    df[f"share_{nombre}"] = df[col] / df[col_total] * 100

df["share_Resto"] = df[col_resto] / df[col_total] * 100

# Verificación: las participaciones deben sumar ~100%
df["suma_shares"] = df[[f"share_{n}" for n in bancos] + ["share_Resto"]].sum(axis=1)

# ---------- 5. HHI ----------
# a) HHI de los 5 grandes (parcial, sin el resto)
df["HHI_top5"] = sum(df[f"share_{n}"]**2 for n in bancos)

# b) HHI aproximado: 5 grandes + resto como un solo bloque
df["HHI_aprox"] = df["HHI_top5"] + df["share_Resto"]**2

# c) HHI normalizado 0–1 (opcional)
df["HHI_norm"] = df["HHI_aprox"] / 10000

# ---------- 6. Clasificación ----------
def clasificar(h):
    if h < 1500:
        return "Baja concentración"
    elif h < 2500:
        return "Concentración moderada"
    else:
        return "Alta concentración"

df["Clasificacion"] = df["HHI_aprox"].apply(clasificar)

# ---------- 7. Mostrar resultados ----------
cols_out = [col_periodo, "HHI_top5", "HHI_aprox", "HHI_norm", "Clasificacion"]
print(df[cols_out].tail(15).to_string(index=False))

# ---------- 8. Guardar a Excel ----------
df.to_excel(SALIDA, index=False)
print(f"\nResultados guardados en: {SALIDA}")




#---------------Grafica de evolución del HHI---------------

import matplotlib.pyplot as plt

plt.figure(figsize=(11, 5))
plt.plot(df[col_periodo], df["HHI_aprox"], lw=1.8)
plt.axhline(1500, color="green", ls="--", label="Umbral 1,500")
plt.axhline(2500, color="red",   ls="--", label="Umbral 2,500")
plt.title("Evolución del HHI - Banca en México")
plt.ylabel("HHI (0 – 10,000)")
plt.xlabel("Periodo")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("HHI_evolucion.png", dpi=150)
plt.show()

