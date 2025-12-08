# Project Report: Simple Fixed-Point Iteration Method

## 1. Discussion of Theory

### 1.1 Background Information
The **Fixed-Point Iteration Method** (also known as Simple Fixed-Point Iteration or One-Point Iteration) is an open method used to find the real roots of a non-linear function $f(x) = 0$. The core idea is to algebraicly transform the original equation into the form:

$$ x = g(x) $$

where $g(x)$ is a function derived from $f(x)$. The method generates a sequence of approximations $\{x_n\}$ using the recurrence relation:

$$ x_{n+1} = g(x_n) $$

Starting with an initial guess $x_0$, the value is iteratively substituted back into the function until the sequence converges to a fixed point $r$, such that $r = g(r)$. This fixed point $r$ is also a root of the original equation $f(x) = 0$.

### 1.2 Derivation and Graphical Representation
Geometrically, the root of the equation lies at the intersection of two graphs:
1.  $y = x$ (the identity line)
2.  $y = g(x)$

The iteration process can be visualized using two distinct patterns depending on the slope of $g(x)$:
*   **Staircase Pattern**: Occurs when $g'(x)$ is positive. The line segment connecting $(x_n, g(x_n))$ to $(x_{n+1}, x_{n+1})$ moves in steps towards the intersection.
*   **Cobweb Pattern**: Occurs when $g'(x)$ is negative. The approximations oscillate around the root, creating a spiral or "cobweb" towards the intersection.

*(Note: Use the "Visualization" tab in the application to generate these plots for your presentation.)*

### 1.3 Convergence and Limitations
The method does not guarantee convergence for all functions $g(x)$ or initial guesses. The **Fixed-Point Theorem** states that the iteration converges if:

1.  $g(x)$ and $g'(x)$ are continuous on an interval containing the root.
2.  $|g'(x)| < 1$ for all $x$ in that interval.

**Limitations:**
*   **Divergence**: If $|g'(x)| > 1$, the errors grow with every iteration, and the method moves away from the root.
*   **Slow Convergence**: Even when it converges, it is generally slower (linear convergence) compared to methods like Newton-Raphson (quadratic convergence).
*   **Multiple Roots**: If a function has multiple roots, the specific fixed-point form $x = g(x)$ may only converge to one of them, depending on the slope near that root.

### 1.4 Importance and Applications
Despite its limitations, Fixed-Point Iteration is important because:
*   **Theoretical Foundation**: It serves as the basis for proving the existence and uniqueness of solutions to differential equations.
*   **Simplicity**: It is easy to program and understand, making it an excellent introduction to numerical methods.
*   **Self-Correction**: Small errors in calculation (except at the last step) do not prevent convergence, as the method is self-correcting.

---

## 2. Documentation of the Application

### 2.1 Detailed Algorithm
The application implements the Fixed-Point Iteration method using the following algorithm:

1.  **Input:**
    *   Read the transformed function $g(x)$.
    *   Read the initial guess $x_0$.
    *   Read the desired tolerance ($\epsilon_{tol}$) and maximum iterations ($K_{max}$).

2.  **Initialization:**
    *   Set current iteration $i = 0$.
    *   Set current error $\epsilon_a = \infty$.
    *   Set current approximation $x_{current} = x_0$.

3.  **Iteration Loop:**
    *   While $i < K_{max}$ and $\epsilon_a \ge \epsilon_{tol}$:
        1.  Store previous value: $x_{prev} = x_{current}$.
        2.  Calculate new value: $x_{current} = g(x_{prev})$.
        3.  Increment iteration: $i = i + 1$.
        4.  If $x_{current} \ne 0$:
            *   Calculate Absolute Relative Approximate Error:
                $$ \epsilon_a = \left| \frac{x_{current} - x_{prev}}{x_{current}} \right| \times 100\% $$
        5.  Record data (Iteration, $x_{prev}$, $x_{current}$, $\epsilon_a$).

4.  **Output:**
    *   Display the root approximation $x_{current}$.
    *   Display the number of iterations and final error.
    *   Generate the Cobweb/Staircase plot.

### 2.2 Sample Problem with Solution

**Problem:**
Find the real positive root of $f(x) = x^2 - x - 1 = 0$ using Fixed-Point Iteration method with $x_0 = 1.0$ and a tolerance of $5\%$.

**Manual Solution:**

1.  **Transform to $x = g(x)$**:
    From $x^2 - x - 1 = 0$, we can rewrite it as:
    $$ x^2 = x + 1 \implies x = \sqrt{x + 1} $$
    Here, $g(x) = \sqrt{x + 1}$.

2.  **Iteration 1:**
    $$ x_1 = g(x_0) = \sqrt{1.0 + 1} = \sqrt{2} \approx 1.414214 $$
    $$ \epsilon_a = |\frac{1.414214 - 1.0}{1.414214}| \times 100\% = 29.29\% $$

3.  **Iteration 2:**
    $$ x_2 = g(x_1) = \sqrt{1.414214 + 1} = \sqrt{2.414214} \approx 1.553774 $$
    $$ \epsilon_a = |\frac{1.553774 - 1.414214}{1.553774}| \times 100\% = 8.98\% $$

4.  **Iteration 3:**
    $$ x_3 = g(x_2) = \sqrt{1.553774 + 1} = \sqrt{2.553774} \approx 1.598053 $$
    $$ \epsilon_a = |\frac{1.598053 - 1.553774}{1.598053}| \times 100\% = 2.77\% $$

**Conclusion:**
Since $2.77\% < 5\%$, the process stops. The approximate root is **1.598053**.
*(Note: The true root is the Golden Ratio $\phi \approx 1.618033$)*

**Application Validation:**
Users can enter `np.sqrt(x + 1)` and `1.0` into the "The Convergence Engine" application to verify these exact results in the Data Table tab.
