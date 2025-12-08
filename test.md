
### **Test Suite 1: Mathematical Logic & Syntax**
*Focus: Verifying the "Math Translator" and the Iteration Engine.*

| ID | Test Scenario | Inputs | Steps | Expected Result |
| :--- | :--- | :--- | :--- | :--- |
| **M01** | **Standard Convergence (Cosine)** | $g(x)$: `cos(x)`<br>$x_0$: `0.5`<br>Tol: `0.0001` | 1. Initialize.<br>2. Click "Run Auto". | System iterates ~30-40 times.<br>Final Value $\approx 0.739085$.<br>Green "Tolerance Met" box appears. |
| **M02** | **Power Syntax Translation** | $g(x)$: `x^2 - 0.5`<br>$x_0$: `0.5` | 1. Initialize (The engine should convert `^` to `**`).<br>2. Click "Next Step". | No syntax error.<br>Calculates $0.5^2 - 0.5 = -0.25$.<br>Graph plots correct parabola shape. |
| **M03** | **Trigonometry & Constants** | $g(x)$: `sin(x) + pi/4`<br>$x_0$: `0` | 1. Initialize. | No syntax error.<br>Recognizes `pi` as 3.14...<br>Calculates correctly. |
| **M04** | **Square Root Function** | $g(x)$: `sqrt(x+1)`<br>$x_0$: `1` | 1. Initialize.<br>2. Run Auto. | Converges to the Golden Ratio ($\approx 1.618$).<br>Graph shows curve starting from $x=-1$. |
| **M05** | **Natural Logarithm** | $g(x)$: `log(x) + 2`<br>$x_0$: `1` | 1. Initialize. | Recognizes `log` as natural log ($ln$).<br>Calculates values correctly. |
| **M06** | **Divergence (Explosion)** | $g(x)$: `2*x`<br>$x_0$: `1` | 1. Initialize.<br>2. Click "Next Step" 5 times. | Values double each time (1, 2, 4, 8, 16).<br>**Graph should not crash** (Code caps axis at 1e5).<br>Error % increases. |
| **M07** | **Oscillation (Never Converges)** | $g(x)$: `-x`<br>$x_0$: `1` | 1. Initialize.<br>2. Run Auto. | Values flip-flop: $1 \to -1 \to 1$.<br>Error remains constant (200%).<br>Iteration reaches "Max Iterations" and stops without green success box. |

---

### **Test Suite 2: Input Validation & Error Handling**
*Focus: Trying to break the app with bad data.*

| ID | Test Scenario | Inputs | Steps | Expected Result |
| :--- | :--- | :--- | :--- | :--- |
| **E01** | **Division by Zero** | $g(x)$: `1/x`<br>$x_0$: `0` | 1. Initialize. | **Graceful Failure.**<br>Red Error message: "float division by zero" or similar.<br>App should not crash/blank screen. |
| **E02** | **Complex Numbers (Negative Root)** | $g(x)$: `sqrt(x)`<br>$x_0$: `-5` | 1. Initialize. | **Graceful Failure.**<br>Error message regarding math domain or complex numbers.<br>Graph handles NaNs gracefully (skips plotting that point). |
| **E03** | **Invalid Syntax (Gibberish)** | $g(x)$: `hello_world`<br>$x_0$: `1` | 1. Initialize. | Error message: "name 'hello_world' is not defined".<br>Buttons remain disabled or revert to uninitialized state. |
| **E04** | **Empty Function Input** | $g(x)$: *(empty)* | 1. Initialize. | Error message asking for valid input.<br>System does not initialize. |
| **E05** | **Non-Numeric Initial Guess** | $x_0$: `abc` | 1. Initialize. | Error message: "could not convert string to float". |

---

### **Test Suite 3: User Interface & State**
*Focus: Layout, Buttons, and Data Persistence.*

| ID | Test Scenario | Steps | Expected Result |
| :--- | :--- | :--- | :--- |
| **U01** | **Initialization Logic** | 1. Load App.<br>2. Check "Next Step" button. | "Next Step" and "Run Auto" should be **Disabled** (greyed out) until "Initialize" is clicked. |
| **U02** | **Double Click Fix Verification** | 1. Enter valid function.<br>2. Click "Initialize" **ONCE**. | "Next Step" button becomes **Enabled** immediately.<br>Green Toast message appears: "System Initialized". |
| **U03** | **Reset Functionality** | 1. Run 10 iterations.<br>2. Click "Initialize / Reset". | Iteration count resets to 0.<br>Graph clears history (only shows $x_0$).<br>Table clears previous rows. |
| **U04** | **Decimal Precision Slider** | 1. Run Auto.<br>2. Move Slider from 6 to 2. | Table values update instantly (e.g., `0.123456` $\to$ `0.12`).<br>Top Metrics update instantly. |
| **U05** | **Continuing After Convergence** | 1. Run Auto (Convergence met).<br>2. Click "Next Step". | System allows user to continue iterating.<br>New rows are added to table.<br>Useful for checking stability. |

---

### **Test Suite 4: Data Table & Reporting**
*Focus: Pandas DataFrame and Styling.*

| ID | Test Scenario | Steps | Expected Result |
| :--- | :--- | :--- | :--- |
| **D01** | **Green Row Highlighting** | 1. Set Tolerance `0.1`.<br>2. Run iterations until Error < 0.1. | In the Data Table tab, the row where Error drops below 0.1 is highlighted in **Green**. |
| **D02** | **Data Accuracy** | 1. Calculate one step manually ($cos(0.5) \approx 0.877582$).<br>2. Check Table Row 1. | "Current X" in table matches manual calculation exactly. |
| **D03** | **Layout Consistency** | 1. Resize browser window (make it narrow). | Data table should scroll horizontally or resize without breaking the layout. |