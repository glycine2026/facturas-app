import streamlit as st
import requests
import pandas as pd

WEBHOOK_URL = "https://hook.us2.make.com/n0wfd9ahdtcvw7jsg8tt1l5g0kk6wkdo"

st.set_page_config(page_title="Portal de Facturas", layout="wide")
st.title("📄 Portal de Facturas de Proveedores")

cuit = st.text_input("Ingresá tu CUIT")
filtro_factura = st.text_input("Buscar por número de factura")


# 🔥 DETECTOR UNIVERSAL DE ESTADO
def detectar_estado(cols):
    posibles_estados = []

    for key, value in cols.items():

        # Caso string directo
        if isinstance(value, str):
            posibles_estados.append(value)

        # Caso dict
        if isinstance(value, dict):
            posibles_estados.extend([
                value.get("text"),
                value.get("label"),
                value.get("additional_info", {}).get("label"),
                value.get("additonal_info", {}).get("label"),
            ])

    # limpiar
    posibles_estados = [e for e in posibles_estados if isinstance(e, str) and e.strip()]

    # 🔥 priorizar estados conocidos
    for estado in posibles_estados:
        e = estado.lower()

        if "pendiente" in e:
            return "Pendiente"
        if "enviada" in e:
            return "Enviada"
        if "ingresada" in e:
            return "Ingresada"
        if "rechazada" in e:
            return "Rechazada"
        if "downloaded" in e:
            return "Pendiente"

    # fallback
    return posibles_estados[0] if posibles_estados else ""


def obtener_fecha_estado(cols):
    for key, value in cols.items():
        if isinstance(value, dict):
            if value.get("text") and "202" in str(value.get("text")):
                return value.get("text")
    return ""


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

                fecha_carga = cols.get("date", {}).get("text")

                rows.append({
                    "Fecha carga": fecha_carga,
                    "Fecha estado": obtener_fecha_estado(cols),
                    "Factura": f.get("name"),
                    "CUIT": cols.get("numeric_mknyacxz"),
                    "Mail": cols.get("lookup_mkszyw7y"),
                    "Estado": detectar_estado(cols),
                })

            df = pd.DataFrame(rows)

            # 🔍 filtro por factura
            if filtro_factura:
                df = df[df["Factura"].astype(str).str.contains(filtro_factura)]

            if df.empty:
                st.warning("No se encontraron facturas")
            else:
                df = df.sort_values(by="Fecha carga", ascending=False)

                st.success(f"{len(df)} factura(s) encontrada(s)")
                st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error("Error al consultar")
            st.write(str(e))
