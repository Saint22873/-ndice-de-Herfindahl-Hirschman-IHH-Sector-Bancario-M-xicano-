# ============================================================
# Evolución individual de la participación de mercado por banco
# ============================================================
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

ARCHIVO = "BASE DE DATOS MODELO.xlsx"
HOJA    = "Activo"

# ---------- 1. Cargar datos ----------
df = pd.read_excel(ARCHIVO, sheet_name=HOJA)

# ---------- 2. Columnas (AJUSTA a tus nombres reales) ----------
col_periodo = "PERIODO"

bancos = {
    "BBVA":      "BBVA",
    "Santander": "SANT",
    "Banamex":   "BANAN",
    "Banorte":   "BANOR",
    "HSBC":      "HSBC",
}

col_total = "TOTAL"                # todos los bancos



# ---------- 3. Limpieza ----------
df[col_periodo] = pd.to_datetime(df[col_periodo], errors="coerce")
df = df.dropna(subset=[col_total])
df = df.sort_values(col_periodo).reset_index(drop=True)

# ---------- 4. Participación de mercado de cada banco (%) ----------
for nombre, col in bancos.items():
    df[f"share_{nombre}"] = df[col] / df[col_total] * 100

# Paleta consistente para cada banco
colores = {
    "BBVA":      "#0C2C56",   # azul oscuro BBVA
    "Santander": "#EC0000",   # rojo Santander
    "Banamex":   "#00529B",   # azul Banamex
    "Banorte":   "#D6001C",   # rojo Banorte
    "HSBC":      "#DB0011",   # rojo HSBC
}

# ============================================================
# GRÁFICA 1: Líneas superpuestas (evolución temporal)
# ============================================================
fig, ax = plt.subplots(figsize=(13, 6))

for nombre in bancos.keys():
    ax.plot(
        df[col_periodo],
        df[f"share_{nombre}"],
        label=nombre,
        color=colores[nombre],
        linewidth=2,
    )

ax.set_title("Evolución de la participación de mercado por banco (2000 – 2026)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Periodo")
ax.set_ylabel("Participación de mercado (%)")
ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
ax.grid(alpha=0.3, linestyle="--")
ax.legend(title="Banco", loc="upper right", frameon=True)

# Etiquetar último valor de cada banco
for nombre in bancos.keys():
    ultimo = df[f"share_{nombre}"].dropna().iloc[-1]
    fecha_ult = df.loc[df[f"share_{nombre}"].notna(), col_periodo].iloc[-1]
    ax.annotate(
        f"{nombre}\n{ultimo:.1f}%",
        xy=(fecha_ult, ultimo),
        xytext=(8, 0),
        textcoords="offset points",
        fontsize=8,
        color=colores[nombre],
        va="center",
        fontweight="bold",
    )

plt.tight_layout()
plt.savefig("evolucion_bancos_lineas.png", dpi=150, bbox_inches="tight")
plt.show()


# ============================================================
# GRÁFICA 2: Área apilada (composición del mercado)
# ============================================================
fig, ax = plt.subplots(figsize=(13, 6))

orden = list(bancos.keys())
shares = df[[f"share_{n}" for n in orden]].T.values  # forma: (bancos, periodos)
labels = orden

ax.stackplot(
    df[col_periodo],
    shares,
    labels=labels,
    colors=[colores[n] for n in orden],
    alpha=0.9,
)

ax.set_title("Composición del mercado bancario - área apilada (top 5 bancos)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Periodo")
ax.set_ylabel("Participación acumulada (%)")
ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
ax.grid(alpha=0.3, linestyle="--", axis="y")
ax.legend(title="Banco", loc="upper left", frameon=True, ncol=5)

plt.tight_layout()
plt.savefig("composicion_bancos_apilado.png", dpi=150, bbox_inches="tight")
plt.show()


# ============================================================
# GRÁFICA 3: Subplots individuales (una mini-gráfica por banco)
# ============================================================
fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(15, 8), sharex=True)
axes = axes.flatten()

for i, nombre in enumerate(bancos.keys()):
    ax = axes[i]
    ax.plot(df[col_periodo], df[f"share_{nombre}"],
            color=colores[nombre], linewidth=1.8)
    ax.fill_between(df[col_periodo], df[f"share_{nombre}"],
                    color=colores[nombre], alpha=0.15)

    # Estadísticas
    prom = df[f"share_{nombre}"].mean()
    maxi = df[f"share_{nombre}"].max()
    mini = df[f"share_{nombre}"].min()

    ax.axhline(prom, color="gray", linestyle=":", linewidth=1,
               label=f"Promedio: {prom:.1f}%")

    ax.set_title(f"{nombre}\nMáx: {maxi:.1f}%  |  Mín: {mini:.1f}%",
                 fontsize=11, fontweight="bold", color=colores[nombre])
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax.grid(alpha=0.3, linestyle="--")
    ax.legend(loc="lower right", fontsize=8, frameon=True)

# Ocultar el subplot sobrante
axes[5].axis("off")

fig.suptitle("Participación individual de cada banco en el mercado",
             fontsize=14, fontweight="bold", y=1.01)
plt.tight_layout()
plt.savefig("participacion_individual_bancos.png", dpi=150, bbox_inches="tight")
plt.show()


# ============================================================
# Tabla resumen por banco
# ============================================================
resumen = pd.DataFrame({
    "Banco":        list(bancos.keys()),
    "Promedio (%)": [df[f"share_{n}"].mean() for n in bancos],
    "Máximo (%)":   [df[f"share_{n}"].max()  for n in bancos],
    "Mínimo (%)":   [df[f"share_{n}"].min()  for n in bancos],
    "Último (%)":   [df[f"share_{n}"].dropna().iloc[-1] for n in bancos],
    "Desv. est.":   [df[f"share_{n}"].std()  for n in bancos],
}).round(2)

print("\n📊 Resumen estadístico por banco\n")
print(resumen.to_string(index=False))

resumen.to_excel("resumen_bancos.xlsx", index=False)
print("\n✅ Tabla guardada en: resumen_bancos.xlsx")

