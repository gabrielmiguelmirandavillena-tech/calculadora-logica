import streamlit as st
import pandas as pd
import itertools
import re

# Configuración de la página
st.set_page_config(page_title="Calculadora de Lógica Proposicional", layout="centered")

st.title("Calculadora de Tablas de Verdad")
st.write("Evalúa expresiones lógicas complejas ingresando tu proposición.")

# Instrucciones de uso
with st.expander("Ver operadores soportados"):
    st.markdown("""
    Utiliza los siguientes operadores en inglés (sintaxis de Python) para formular tu expresión:
    * **Conjunción (AND):** `and` (ej. `P and Q`)
    * **Disyunción (OR):** `or` (ej. `P or Q`)
    * **Negación (NOT):** `not` (ej. `not P`)
    * **Implicación material:** Utiliza `<=` (ej. `P <= Q`)
    * **Flecha de Peirce (NOR):** Escríbelo como `not (P or Q)`
    """)

# Entrada del usuario
expression = st.text_input(
    "Ingresa tu expresión proposicional usando letras mayúsculas para las variables:", 
    "A and (B or not C)"
)

if st.button("Generar Tabla"):
    try:
        # Extraer variables únicas buscando letras mayúsculas aisladas
        variables = sorted(list(set(re.findall(r'\b[A-Z]\b', expression))))

        if not variables:
            st.warning("No se encontraron variables. Asegúrate de usar letras mayúsculas (ej. A, B, P, Q).")
        else:
            # Generar todas las combinaciones posibles de Verdad/Falso (2^n)
            combinations = list(itertools.product([True, False], repeat=len(variables)))

            results = []
            for combo in combinations:
                # Mapear cada variable a su valor de verdad en la iteración actual
                env = dict(zip(variables, combo))
                
                # Evaluar la expresión de forma segura
                res = eval(expression, {"__builtins__": {}}, env)
                
                # Formatear la fila para la tabla
                row = {var: "V" if val else "F" for var, val in env.items()}
                row["Resultado Final"] = "V" if res else "F"
                results.append(row)

            # Convertir a DataFrame para una visualización limpia
            df = pd.DataFrame(results)
            
            st.success("Tabla generada con éxito:")
            st.table(df)
            
    except SyntaxError:
        st.error("Error de sintaxis. Verifica que los operadores y paréntesis estén bien colocados.")
    except Exception as e:
        st.error(f"Error al evaluar la expresión: {e}")
