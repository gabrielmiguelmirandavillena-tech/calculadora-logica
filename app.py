import streamlit as st
import pandas as pd
import itertools
import re

# Configuración de página
st.set_page_config(page_title="LogicPro v2.0", layout="centered")

# Estilos CSS para mejorar la apariencia de los botones
st.markdown("""
    <style>
    div.stButton > button:first-child { background-color: #f0f2f6; border-radius: 10px; height: 3em; font-weight: bold; }
    div.stButton > button:hover { border: 2px solid #1565c0; color: #1565c0; }
    .status-box { padding: 15px; border-radius: 10px; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🖥️ Analizador Lógico Proposicional")
st.write("Construye tu fórmula. Si los botones tardan, puedes editar el texto directamente.")

# --- GESTIÓN DE ESTADO ---
if 'expr' not in st.session_state:
    st.session_state.expr = ""

def add_to_expr(val):
    st.session_state.expr += val

def clear_expr():
    st.session_state.expr = ""

def delete_last():
    st.session_state.expr = st.session_state.expr[:-2] if st.session_state.expr.endswith(" ") else st.session_state.expr[:-1]

# --- INTERFAZ DE USUARIO ---
# Input de texto sincronizado con los botones
st.session_state.expr = st.text_input("Fórmula actual:", value=st.session_state.expr)

# Teclado Lógico
c1, c2, c3, c4, c5, c6 = st.columns(6)
if c1.button("P"): add_to_expr("P ")
if c2.button("Q"): add_to_expr("Q ")
if c3.button("R"): add_to_expr("R ")
if c4.button("S"): add_to_expr("S ")
if c5.button("("): add_to_expr("( ")
if c6.button(")"): add_to_expr(" )")

o1, o2, o3, o4, o5, o6 = st.columns(6)
if o1.button("¬ NOT"): add_to_expr("not ")
if o2.button("∧ AND"): add_to_expr("and ")
if o3.button("∨ OR"): add_to_expr("or ")
if o4.button("→ IF"): add_to_expr("=> ")
if o5.button("↔ IFF"): add_to_expr("== ")
if o6.button("⊕ XOR"): add_to_expr("^ ")

bc1, bc2 = st.columns(2)
if bc1.button("⬅️ Borrar último"): delete_last(); st.rerun()
if bc2.button("🗑️ Limpiar todo"): clear_expr(); st.rerun()

# --- PROCESAMIENTO ---
def solve_logic(formula, values):
    # Traducir implicación para Python: (A => B) -> (not A or B)
    # Usamos una traducción segura para eval()
    processed = formula.replace("=>", "<=") # En Python bool, A <= B es B or not A
    try:
        return eval(processed, {"__builtins__": {}}, values)
    except:
        return None

if st.button("🚀 GENERAR TABLA DE VERDAD", type="primary"):
    if not st.session_state.expr.strip():
        st.warning("Escribe una expresión primero.")
    else:
        try:
            # Encontrar variables (P, Q, R, S)
            vars_found = sorted(list(set(re.findall(r'\b[P-S]\b', st.session_state.expr))))
            if not vars_found:
                st.error("No se detectaron variables (P, Q, R o S).")
            else:
                # Generar combinaciones
                combos = list(itertools.product([True, False], repeat=len(vars_found)))
                rows = []
                results = []

                for c in combos:
                    context = dict(zip(vars_found, c))
                    res = solve_logic(st.session_state.expr, context)
                    
                    if res is None:
                        raise ValueError("Error de sintaxis")
                    
                    row = {v: (1 if context[v] else 0) for v in vars_found}
                    row["Resultado"] = 1 if res else 0
                    rows.append(row)
                    results.append(res)

                # Mostrar Resultados
                df = pd.DataFrame(rows)
                st.divider()
                
                # Clasificación
                if all(results):
                    st.success("✨ Es una **Tautología** (Siempre 1)")
                elif not any(results):
                    st.error("💀 Es una **Contradicción** (Siempre 0)")
                else:
                    st.warning("⚖️ Es una **Contingencia** (Mezcla de 0 y 1)")

                st.table(df)
                
        except Exception:
            st.error("❌ Error de Sintaxis: Revisa que los conectores y paréntesis estén bien puestos (ej. `P and Q`).")
