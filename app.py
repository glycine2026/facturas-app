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

            # 🔍 DEBUG (por si algo falla)
            if response.status_code != 200:
                st.error(f"Error HTTP: {response.status_code}")
                st.write(response.text)
                st.stop()

            data = response.json()

            # 🔥 CLAVE: usar "array" (salida del aggregator)
            facturas = data.get("array", [])

            rows = []

            for f in facturas:
                cols = f.get("mappable_column_values", {})

                rows.append({
                    "Factura": f.get("name"),
                    "CUIT": cols.get("numeric_mknyacxz"),
                    "Mail": cols.get("lookup_mkszyw7y"),
                    "Estado": cols.get("status") or cols.get("color_mkv8nqvv"),
                    "Fecha carga": cols.get("date", {}).get("text")
                })

            df = pd.DataFrame(rows)

            if len(df) == 0:
                st.warning("No se encontraron facturas")
            else:
                st.success(f"{len(df)} factura(s) encontrada(s)")
                st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error("Error al procesar la respuesta")
            st.write(str(e))
