import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import re
import math




class IterationEngine:
    def __init__(self):
        self.expression = ""
        self.history = [] 
        self.previous_x = 0.0
        self.g_str = ""

    def initialize(self, func_str, x0):
        self.g_str = func_str
        self.history = []
        try:
            self.previous_x = float(x0)
            val = self.evaluate_g(self.previous_x)
            if np.isnan(val) or np.iscomplex(val):
                return False, "DomainError: Initial guess results in an undefined value."
            return True, ""
        except Exception as e:
            return False, e

    def evaluate_g(self, x):
        safe_dict = {
            "x": x,
            "np": np,
            "cos": np.cos, "sin": np.sin, "tan": np.tan,
            "sqrt": np.sqrt, "log": np.log, "exp": np.exp,
            "abs": np.abs, "pi": np.pi, "e": np.e
        }
        with np.errstate(all='ignore'):
            try:
                result = eval(self.g_str, {"__builtins__": {}}, safe_dict)
                return result
            except NameError as e:
                raise NameError(e)
            except Exception as e:
                raise e

    def step(self):
        try:
            x_in = self.previous_x
            if abs(x_in) > 1e10:
                return {"error_msg": "OverflowError: Values are too large (Divergence)"}

            x_out = self.evaluate_g(x_in)
            
            if np.isnan(x_out) or np.iscomplex(x_out):
                return {"error_msg": "DomainError: Result is not a real number."}

            if x_out == 0:
                error_pct = 0.0 if x_in == 0 else 100.0
            else:
                error_pct = abs((x_out - x_in) / x_out) * 100
            
            self.history.append((x_in, x_out))
            self.previous_x = x_out
            
            return {
                "step": len(self.history),
                "x_in": x_in,
                "x_out": x_out,
                "error": error_pct
            }
        except Exception as e:
            return {"error_msg": str(e)}

    def run_auto(self, tolerance, max_iter):
        results = []
        for _ in range(max_iter):
            res = self.step()
            if "error_msg" in res:
                results.append(res)
                break
            results.append(res)
            if res["error"] < tolerance and res["step"] > 0:
                break
        return results

    def g_func(self, val):
        return self.evaluate_g(val)






def process_math_input(user_input):
    if not user_input: return ""
    expr = user_input.strip().replace("^", "**")
    
    expr = re.sub(r'(\d)\s*(x)', r'\1*\2', expr)
    expr = re.sub(r'(\d)\s*\(', r'\1*(', expr)
    expr = re.sub(r'\)\s*(\d|x)', r')*\1', expr)

    mappings = [
        (r'\bcos\b', 'np.cos'), (r'\bsin\b', 'np.sin'), (r'\btan\b', 'np.tan'),
        (r'\bsqrt\b', 'np.sqrt'), (r'\bexp\b', 'np.exp'), (r'\blog\b', 'np.log'),
        (r'\bpi\b', 'np.pi'), (r'\be\b', 'np.e'), (r'\babs\b', 'np.abs')
    ]
    for pattern, replacement in mappings:
        expr = re.sub(fr'(?<!np\.)' + pattern, replacement, expr)
    return expr

def get_friendly_error_message(raw_error):
    msg = str(raw_error).lower()
    if "import" in msg or "module" in msg: return "🚫 **Security/Syntax Error:** Import statements not allowed."
    if "division by zero" in msg: return "🚫 **Math Error:** Division by zero."
    if "domain" in msg or "complex" in msg or "nan" in msg: return "⛔ **Domain Error:** Result is undefined."
    if "name" in msg and "is not defined" in msg: return "🤔 **Unknown Syntax:** Use standard math (e.g. `cos(x)`)."
    if "syntax" in msg: return "✍️ **Syntax Error:** Check parentheses."
    if "overflow" in msg: return "💥 **Divergence:** Values exploded to Infinity."
    return f"⚠️ **Error:** {raw_error}"

def validate_inputs(func, x0, tol):
    if not func or not func.strip(): return False, "Function input cannot be empty."
    try: float(x0)
    except: return False, "Initial Guess must be a valid number."
    try: 
        if float(tol) <= 0: return False, "Tolerance must be positive."
    except: return False, "Tolerance must be a valid number."
    return True, ""





st.set_page_config(page_title="Convergence Engine", page_icon="🕸️", layout="wide")



