import streamlit as st
import requests
import pandas as pd

WEBHOOK_URL = "https://hook.us2.make.com/n0wfd9ahdtcvw7jsg8tt1l5g0kk6wkdo"

st.set_page_config(page_title="Portal de Facturas", layout="wide")
st.title("📄 Portal de Facturas de Proveedores")

cuit = st.text_input("Ingresá tu CUIT")


def normalizar_estado(cols: dict) -> str:
    """
    Busca el estado en distintas variantes posibles del JSON de Monday.
    Regla especial:
    - si el label/text es 'Downloaded' => mostrar 'Pendiente'
    """
    candidatos = [
        cols.get("status"),
        cols.get("color_mkv8nqvv"),
        cols.get("color_mkvnb20x"),
        cols.get("color_mkvn9vzd"),
        cols.get("color_mkvnh3q7"),
        cols.get("color_mkvn4n98"),
    ]

    for candidato in candidatos:
        if candidato is None:
            continue

        # Caso 1: ya viene como texto simple
        if isinstance(candidato, str):
            estado = candidato.strip()
            if estado:
                return "Pendiente" if estado.lower() == "downloaded" else estado

        # Caso 2: viene como dict
        if isinstance(candidato, dict):
            # posibles lugares donde puede venir el texto/label
            posibles = [
                candidato.get("text"),
                candidato.get("label"),
                candidato.get("additional_info", {}).get("label"),
                candidato.get("additonal_info", {}).get("label"),  # typo común de Monday/Make
            ]

            for valor in posibles:
                if isinstance(valor, str) and valor.strip():
                    estado = valor.strip()
                    return "Pendiente" if estado.lower() == "downloaded" else estado

    return ""


if st.button("Buscar facturas"):
    if not cuit:
        st.warning("Ingresá un CUIT")
    else:
        try:
            response = requests.post(
                WEBHOOK_URL,
                json={"cuit": cuit},
                timeout=30,
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

                fecha = cols.get("date", {}).get("text", "")

                rows.append({
                    "Fecha carga": fecha,
                    "Factura": f.get("name", ""),
                    "CUIT": cols.get("numeric_mknyacxz", ""),
                    "Mail": cols.get("lookup_mkszyw7y", ""),
                    "Estado": normalizar_estado(cols),
                })

            df = pd.DataFrame(rows)

            if df.empty:
                st.warning("No se encontraron facturas")
            else:
                # ordenar por fecha descendente
                df = df.sort_values(by="Fecha carga", ascending=False, na_position="last")

                st.success(f"{len(df)} factura(s) encontrada(s)")
                st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error("Error al consultar")
            st.write(str(e))
