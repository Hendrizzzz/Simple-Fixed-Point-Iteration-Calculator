Here is a professional User Guide for your application. You can include this in your project’s `README.md` file or simply use it to learn the new syntax.

---

# 🕸️ The Convergence Engine: User Guide

## 1. Mathematical Syntax (The "Human" Way)

| Operation | Syntax to Type | Example |
| :--- | :--- | :--- |
| **Trigonometry** | `cos`, `sin`, `tan` | `cos(x)` |
| **Exponents** | `^` or `**` | `x^2 + 1` |
| **Square Root** | `sqrt` | `sqrt(x + 5)` |
| **Logarithm** | `log` (Natural Log), `exp` | `log(x)` |
| **Absolute Value** | `abs` | `abs(x - 2)` |
| **Constants** | `pi`, `e` | `x + pi` |
| **Arithmetic** | `+`, `-`, `*`, `/` | `(x + 1) / 2` |

### Examples:
*   **Simple:** `cos(x)`
*   **Polynomial:** `(x^2 + 2) / 3`
*   **Complex:** `sqrt(2*x + 5)`

---

## 2. How to Run the Iteration

### Step 1: Configuration
1.  **Function g(x):** Enter your rearranged function. (Remember: for $f(x)=0$, rewrite it as $x = g(x)$).
2.  **Initial Guess ($x_0$):** Pick a starting number.
3.  **Tolerance:** How precise do you want the answer? (e.g., `0.0001`).
4.  **Max Iterations:** Stop automatically if it takes too long.
5.  **Click "Initialize / Reset":** This locks in your function and prepares the engine.

### Step 2: Execution
*   **Next Step:** Clicking this runs **one single iteration**. Use this to watch the "cobweb" form line-by-line.
*   **Run Auto:** Automatically runs iterations until the Tolerance is met or Max Iterations is reached.

---

## 3. Interactive Graph Controls (The Genius Features)
The graph is powered by Plotly and includes custom hotkeys for a seamless experience.

### Mouse Controls
*   **Scroll Wheel:** Zoom In / Zoom Out (smooth animation).
*   **Double Click:** Reset view to default.
*   **Hover:** See the exact $(x, y)$ coordinates of any point.


---

## 4. Understanding the Visuals

### The Graph (Cobweb Plot)
*   **Green Dashed Line ($y=x$):** This is the target. The solution lies exactly on this line.
*   **Cyan Curve ($g(x)$):** This is your function.
*   **Yellow Path:** The path of the iteration.
    *   Vertical line = Calculating new value.
    *   Horizontal line = Updating $x$ for the next step.
    *   **Spiral:** Indicates the answer is oscillating (overshooting).
    *   **Staircase:** Indicates direct approach to the answer.
*   **Pink Dot:** The current value of $x$.

### The Data Table
*   **Green Highlight:** If a row is highlighted in green, that iteration met your **Tolerance** requirement. This is your converged solution.

---

## 5. Troubleshooting / Common Issues

**"The graph looks like a mess / is blank!"**
*   **Cause:** The function might be diverging (going to infinity).
*   **Fix:** Check your $g(x)$. If the slope $|g'(x)| \geq 1$ near the root, Fixed Point Iteration will naturally fail (diverge). Try a different arrangement of $g(x)$.

**"The buttons are disabled."**
*   **Fix:** You must click **"Initialize / Reset"** every time you change the function or the initial guess.

**"Hotkeys aren't working."**
*   **Fix:** Click anywhere on the dark background of the app (outside the text inputs) to give the page focus, then try pressing **Z** or **H** again.