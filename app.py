import streamlit as st
import requests
import pandas as pd

# 🔗 WEBHOOKS
WEBHOOK_FACTURAS = "https://hook.us2.make.com/n0wfd9ahdtcvw7jsg8tt1l5g0kk6wkdo"
WEBHOOK_GENERAR_TOKEN = "https://hook.us2.make.com/pge18s5nwbpciprxph4o1yokco3aehne"
WEBHOOK_VALIDAR_TOKEN = "https://hook.us2.make.com/u8d830syq846gmavpbol11lo4qrvca60"

st.set_page_config(page_title="Portal de Facturas", layout="wide")
st.title("📄 Portal de Facturas de Proveedores")


# 🔐 SESSION
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.cuit = None


# 🔥 ESTADO
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


# 🔥 FECHA ESTADO
def obtener_fecha_estado(cols):
    for value in cols.values():
        if isinstance(value, dict):
            text = value.get("text")
            if text and "202" in str(text):
                return text
    return ""


# ===============================
# 🔐 LOGIN
# ===============================

if not st.session_state.autenticado:

    st.subheader("🔐 Ingreso")

    cuit_input = st.text_input("Ingresá tu CUIT")

    if st.button("Enviar código"):
        if cuit_input:
            try:
                requests.post(WEBHOOK_GENERAR_TOKEN, json={"cuit": cuit_input})
                st.success("📧 Código enviado por mail")
                st.session_state.cuit = cuit_input
            except:
                st.error("Error al enviar código")

    token_input = st.text_input("Ingresá el código")

    if st.button("Validar código"):
        try:
            response = requests.post(
                WEBHOOK_VALIDAR_TOKEN,
                json={
                    "cuit": st.session_state.cuit,
                    "token": token_input
                }
            )

            data = response.json()

            if data.get("valid"):
                st.session_state.autenticado = True
                st.success("✅ Acceso concedido")
                st.rerun()
            else:
                st.error("❌ Código incorrecto")

        except Exception as e:
            st.error("Error validando token")
            st.write(str(e))


# ===============================
# 📄 FACTURAS
# ===============================

else:

    st.success(f"Conectado como CUIT: {st.session_state.cuit}")

    if st.button("Cerrar sesión"):
        st.session_state.autenticado = False
        st.session_state.cuit = None
        st.rerun()

    if st.button("Buscar facturas"):

        try:
            response = requests.post(
                WEBHOOK_FACTURAS,
                json={"cuit": st.session_state.cuit}
            )

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
                filtro = st.text_input("Buscar por factura")

                if filtro:
                    df = df[df["Factura"].astype(str).str.contains(filtro)]

                df = df.sort_values(by="Fecha carga", ascending=False)

                st.success(f"{len(df)} factura(s) encontrada(s)")
                st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error("Error al consultar")
            st.write(str(e))
