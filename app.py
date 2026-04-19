import streamlit as st
import pandas as pd
import itertools
import re

# Configuración básica sin colores fijos para evitar errores visuales
st.set_page_config(page_title="Ingeniería Lógica", layout="wide")

st.title("🖥️ Analizador Proposicional Profesional")
st.write("Usa el teclado o escribe directamente. Resultados en binario (0/1).")

# Estado de la expresión
if 'expr' not in st.session_state:
    st.session_state.expr = ""

# Funciones de control
def add(val): st.session_state.expr += val
def clear(): st.session_state.expr = ""
def undo(): st.session_state.expr = st.session_state.expr.strip()[:-1]

# --- INTERFAZ ---
# Caja de texto principal (puedes borrar la 'Q' extra manualmente aquí si aparece)
st.session_state.expr = st.text_input("Expresión actual:", value=st.session_state.expr)

# Teclado dinámico (Sin CSS invasivo para que se vea bien en cualquier tema)
c1, c2, c3, c4, c5, c6 = st.columns(6)
if c1.button("P"): add("P "); st.rerun()
if c2.button("Q"): add("Q "); st.rerun()
if c3.button("R"): add("R "); st.rerun()
if c4.button("S"): add("S "); st.rerun()
if c5.button("("): add("( "); st.rerun()
if c6.button(")"): add(") "); st.rerun()

o1, o2, o3, o4, o5, o6 = st.columns(6)
if o1.button("NOT"): add("not "); st.rerun()
if o2.button("AND"): add("and "); st.rerun()
if o3.button("OR"): add("or "); st.rerun()
if o4.button("IF"): add("=> "); st.rerun()
if o5.button("IFF"): add("== "); st.rerun()
if o6.button("XOR"): add("^ "); st.rerun()

col_util1, col_util2 = st.columns(2)
if col_util1.button("⬅️ Corregir", use_container_width=True): undo(); st.rerun()
if col_util2.button("🗑️ Limpiar Todo", use_container_width=True): clear(); st.rerun()

# --- LÓGICA DE CÁLCULO ---
def evaluar_logica(formula, valores):
    # En Python, el operador '<=' funciona como implicación lógica (A implica B)
    f_procesada = formula.replace("=>", "<=")
    try:
        return eval(f_procesada, {"__builtins__": {}}, valores)
    except:
        return None

if st.button("🚀 GENERAR ANÁLISIS", type="primary", use_container_width=True):
    if not st.session_state.expr:
        st.warning("La expresión está vacía.")
    else:
        try:
            # Extraer variables P, Q, R, S
            vars_encontradas = sorted(list(set(re.findall(r'\b[P-S]\b', st.session_state.expr))))
            
            if not vars_encontradas:
                st.error("No se detectaron variables válidas (P, Q, R, S).")
            else:
                combinaciones = list(itertools.product([True, False], repeat=len(vars_encontradas)))
                tabla = []
                resultados_puros = []

                for combo in combinaciones:
                    contexto = dict(zip(vars_encontradas, combo))
                    res = evaluar_logica(st.session_state.expr, contexto)
                    
                    if res is None: raise Exception("Error de sintaxis")
                    
                    # Crear fila con 1s y 0s
                    fila = {v: (1 if contexto[v] else 0) for v in vars_encontradas}
                    fila["Resultado"] = 1 if res else 0
                    tabla.append(fila)
                    resultados_puros.append(res)

                # Mostrar Tabla
                df = pd.DataFrame(tabla)
                st.divider()
                
                # Clasificación de ingeniería
                if all(resultados_puros):
                    st.success("✨ TAUTOLOGÍA")
                elif not any(resultados_puros):
                    st.error("❌ CONTRADICCIÓN")
                else:
                    st.warning("⚖️ CONTINGENCIA")
                
                st.table(df) # st.table es más estable que st.dataframe para entregas académicas
                
        except:
            st.error("Sintaxis incorrecta. Revisa que los operadores y paréntesis estén balanceados.")
