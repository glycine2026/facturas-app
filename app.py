import streamlit as st
import requests
import pandas as pd

WEBHOOK_URL = "https://hook.us2.make.com/n0wfd9ahdtcvw7jsg8tt1l5g0kk6wkdo"

st.set_page_config(page_title="Portal de Facturas", layout="wide")

st.title("📄 Portal de Facturas de Proveedores")

cuit = st.text_input("Ingresá tu CUIT")

if st.button("Buscar facturas"):

    if not cuit:
        st.warning("Ingresá un CUIT")
    else:
        try:
            response = requests.post(
                WEBHOOK_URL,
                json={"cuit": cuit}
            )

            data = response.json()
            facturas = data.get("array", [])

            rows = []

            for f in facturas:
                cols = f.get("mappable_column_values", {})

                # 🔥 ESTADO ROBUSTO
                estado_raw = (
                    cols.get("status")
                    or cols.get("color_mkv8nqvv")
                )

                # si viene como dict (Downloaded case)
                if isinstance(estado_raw, dict):
                    estado = estado_raw.get("additional_info", {}).get("label")
                else:
                    estado = estado_raw

                # normalización
                if estado and estado.lower() == "downloaded":
                    estado = "Pendiente"

                # fecha
                fecha = cols.get("date", {}).get("text")

                rows.append({
                    "Fecha carga": fecha,
                    "Factura": f.get("name"),
                    "CUIT": cols.get("numeric_mknyacxz"),
                    "Mail": cols.get("lookup_mkszyw7y"),
                    "Estado": estado
                })

            df = pd.DataFrame(rows)

            if len(df) == 0:
                st.warning("No se encontraron facturas")
            else:
                # 🔥 ordenar por fecha
                df = df.sort_values(by="Fecha carga", ascending=False)

                st.success(f"{len(df)} factura(s) encontrada(s)")
                st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error("Error al consultar")
            st.write(str(e))
