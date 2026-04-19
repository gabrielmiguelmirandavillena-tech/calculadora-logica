import streamlit as st
import pandas as pd
import itertools
import re

# Configuración estética
st.set_page_config(page_title="LogicPro Master", layout="wide")
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; font-weight: bold; }
    .main { background-color: #f5f7f9; }
    </style>
    """, unsafe_allow_html=True)

st.title("🖥️ Analizador Lógico Proposicional")
st.write("Construye tu expresión usando el teclado dinámico.")

# Inicializar el estado de la expresión si no existe
if 'expr' not in st.session_state:
    st.session_state.expr = ""

# --- INTERFAZ DE USUARIO (TECLADO) ---
col_main, col_side = st.columns([2, 1])

with col_main:
    # Pantalla de visualización
    st.info(f"**Expresión actual:** `{st.session_state.expr if st.session_state.expr else 'Vacío...'}`")
    
    # Filas de botones
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    if c1.button("P"): st.session_state.expr += "P "
    if c2.button("Q"): st.session_state.expr += "Q "
    if c3.button("R"): st.session_state.expr += "R "
    if c4.button("S"): st.session_state.expr += "S "
    if c5.button("("): st.session_state.expr += "( "
    if c6.button(")"): st.session_state.expr += " )"

    o1, o2, o3, o4, o5, o6 = st.columns(6)
    if o1.button("NOT (¬)"): st.session_state.expr += "not "
    if o2.button("AND (∧)"): st.session_state.expr += "and "
    if o3.button("OR (∨)"): st.session_state.expr += "or "
    if o4.button("IF (→)"): st.session_state.expr += "=> "
    if o5.button("IFF (↔)"): st.session_state.expr += "== "
    if o6.button("XOR (⊕)"): st.session_state.expr += "^ "

    if st.button("🗑️ Limpiar Todo"):
        st.session_state.expr = ""
        st.rerun()

# --- LÓGICA DE PROCESAMIENTO ---
def evaluate_logic(expr, values):
    # Reemplazar implicación: A => B  es  (not A or B)
    # El orden de reemplazo importa para no romper la sintaxis
    temp_expr = expr.replace("=>", " <= ") # Python usa <= para implicación en booleanos
    try:
        return eval(temp_expr, {"__builtins__": {}}, values)
    except:
        return None

if st.button("🚀 Generar Análisis Completo", type="primary"):
    if not st.session_state.expr:
        st.error("Por favor, construye una expresión primero.")
    else:
        try:
            vars_found = sorted(list(set(re.findall(r'\b[P-S]\b', st.session_state.expr))))
            combos = list(itertools.product([True, False], repeat=len(vars_found)))
            
            data = []
            results_list = []
            
            for combo in combos:
                env = dict(zip(vars_found, combo))
                res = evaluate_logic(st.session_state.expr, env)
                
                if res is None: raise Exception("Sintaxis inválida")
                
                row = {v: (1 if env[v] else 0) for v in vars_found}
                row["Resultado"] = 1 if res else 0
                data.append(row)
                results_list.append(res)
            
            # --- MOSTRAR RESULTADOS ---
            df = pd.DataFrame(data)
            
            with col_side:
                st.subheader("Análisis de Propiedades")
                if all(results_list):
                    st.success("✅ **Tautología**")
                elif not any(results_list):
                    st.error("❌ **Contradicción**")
                else:
                    st.warning("⚠️ **Contingencia**")
                
                st.metric("Filas generadas", len(df))
                st.download_button("Descargar CSV", df.to_csv(index=False), "tabla_verdad.csv")

            st.subheader("Tabla de Verdad Resultante")
            st.dataframe(df.style.background_gradient(cmap='Blues', subset=['Resultado']), use_container_width=True)
            
        except Exception as e:
            st.error(f"Error en la expresión: Asegúrate de cerrar paréntesis y usar conectores válidos.")
