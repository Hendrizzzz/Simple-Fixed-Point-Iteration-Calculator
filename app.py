import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from convergence_engine import IterationEngine

st.set_page_config(
    page_title="The Convergence Engine",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        .stApp {
            background_color: #0e1117;
        }
        [data-testid="stSidebar"] {
            min-width: 400px;
            max-width: 400px;
        }
        .css-1d391kg {
            padding-top: 1rem;
        }
        .metric-card {
            background-color: #262730;
            padding: 15px;
            border-radius: 10px;
            text_align: center;
        }
    </style>
""", unsafe_allow_html=True)

if 'engine' not in st.session_state:
    st.session_state.engine = IterationEngine()
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
if 'history_df' not in st.session_state:
    st.session_state.history_df = pd.DataFrame(columns=["Iteration", "Previous X", "Current X", "Error (%)"])
if 'auto_complete' not in st.session_state:
    st.session_state.auto_complete = False

# Sidebar dawg
with st.sidebar:
    st.title("Configuration")
    
    g_func_input = st.text_input("Function g(x):", value="np.cos(x)", help="Enter a python expression using 'x' and 'np'.")
    x0_input = st.text_input("Initial Guess x0:", value="0.5")
    
    col1, col2 = st.columns(2)
    with col1:
        tol_input = st.text_input("Tolerance:", value="0.0001")
    with col2:
        max_iter_input = st.number_input("Max Iterations:", value=100, min_value=1, step=1)
        
    decimals = st.slider("Decimal Places:", min_value=0, max_value=20, value=6)
    
    if st.button("Initialize / Reset", type="primary"):
        success, msg = st.session_state.engine.initialize(g_func_input, x0_input)
        if success:
            st.session_state.initialized = True
            st.session_state.auto_complete = False
            st.session_state.history_df = pd.DataFrame([{
                "Iteration": 0,
                "Previous X": st.session_state.engine.previous_x,
                "Current X": st.session_state.engine.previous_x,
                "Error (%)": 0.0
            }])
            st.success(f"Initialized: x₀ = {st.session_state.engine.previous_x}")
        else:
            st.error(msg)
            st.session_state.initialized = False

    st.markdown("---")
    
    col_step, col_auto = st.columns(2)
    with col_step:
        if st.button("Next Step", disabled=not st.session_state.initialized or st.session_state.auto_complete):
             result = st.session_state.engine.step()
             if result and "error" in result and isinstance(result["error"], str):
                 st.error(result["error"])
             elif result:
                 new_row = {
                     "Iteration": result["step"],
                     "Previous X": result["x_in"],
                     "Current X": result["x_out"],
                     "Error (%)": result["error"]
                 }
                 st.session_state.history_df = pd.concat([st.session_state.history_df, pd.DataFrame([new_row])], ignore_index=True)

    with col_auto:
        if st.button("Run Auto", disabled=not st.session_state.initialized):
            try:
                tol_val = float(tol_input)
                results = st.session_state.engine.run_auto(tol_val, int(max_iter_input))
                if results:
                    new_rows = []
                    for res in results:
                         new_rows.append({
                             "Iteration": res["step"],
                             "Previous X": res["x_in"],
                             "Current X": res["x_out"],
                             "Error (%)": res["error"]
                         })
                    st.session_state.history_df = pd.concat([st.session_state.history_df, pd.DataFrame(new_rows)], ignore_index=True)
                    st.session_state.auto_complete = True
            except ValueError:
                st.error("Invalid tolerance value.")


# Main Content
st.title("The Convergence Engine")

if not st.session_state.initialized:
    st.info("👈 Please initialize the function in the sidebar to start.")
else:
    last_row = st.session_state.history_df.iloc[-1]
    curr_x = last_row["Current X"]
    curr_err = last_row["Error (%)"]
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Current Value (x)", f"{curr_x:.{decimals}f}")
    with c2:
        st.metric("Relative Error", f"{curr_err:.{decimals}f}%")
    with c3:
        try:
            tol_val = float(tol_input)
            if curr_err < tol_val and last_row["Iteration"] > 0:
                st.success("TOLERANCE MET ✅")
            else:
                st.caption("Iterating...")
        except:
            pass

    tab1, tab2 = st.tabs(["Visualization", "Data Table"])

    with tab1:
        fig, ax = plt.subplots(figsize=(8, 6))
        
        x0_start = st.session_state.engine.history[0][0] # x0 is first point x
        all_xs = [p[0] for p in st.session_state.engine.history] + [p[1] for p in st.session_state.engine.history]
        min_dim = min(all_xs) - 1
        max_dim = max(all_xs) + 1
        
        x_vals = np.linspace(min_dim, max_dim, 400)
        
        ax.plot(x_vals, x_vals, color="#00ff00", label="y = x", linewidth=1.5, linestyle="--")
        try:
            y_vals = [st.session_state.engine.g_func(x) for x in x_vals]
            ax.plot(x_vals, y_vals, color="#00ffff", label=f"y = {st.session_state.engine.g_str}", linewidth=1.5)
        except Exception as e:
            st.error(f"Plotting error: {e}")

        # Cobweb Plot
        if len(st.session_state.engine.history) > 0:
            xs_hist = [p[0] for p in st.session_state.engine.history]
            ys_hist = [p[1] for p in st.session_state.engine.history]
            ax.plot(xs_hist, ys_hist, color="#ffff00", linewidth=1, alpha=0.8)
            ax.plot(curr_x, curr_x, 'o', color="#ffff00", markersize=5) 

        # Subplot Styles
        ax.set_facecolor("#2b2b2b")
        fig.patch.set_facecolor("#0e1117")
        ax.tick_params(colors="white")
        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white') 
        ax.spines['left'].set_color('white')
        ax.spines['right'].set_color('white')
        
        ax.legend(facecolor="#262730", labelcolor="white")
        ax.grid(True, linestyle="--", alpha=0.3)
        ax.set_title("Cobweb Plot", color="white")
        
        st.pyplot(fig)

    with tab2:
        display_df = st.session_state.history_df.copy()
        display_df["Previous X"] = display_df["Previous X"].apply(lambda x: f"{x:.{decimals}f}")
        display_df["Current X"] = display_df["Current X"].apply(lambda x: f"{x:.{decimals}f}")
        display_df["Error (%)"] = display_df["Error (%)"].apply(lambda x: f"{x:.{decimals}f}")
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