st.markdown("""
    <style>
        /* Global Spacing */
        .block-container { padding-top: 2rem; padding-bottom: 3rem; }

        /* --- DASHBOARD METRIC CARDS --- */
        .stat-box { 
            background-color: var(--secondary-background-color); 
            border: 1px solid rgba(128, 128, 128, 0.2);
            padding: 15px; 
            border-radius: 12px; 
            text-align: center; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: transform 0.2s ease;
        }
        .stat-box:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        }
        .stat-label { 
            color: var(--text-color); 
            opacity: 0.7;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 0.75rem; 
            margin-bottom: 5px; 
            font-weight: 600;
        }
        .stat-value { 
            color: var(--primary-color); 
            font-size: 1.6rem; 
            font-weight: 700; 
            font-family: 'Source Code Pro', monospace;
        }
        
        /* --- ALERTS --- */
        .success-box { 
            padding: 1rem; border-radius: 12px; 
            background-color: rgba(16, 185, 129, 0.15); 
            border: 1px solid rgba(16, 185, 129, 0.4); 
            color: #059669; 
            text-align: center; margin-bottom: 1.5rem; 
            font-weight: 600;
        }
        /* Dark mode adjustment for success text */
        @media (prefers-color-scheme: dark) {
            .success-box { color: #34d399; }
        }

        /* --- LANDING PAGE CARDS --- */
        .landing-card { 
            background-color: var(--secondary-background-color); 
            padding: 25px; 
            border-radius: 16px; 
            border: 1px solid rgba(128, 128, 128, 0.15); 
            height: 100%; 
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02);
            transition: all 0.3s ease;
        }
        .landing-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.08);
            border-color: var(--primary-color);
        }
        .landing-icon { 
            font-size: 3.5rem; 
            margin-bottom: 15px; 
            display: block; 
        }
        .landing-title { 
            font-weight: 800; font-size: 1.3rem; margin-bottom: 8px; 
            color: var(--text-color); 
        }
        .landing-text { 
            font-size: 0.95rem; color: var(--text-color); 
            opacity: 0.7; line-height: 1.5;
        }
    </style>
""", unsafe_allow_html=True)

if 'engine' not in st.session_state: st.session_state.engine = IterationEngine()
if 'initialized' not in st.session_state: st.session_state.initialized = False
if 'history_df' not in st.session_state: st.session_state.history_df = pd.DataFrame(columns=["Iteration", "Previous X", "Current X", "Error (%)"])
if 'runtime_error' not in st.session_state: st.session_state.runtime_error = None

with st.sidebar:
    st.header("⚙️ Configuration")
    g_func_raw = st.text_input("Function g(x):", value="cos(x)")
    x0_input = st.text_input("Initial Guess ($x_0$):", value="0.5")
    tol_input = st.text_input("Tolerance:", value="0.0001")
    
    st.markdown("---")
    st.subheader("👁️ Visuals")
    show_cobweb = st.toggle("Show Cobweb Path", value=True)
    auto_focus = st.toggle("Camera: Follow Steps", value=True, help="ON: Auto-zooms to new points.\nOFF: Static view.")

    with st.expander("📚 Math Syntax Guide"):
        st.markdown("""
        ℹ️ Trigonometric functions assume Radians.
        * **Power:** `x^2` or `x**2`
        * **Trig:** `cos(x)`, `sin(x)`, `tan(x)`
        * **Roots:** `sqrt(x)`
        * **Logs:** `log(x)` (natural), `exp(x)`
        * **Constants:** `pi`, `e`
        """)

    with st.expander("🛠️ Limits"):
        max_iter_input = st.number_input("Max Iterations:", value=100, step=10)
        decimals = st.slider("Decimals:", 0, 15, 6)

    col_btn1, col_btn2 = st.columns(2)
    
    if col_btn1.button("Initialize", type="primary", use_container_width=True):
        st.session_state.runtime_error = None
        is_valid, err_msg = validate_inputs(g_func_raw, x0_input, tol_input)
        
        if not is_valid:
            st.error(err_msg)
            st.session_state.initialized = False
        else:
            try:
                proc_func = process_math_input(g_func_raw)
                compile(proc_func, "<string>", "eval") 
                success, eng_msg = st.session_state.engine.initialize(proc_func, x0_input)
                if success:
                    st.session_state.initialized = True
                    st.session_state.history_df = pd.DataFrame([{"Iteration": 0, "Previous X": float(x0_input), "Current X": float(x0_input), "Error (%)": 0.0}])
                    st.toast(f"System Ready: x₀ = {x0_input}")
                else:
                    st.error(get_friendly_error_message(eng_msg))
                    st.session_state.initialized = False
            except Exception as e:
                st.error(get_friendly_error_message(e))
                st.session_state.initialized = False

    if col_btn2.button("Reset", use_container_width=True):
        st.session_state.history_df = pd.DataFrame(columns=["Iteration", "Previous X", "Current X", "Error (%)"])
        st.session_state.runtime_error = None
        st.session_state.initialized = False

    st.markdown("---")
    c1, c2 = st.columns(2)
    step_clicked = c1.button("Step ▶", disabled=not st.session_state.initialized, use_container_width=True)
    auto_clicked = c2.button("Run Auto ⏩", disabled=not st.session_state.initialized, use_container_width=True)

    if st.session_state.initialized:
        tol_val = float(tol_input) if tol_input else 1e-4
        
        if step_clicked:
            res = st.session_state.engine.step()
            if "error_msg" in res:
                st.session_state.runtime_error = get_friendly_error_message(res["error_msg"])
            else:
                st.session_state.runtime_error = None
                new_row = {"Iteration": int(res["step"]), "Previous X": res["x_in"], "Current X": res["x_out"], "Error (%)": res["error"]}
                st.session_state.history_df = pd.concat([st.session_state.history_df, pd.DataFrame([new_row])], ignore_index=True)

        if auto_clicked:
            results = st.session_state.engine.run_auto(tol_val, int(max_iter_input))
            new_rows = []
            st.session_state.runtime_error = None
            for res in results:
                if "error_msg" in res:
                    st.session_state.runtime_error = get_friendly_error_message(res["error_msg"])
                    break
                new_rows.append({"Iteration": int(res["step"]), "Previous X": res["x_in"], "Current X": res["x_out"], "Error (%)": res["error"]})
            
            if new_rows:
                st.session_state.history_df = pd.concat([st.session_state.history_df, pd.DataFrame(new_rows)], ignore_index=True)

