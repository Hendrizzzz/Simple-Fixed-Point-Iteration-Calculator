# The Convergence Engine: Fixed Point Iteration

A high-fidelity, interactive educational application for visualizing the Fixed Point Iteration method ($x_{n+1} = g(x_n)$). This tool is designed for students, educators, and math enthusiasts to explore convergence, divergence, and chaos in a modern, dark-themed environment.

## Features

*   **Dual Modes**:
    *   **Visualization Mode**: Interactive Cobweb/Staircase plots with Zoom and Pan capabilities.
    *   **Automatic Mode**: Batch calculation with customizable Tolerance and Max Iterations, displaying results in a scrollable Data Table.
*   **Dynamic Configuration**:
    *   Input any valid Python mathematical expression for $g(x)$ (e.g., `np.cos(x)`, `2.8*x*(1-x)`).
    *   Set Initial Guess ($x_0$).
*   **Modern UI**:
    *   Sleek Dark/Sci-Fi theme using `customtkinter`.
    *   Real-time system logging.
    *   Responsive layout with Sidebar and Tabs.

## Installation & Setup

Follow these steps to set up the application on a new computer.

### Prerequisites

*   **Python 3.8+**: Ensure Python is installed. You can download it from [python.org](https://www.python.org/).

### Step 1: Clone or Download

Clone this repository or download the source code to your local machine.

```bash
git clone <repository-url>
cd Simple-Fixed-Point-Iteration-Calculator
```

### Step 2: Create a Virtual Environment (Recommended)

It is good practice to use a virtual environment to manage dependencies.

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

Install the required Python libraries using `pip` and the provided `requirements.txt` file.

```bash
pip install -r requirements.txt
```

*Dependencies include: `customtkinter`, `matplotlib`, `numpy`.*

## Usage

### Running the App

Execute the main script to launch the application:

```bash
python convergence_engine.py
```

### How to Use

1.  **Configuration (Sidebar)**:
    *   **Function g(x)**: Enter your iteration function. Use `np` for NumPy functions (e.g., `np.cos(x)`, `np.exp(-x)`).
    *   **Initial Guess x0**: Enter the starting value.
    *   **Tolerance**: (For Auto Mode) Stop when relative error is below this value (default `0.0001`).
    *   **Max Iterations**: (For Auto Mode) Stop after this many steps (default `100`).

2.  **Visualization Mode**:
    *   Click **INITIALIZE** to prepare the graph.
    *   Click **NEXT STEP** repeatedly to see the cobweb plot form step-by-step.
    *   Use the **Toolbar** below the graph to Zoom or Pan.

3.  **Automatic Mode**:
    *   Click **RUN AUTO** to calculate the entire sequence instantly.
    *   The app will switch to the **Data Table** tab to show the results.

4.  **Reset**:
    *   Click **RESET** to clear all data and start over with a new function.

## Examples to Try

*   **Cosine Convergence**: `g(x) = np.cos(x)`, `x0 = 0.5`
*   **Logistic Map (Chaos)**: `g(x) = 3.8 * x * (1 - x)`, `x0 = 0.1`
*   **Divergence**: `g(x) = 2 * x`, `x0 = 1`