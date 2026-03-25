import streamlit as st
import requests
import pandas as pd

# 🔗 Webhook Make
WEBHOOK_URL = "https://hook.us2.make.com/n0wfd9ahdtcvw7jsg8tt1l5g0kk6wkdo"

st.set_page_config(page_title="Portal de Facturas", layout="wide")

st.title("📄 Portal de Facturas de Proveedores")

# Input CUIT
cuit = st.text_input("Ingresá tu CUIT")

if st.button("Buscar facturas"):

    if not cuit:
        st.warning("Por favor ingresá un CUIT")
    else:
        try:
            response = requests.post(
                WEBHOOK_URL,
                json={"cuit": cuit}
            )

            data = response.json()

            # Puede venir como objeto o lista
            if isinstance(data, list):
                facturas = data
            else:
                facturas = [data]

            rows = []

            for f in facturas:
                cols = f.get("mappable_column_values", {})

                rows.append({
                    "Factura": f.get("name"),
                    "CUIT": cols.get("numeric_mknyacxz"),
                    "Mail": cols.get("lookup_mkszyw7y"),
                    "Estado": cols.get("status"),
                    "Fecha carga": cols.get("date", {}).get("text")
                })

            df = pd.DataFrame(rows)

            if len(df) == 0:
                st.warning("No se encontraron facturas")
            else:
                st.success(f"{len(df)} factura(s) encontrada(s)")
                st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"Error al consultar: {e}")
