import streamlit as st
import requests
import pandas as pd

WEBHOOK_URL = "https://hook.us2.make.com/n0wfd9ahdtcvw7jsg8tt1l5g0kk6wkdo"

st.set_page_config(page_title="Portal de Facturas", layout="wide")
st.title("📄 Portal de Facturas de Proveedores")

cuit = st.text_input("Ingresá tu CUIT")


# 🔥 DETECTOR DE ESTADO (CON PRIORIDADES)
def detectar_estado(cols):
    posibles = []

    for value in cols.values():

        if isinstance(value, str):
            posibles.append(value)

        elif isinstance(value, dict):
            posibles.extend([
                value.get("text"),
                value.get("label"),
                value.get("additional_info", {}).get("label"),
                value.get("additonal_info", {}).get("label"),
            ])

    posibles = [p.strip().lower() for p in posibles if isinstance(p, str) and p.strip()]

    # 🔥 prioridad correcta
    prioridades = [
        ("enviada", "Enviada"),
        ("rechazada", "Rechazada"),
        ("cancelada", "Cancelada"),
        ("ingresada", "Ingresada"),
        ("pendiente descarga", "Pendiente Descarga"),
        ("demorado (interno)", "Demorado (Interno)"),
        ("demorado (externo)", "Demorado (Externo)"),
        ("pendiente", "Pendiente"),
        ("downloaded", "Pendiente"),
    ]

    for key, valor in prioridades:
        for estado in posibles:
            if key in estado:
                return valor

    return posibles[0] if posibles else ""


# 🔥 FECHA DE ÚLTIMO ESTADO
def obtener_fecha_estado(cols):
    for value in cols.values():
        if isinstance(value, dict):
            text = value.get("text")
            if text and "202" in str(text):
                return text
    return ""


# 🚀 BOTÓN
if st.button("Buscar facturas"):

    if not cuit:
        st.warning("Ingresá un CUIT")
    else:
        try:
            response = requests.post(
                WEBHOOK_URL,
                json={"cuit": cuit}
            )

            if response.status_code != 200:
                st.error(f"Error HTTP: {response.status_code}")
                st.write(response.text)
                st.stop()

            data = response.json()
            facturas = data.get("array", [])

            rows = []

            for f in facturas:
                cols = f.get("mappable_column_values", {})

                rows.append({
                    "Fecha carga": cols.get("date", {}).get("text"),
                    "Fecha estado": obtener_fecha_estado(cols),
                    "Factura": f.get("name"),
                    "CUIT": cols.get("numeric_mknyacxz"),
                    "Mail": cols.get("lookup_mkszyw7y"),
                    "Estado": detectar_estado(cols),
                })

            df = pd.DataFrame(rows)

            if df.empty:
                st.warning("No se encontraron facturas")
            else:
                # 🔍 buscador aparece después
                filtro_factura = st.text_input("Buscar por número de factura")

                if filtro_factura:
                    df = df[df["Factura"].astype(str).str.contains(filtro_factura)]

                # ordenar por fecha
                df = df.sort_values(by="Fecha carga", ascending=False)

                st.success(f"{len(df)} factura(s) encontrada(s)")
                st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error("Error al consultar")
            st.write(str(e))