st.title("🕸️ The Convergence Engine")


if st.session_state.initialized:
    if st.session_state.runtime_error:
        st.error(st.session_state.runtime_error)

    if len(st.session_state.history_df) > 0:
        last = st.session_state.history_df.iloc[-1]
        curr_x = last["Current X"]
        curr_err = last["Error (%)"]
        curr_iter = int(last["Iteration"])
        
        try: tol_val = float(tol_input)
        except: tol_val = 1e-4
        max_iter = int(max_iter_input)
        

        if curr_err < tol_val and curr_iter > 0:
            st.markdown(f'<div class="success-box">✅ Solution Converged<br><span style="font-size:0.9rem; opacity:0.8">Target reached at x = {curr_x:.{decimals}f}</span></div>', unsafe_allow_html=True)
        elif curr_iter >= max_iter:
            st.warning(f"⚠️ Max iterations ({max_iter}) reached without convergence.")


        k1, k2, k3 = st.columns(3)
        k1.markdown(f'<div class="stat-box"><div class="stat-label">Iteration</div><div class="stat-value">#{curr_iter}</div></div>', unsafe_allow_html=True)
        k2.markdown(f'<div class="stat-box"><div class="stat-label">Current X</div><div class="stat-value">{curr_x:.{decimals}f}</div></div>', unsafe_allow_html=True)
        

        err_style = "color: #EF553B;" if curr_err > tol_val else "color: #00CC96;"
        k3.markdown(f'<div class="stat-box"><div class="stat-label">Relative Error</div><div class="stat-value" style="{err_style}">{curr_err:.{decimals}f}%</div></div>', unsafe_allow_html=True)

        tab_plot, tab_data = st.tabs(["🕸️ Interactive Plot", "📋 Data Table"])

        with tab_plot:
            history = st.session_state.engine.history
            
            try: x_start = float(x0_input)
            except: x_start = 0.0

            try:
                x_next_pred = st.session_state.engine.g_func(x_start)
                if np.isnan(x_next_pred) or abs(x_next_pred) > 1e10: 
                    x_next_pred = x_start 
            except:
                x_next_pred = x_start

            static_points = [x_start, x_next_pred]
            sp_min, sp_max = min(static_points), max(static_points)
            sp_span = sp_max - sp_min
            
            if sp_span == 0: 
                sp_span = abs(sp_min) * 0.5 if sp_min != 0 else 2.0
            
            sp_buff = sp_span * 0.5
            static_range = [sp_min - sp_buff, sp_max + sp_buff]

            bg_limit = max(abs(sp_max), abs(sp_min), sp_span) * 50
            if bg_limit == 0: bg_limit = 100 

            x_bg = np.linspace(-bg_limit, bg_limit, 5000) 
            y_bg = []
            for v in x_bg:
                try:
                    r = st.session_state.engine.g_func(v)
                    if np.isnan(r) or np.iscomplex(r): y_bg.append(None)
                    else: y_bg.append(r)
                except: y_bg.append(None)

            fig = go.Figure()

            fig.add_trace(go.Scatter(x=[-bg_limit, bg_limit], y=[-bg_limit, bg_limit], mode='lines', name='y=x', 
                                     line=dict(color='#7F8C8D', dash='dash', width=2), hoverinfo='skip'))
            
            fig.add_trace(go.Scatter(x=x_bg, y=y_bg, mode='lines', name='g(x)', 
                                     line=dict(color='#00B4D8', width=3)))

            if show_cobweb and history:
                cx, cy = [], []
                sx = history[0][0]
                cx.append(sx); cy.append(sx)
                for px, nx in history:
                    cx.extend([px, px, nx, nx])
                    cy.extend([px, nx, nx, nx])
                fig.add_trace(go.Scatter(x=cx, y=cy, mode='lines+markers', name='Path', 
                                         line=dict(color='#F59E0B', width=2), 
                                         marker=dict(size=5, color='#F59E0B'))) 

            fig.add_trace(go.Scatter(x=[curr_x], y=[curr_x], mode='markers', name='Current', 
                                     marker=dict(size=14, color='#F72585', symbol='diamond', 
                                                 line=dict(color='white', width=2))))

            follow_points = []
            if history:
                recent = history[-5:] 
                follow_points += [p[0] for p in recent] + [p[1] for p in recent]
            follow_points.append(curr_x)
            if not history: follow_points.append(x_start)
            
            follow_points = [p for p in follow_points if -1e10 < p < 1e10]
            if not follow_points: follow_points = [x_start]
            
            fp_min, fp_max = min(follow_points), max(follow_points)
            fp_span = fp_max - fp_min
            if fp_span == 0: fp_span = abs(fp_min)*0.4 if fp_min!=0 else 1.0
            fp_buff = fp_span * 0.25
            smart_range = [fp_min - fp_buff, fp_max + fp_buff]

            if auto_focus:
                final_x = smart_range
                final_y = smart_range
                ui_rev = f"step_{curr_iter}" 
            else:
                final_x = static_range
                final_y = static_range
                ui_rev = "constant_view"

            fig.update_layout(
                height=500, 
                dragmode='pan',
                uirevision=ui_rev,
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    title="x", 
                    range=final_x,
                    zeroline=True, zerolinewidth=1.5, zerolinecolor='#9CA3AF',
                    gridcolor='rgba(128, 128, 128, 0.1)',
                    showgrid=True
                ),
                yaxis=dict(
                    title="g(x)", 
                    range=final_y,
                    zeroline=True, zerolinewidth=1.5, zerolinecolor='#9CA3AF',
                    gridcolor='rgba(128, 128, 128, 0.1)',
                    showgrid=True
                ),
                margin=dict(l=20, r=20, t=30, b=20), 
                legend=dict(
                    x=0.01, y=0.99,
                    xanchor="left", yanchor="top",
                    bgcolor="rgba(128, 128, 128, 0.2)",
                    bordercolor="rgba(128, 128, 128, 0.3)",
                    borderwidth=1
                )
            )
            st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': True})

        with tab_data:
            st.info(
                """
                ℹ️ **Note on Precision:** Calculations are performed using full floating-point precision (15+ digits). 
                The values below are **rounded** for readability. If you calculate the error manually using these rounded numbers, 
                your result may differ slightly from the computer's exact result.
                """
            )

            def highlight_success(row):
                try:
                    e = float(row['Error (%)'])
                    i = int(row['Iteration'])
                    if e < tol_val and i > 0:
                        return ['background-color: rgba(52, 211, 153, 0.25)'] * len(row)
                except: pass
                return [''] * len(row)

            fmt_dict = {
                "Previous X": f"{{:.{decimals}f}}",
                "Current X": f"{{:.{decimals}f}}",
                "Error (%)": f"{{:.{decimals}f}}" 
            }
            
            styled_df = st.session_state.history_df.style\
                .apply(highlight_success, axis=1)\
                .format(fmt_dict)
            
            st.dataframe(
                styled_df, 
                use_container_width=True, 
                hide_index=True
            )

else:
    st.markdown("### 👋 Welcome! Ready to converge?")
    st.markdown("Use the sidebar 👈 to configure your function, then click **Initialize**.")
    
    w1, w2, w3 = st.columns(3)
    with w1:
        st.markdown('<div class="landing-card"><span class="landing-icon">📈</span><div class="landing-title">Visualize</div><div class="landing-text">Explore fixed-point iteration with real-time, interactive Cobweb plots.</div></div>', unsafe_allow_html=True)
    with w2:
        st.markdown('<div class="landing-card"><span class="landing-icon">🔬</span><div class="landing-title">Analyze</div><div class="landing-text">Track relative error and convergence speed with precision.</div></div>', unsafe_allow_html=True)
    with w3:
        st.markdown('<div class="landing-card"><span class="landing-icon">🧪</span><div class="landing-title">Experiment</div><div class="landing-text">Test functions, initial guesses, and tolerances in a safe sandbox.</div></div>', unsafe_allow_html=True)