import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components
import re  
from convergence_engine import IterationEngine

def get_friendly_error_message(raw_error):
    """
    Translates raw Python exceptions into helpful, non-technical user feedback.
    The ORDER of checks is critical here.
    """
    msg = str(raw_error).lower()
    
    if "division by zero" in msg:
        return "🚫 **Math Error:** Division by zero occurred. The value of 'x' hit 0."
    
    if "domain" in msg or "complex" in msg or "negative" in msg or "nan" in msg:
        return "⛔ **Domain Error:** The calculation resulted in an impossible number (e.g., Square Root of a negative number or Log of zero/negative). Check your Initial Guess."
    
    if "name" in msg and "is not defined" in msg:
        match = re.search(r"name '(.+?)' is not defined", str(raw_error))
        var_name = match.group(1) if match else "unknown"
        return f"🤔 **Unknown Word:** The app doesn't understand **'{var_name}'**. Please use standard math (e.g., `cos`, `sqrt`) and use `*` for multiplication."
    
    if "overflow" in msg or "too large" in msg:
        return "💥 **Number Explosion:** The numbers became too huge to calculate. The function is diverging."
    
    if "syntax" in msg or "unexpected eof" in msg or "parsing" in msg or "invalid syntax" in msg:
        return "✍️ **Syntax Error:** Please check your equation. You might have missing parentheses or an incomplete expression."

    return f"⚠️ **Calculation Failed:** {raw_error}"


def process_math_input(user_input):
    """
    Translates 'Human Math' to 'Python/Numpy Math' safely.
    """
    if not user_input: return ""
    
    expr = user_input.strip().replace("^", "**")
    
    mappings = [
        (r'\bcos\b', 'np.cos'), (r'\bsin\b', 'np.sin'), (r'\btan\b', 'np.tan'),
        (r'\bsqrt\b', 'np.sqrt'), (r'\bexp\b', 'np.exp'), (r'\blog\b', 'np.log'),
        (r'\bpi\b', 'np.pi'), (r'\be\b', 'np.e'), (r'\babs\b', 'np.abs')
    ]
    
    for pattern, replacement in mappings:
        expr = re.sub(fr'(?<!np\.)' + pattern, replacement, expr)
        
    return expr

