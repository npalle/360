import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

# Título de la app
st.title("Dashboard de Ventas - tres60 Kiosco")

# Carga de archivo
uploaded_file = st.file_uploader(
    "Sube tu archivo Excel o CSV (Listado_Caja)",
    type=["xlsx", "xls", "csv"]
)

# Verifica que se haya subido un archivo
if uploaded_file is None:
    st.info("Por favor, sube un archivo para comenzar el análisis.")
    st.stop()

# Determina extensión y lee
filename = uploaded_file.name.lower()
if filename.endswith((".xlsx", ".xls")):
    df = pd.read_excel(uploaded_file, header=1)
else:
    df = pd.read_csv(uploaded_file)

# Normalizar nombres de columnas
df.rename(columns={"Importe": "Total", "Usuario": "Empleado"}, inplace=True)

# Convertir fecha y extraer hora
df["Fecha"] = pd.to_datetime(df["Fecha"])
df["Hora"] = pd.to_datetime(df["Hora"], errors="coerce").dt.hour

# Mapear día de la semana al español
dias_esp = {
    "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
    "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
}
df["DíaSemana"] = df["Fecha"].dt.day_name().map(dias_esp)

# Opciones de métricas
opciones = [
    "Ventas por día",
    "Ventas por hora",
    "Ventas por día de la semana",
    "Ventas por empleada",
    "Ventas por forma de pago"
]
if any(col.lower() in ("producto", "descripción") for col in df.columns):
    opciones.insert(0, "Ventas por producto")

# Selector de métrica
seleccion = st.sidebar.selectbox("Elige una métrica", opciones)

# Preparar gráfico
fig, ax = plt.subplots()

if seleccion == "Ventas por producto":
    col_desc = next(c for c in df.columns if c.lower() in ("producto", "descripción"))
    serie = df.groupby(col_desc)["Total"].sum().sort_values(ascending=False)
    serie.plot.bar(ax=ax)
    ax.set_ylabel("Ventas ($)")
    ax.set_title("Ventas por producto")
    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))

elif seleccion == "Ventas por día":
    # Agrupar por día del mes
    df["DíaMes"] = df["Fecha"].dt.day
    serie = df.groupby("DíaMes")["Total"].sum()
    serie.plot(ax=ax, marker="o")
    ax.set_xlabel("Día del mes")
    ax.set_ylabel("Ventas ($)")
    ax.set_title("Ventas por día")
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))

elif seleccion == "Ventas por hora":
    serie = df.groupby("Hora")["Total"].sum()
    serie.plot(kind="bar", ax=ax)
    ax.set_xlabel("Hora del día")
    ax.set_ylabel("Ventas ($)")
    ax.set_title("Ventas por hora")
    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))

elif seleccion == "Ventas por día de la semana":
    orden = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    serie = df.groupby("DíaSemana")["Total"].sum().reindex(orden)
    serie.plot(kind="bar", ax=ax)
    ax.set_ylabel("Ventas ($)")
    ax.set_title("Ventas por día de la semana")
    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))

elif seleccion == "Ventas por empleada":
    serie = df.groupby("Empleado")["Total"].sum()
    serie.plot(kind="bar", ax=ax)
    ax.set_ylabel("Ventas ($)")
    ax.set_title("Ventas por empleada")
    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))

elif seleccion == "Ventas por forma de pago":
    pagos = {
        "Efectivo": df["Forma de Pago"].str.contains("efectivo", case=False, na=False),
        "Mercado Pago": df["Forma de Pago"].str.contains("mercado pago", case=False, na=False)
    }
    datos_fp = {k: df.loc[m, "Total"].sum() for k, m in pagos.items()}
    serie = pd.Series(datos_fp)
    serie.plot(kind="bar", ax=ax)
    ax.set_ylabel("Ventas ($)")
    ax.set_title("Ventas por forma de pago")
    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))

# Mostrar gráfico en la app
st.pyplot(fig)
