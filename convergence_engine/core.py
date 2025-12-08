
import numpy as np

class IterationEngine:
    """
    Handles the mathematical logic and state of the Fixed Point Iteration.
    """
    def __init__(self):
        self.g_func = None
        self.g_str = ""
        self.previous_x = 0.0
        self.history = [] 
        self.step_count = 0
        self.error = None

    def initialize(self, g_expression, x0):
        """
        Parses the function and sets initial state.
        """
        try:
            context = {k: v for k, v in np.__dict__.items() if callable(v) or isinstance(v, (int, float, np.number))}
            context['np'] = np
            context['x'] = 0 # Test variable
            
            self.g_str = g_expression
            self.g_func = lambda x: eval(g_expression, {"__builtins__": {}}, {**context, 'x': x})
            
            self.g_func(float(x0))
            
            self.previous_x = float(x0)
            self.history = [(self.previous_x, 0)] # Start at (x0, 0)
            self.step_count = 0
            self.error = None
            return True, "Initialization Successful."
        except Exception as e:
            return False, f"Error parsing function: {e}"

    def step(self):
        """
        Performs one iteration step: x_{n+1} = g(x_n).
        Returns details for logging and plotting.
        """
        if not self.g_func:
            return None

        x_in = self.previous_x
        try:
            x_out = self.g_func(x_in)
        except Exception as e:
            return {"error": str(e)}

        if x_out != 0:
            self.error = abs((x_out - x_in) / x_out) * 100
        else:
            self.error = 0.0

        # p1 = (x_in, x_in) if self.step_count > 0 else (x_in, 0) 
        prev_pt = self.history[-1]
        pt_curve = (x_in, x_out)
        pt_diag = (x_out, x_out)
        
        self.history.append(pt_curve)
        self.history.append(pt_diag)
        
        self.previous_x = x_out
        self.step_count += 1
        
        return {
            "step": self.step_count,
            "x_in": x_in,
            "x_out": x_out,
            "error": self.error,
            "points": [prev_pt, pt_curve, pt_diag]
        }

    def run_auto(self, tolerance, max_iter):
        """
        Runs the iteration automatically until error < tolerance or max_iter reached.
        Returns a list of step data.
        """
        if not self.g_func:
            return None

        results = []
        
        while self.step_count < max_iter:
            step_data = self.step()
            if not step_data or "error" in step_data and isinstance(step_data["error"], str):
                 results.append(step_data)
                 break
            
            results.append(step_data)
            
            if step_data["error"] < tolerance:
                break
                
        return results

    def reset(self):
        self.g_func = None
        self.previous_x = 0.0
        self.history = []
        self.step_count = 0
        self.error = None