st.set_page_config(
    page_title="The Convergence Engine",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        .stApp { background_color: #0e1117; }
        .metric-card { background-color: #262730; padding: 15px; border-radius: 10px; text_align: center; }
        .success-box { padding: 1rem; border-radius: 0.5rem; background-color: rgba(0, 255, 0, 0.1); border: 1px solid #00ff00; margin-bottom: 1rem; }
        div[data-testid="stToast"] { padding: 1rem; }
    </style>
""", unsafe_allow_html=True)

if 'engine' not in st.session_state:
    st.session_state.engine = IterationEngine()
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
if 'history_df' not in st.session_state:
    st.session_state.history_df = pd.DataFrame(columns=["Iteration", "Previous X", "Current X", "Error (%)"])

with st.sidebar:
    st.title("Configuration")
    
    g_func_raw = st.text_input(
        "Function g(x):", 
        value="cos(x)", 
        help="Enter the Right-Hand Side (RHS) expression."
    )
    
    x0_input = st.text_input("Initial Guess x0:", value="0.5")
    tol_input = st.text_input("Tolerance:", value="0.0001")
    max_iter_input = st.number_input("Max Iterations:", value=100, min_value=1, step=1)
    decimals = st.slider("Decimal Places:", min_value=0, max_value=20, value=6)

    submitted = st.button("Initialize / Reset", type="primary", use_container_width=True)
    
    with st.expander("📝 Math Syntax Guide"):
        st.markdown("""
        - **Power:** `x^2` or `x**2`
        - **Trig:** `cos(x)`, `sin(x)`, `tan(x)`
        - **Roots:** `sqrt(x)`
        - **Logs:** `log(x)` (natural), `exp(x)`
        - **Constants:** `pi`, `e`
        """)

    if submitted:
        if not g_func_raw.strip():
            st.error("⚠️ **Missing Input:** Please enter a function (e.g., `cos(x)`).")
            st.session_state.initialized = False
        else:
            try:
                float(x0_input) 
                valid_number = True
            except ValueError:
                st.error("🔢 **Input Error:** Initial Guess must be a valid number (e.g., 0.5, -2).")
                valid_number = False
                st.session_state.initialized = False

            if valid_number:
                processed_func = process_math_input(g_func_raw)
                
                success, msg = st.session_state.engine.initialize(processed_func, x0_input)
                
                if success:
                    st.session_state.initialized = True
                    st.session_state.history_df = pd.DataFrame([{
                        "Iteration": 0,
                        "Previous X": st.session_state.engine.previous_x,
                        "Current X": st.session_state.engine.previous_x,
                        "Error (%)": 0.0
                    }])
                    st.toast(f"System Initialized: x₀ = {st.session_state.engine.previous_x}", icon="✅")
                else:
                    friendly_msg = get_friendly_error_message(msg)
                    st.error(friendly_msg)
                    st.session_state.initialized = False

    st.markdown("---")
    
    col_step, col_auto = st.columns(2)
    
    with col_step:
        if st.button("Next Step", disabled=not st.session_state.initialized, use_container_width=True):
             result = st.session_state.engine.step()
             if result and "error" in result and isinstance(result["error"], str):
                 st.error(get_friendly_error_message(result["error"]))
             elif result:
                 new_row = {
                     "Iteration": int(result["step"]),
                     "Previous X": result["x_in"],
                     "Current X": result["x_out"],
                     "Error (%)": result["error"]
                 }
                 st.session_state.history_df = pd.concat([st.session_state.history_df, pd.DataFrame([new_row])], ignore_index=True)

    with col_auto:
        if st.button("Run Auto", disabled=not st.session_state.initialized, use_container_width=True):
            try:
                tol_val = float(tol_input)
                results = st.session_state.engine.run_auto(tol_val, int(max_iter_input))
                if results:
                    new_rows = []
                    for res in results:
                         new_rows.append({
                             "Iteration": int(res["step"]),
                             "Previous X": res["x_in"],
                             "Current X": res["x_out"],
                             "Error (%)": res["error"]
                         })
                    st.session_state.history_df = pd.concat([st.session_state.history_df, pd.DataFrame(new_rows)], ignore_index=True)
            except ValueError:
                st.error("🔢 **Input Error:** Invalid tolerance value.")


st.title("The Convergence Engine")

if not st.session_state.initialized:
    st.info("👈 Please enter a function (e.g., `cos(x)`) and initialize the system.")
else:
    if len(st.session_state.history_df) > 0:
        last_row = st.session_state.history_df.iloc[-1]
        curr_x = last_row["Current X"]
        curr_err = last_row["Error (%)"]
        curr_iter = int(last_row["Iteration"])
        
        try:
            tol_val = float(tol_input)
            is_converged = curr_err < tol_val and curr_iter > 0
        except:
            tol_val = 0.0001
            is_converged = False

        if is_converged:
            st.markdown(f"""
                <div class="success-box">
                    <h3>✅ Tolerance Met!</h3>
                    <p>The solution converged to <b>x = {curr_x:.{decimals}f}</b> at <b>Iteration {curr_iter}</b>.</p>
                </div>
            """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Current Iteration", f"#{curr_iter}")
        with c2:
            st.metric("Current Value (x)", f"{curr_x:.{decimals}f}")
        with c3:
            st.metric("Relative Error", f"{curr_err:.{decimals}f}%", delta_color="inverse")

    tab1, tab2 = st.tabs(["Interactive Visualization", "Data Table"])

    with tab1:
        history = st.session_state.engine.history
        
        x_points = [p[0] for p in history] + [p[1] for p in history]
        if not x_points:
            x_min, x_max = -1, 1
        else:
            x_min, x_max = min(x_points), max(x_points)
        
        span = x_max - x_min
        if span == 0: span = 1
        plot_min = x_min - (span * 0.2)
        plot_max = x_max + (span * 0.2)

        if plot_min < -1e5: plot_min = -1e5
        if plot_max > 1e5: plot_max = 1e5

        x_space = np.linspace(plot_min, plot_max, 500)
        y_identity = x_space
        
        try:
            y_curve = []
            for val in x_space:
                try:
                    res = st.session_state.engine.g_func(val)
                    if np.iscomplex(res) or np.isnan(res):
                        y_curve.append(None) 
                    else:
                        y_curve.append(res)
                except:
                    y_curve.append(None)
        except Exception:
            y_curve = x_space * 0 

        cobweb_x = []
        cobweb_y = []
        if len(history) > 0:
            start_x = history[0][0]
            cobweb_x.append(start_x)
            cobweb_y.append(start_x)
            for i, (prev_x, curr_x) in enumerate(history):
                cobweb_x.append(prev_x)
                cobweb_y.append(curr_x)
                cobweb_x.append(curr_x)
                cobweb_y.append(curr_x)

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=x_space, y=y_identity, mode='lines', name='y = x',
            line=dict(color='#00ff00', width=1, dash='dash')
        ))

        display_func_name = g_func_raw if 'g_func_raw' in locals() else st.session_state.engine.g_str
        fig.add_trace(go.Scatter(
            x=x_space, y=y_curve, mode='lines', name=f'g(x) = {display_func_name}',
            line=dict(color='#00ffff', width=2)
        ))

        fig.add_trace(go.Scatter(
            x=cobweb_x, y=cobweb_y, mode='lines+markers', name='Iteration Path',
            line=dict(color='#ffff00', width=1), marker=dict(size=4),
            hovertemplate='x: %{x:.6f}<br>y: %{y:.6f}'
        ))

        if len(history) > 0:
            fig.add_trace(go.Scatter(
                x=[curr_x], y=[curr_x], mode='markers', name='Current x',
                marker=dict(size=10, color='#ff00ff', symbol='circle'), hoverinfo='skip'
            ))

        fig.update_layout(
            title="Interactive Cobweb Plot",
            xaxis_title="x", yaxis_title="g(x)",
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=600,
            xaxis=dict(
                range=[plot_min, plot_max], zeroline=True, zerolinewidth=2,
                zerolinecolor='rgba(255,255,255,0.6)', showgrid=True,
                gridcolor='rgba(255,255,255,0.1)', showspikes=True,
                spikemode='across', spikesnap='cursor', spikethickness=1,
                spikecolor='rgba(255,255,255,0.3)'
            ),
            yaxis=dict(
                range=[plot_min, plot_max], zeroline=True, zerolinewidth=2,
                zerolinecolor='rgba(255,255,255,0.6)', showgrid=True,
                gridcolor='rgba(255,255,255,0.1)', showspikes=True,
                spikemode='across', spikesnap='cursor', spikethickness=1,
                spikecolor='rgba(255,255,255,0.3)'
            ),
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(0,0,0,0.5)"),
            hovermode="closest"
        )

        config = {
            'scrollZoom': True, 
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['lasso2d', 'select2d']
        }

        st.plotly_chart(fig, use_container_width=True, config=config)

    with tab2:
        df_display = st.session_state.history_df.copy()
        
        def highlight_converged_row(row):
            try:
                err = float(row['Error (%)'])
                it = int(row['Iteration'])
                if err < tol_val and it > 0:
                    return ['background-color: rgba(30, 200, 30, 0.2); color: white'] * len(row)
            except:
                pass
            return [''] * len(row)

        styled_df = df_display.style.apply(highlight_converged_row, axis=1)
        fmt = f"%.{decimals}f"

        st.dataframe(
            styled_df, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Iteration": st.column_config.NumberColumn(format="%d"),
                "Previous X": st.column_config.NumberColumn(format=fmt),
                "Current X": st.column_config.NumberColumn(format=fmt),
                "Error (%)": st.column_config.NumberColumn(format=fmt),
            }
        )