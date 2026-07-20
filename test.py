import sympy as sp
import re

def latex_to_sympy_string(latex_str):
    """
    ממירה מחרוזת LaTeX בסיסית למחרוזת שפייתון ו-SymPy יכולים להבין ישירות.
    """
    # 1. ניקוי רווחים מיותרים וסמלים נפוצים
    s = latex_str.strip()
    s = s.replace(r'\cdot', '*')
    s = s.replace(r' ', '')
    
    # 2. טיפול בשברים מהצורה \frac{num}{den} -> (num)/(den)
    # משתמש בביטוי רגולרי כדי למצוא שברים בצורה רקורסיבית (תומך גם בשברים מקוננים)
    def replace_frac(match):
        return f"({match.group(1)})/({match.group(2)})"
    
    # מריץ את ההחלפה בלולאה כדי לטפל בשברים בתוך שברים
    prev_s = ""
    while prev_s != s:
        prev_s = s
        s = re.sub(r'\\frac\s*\{([^}]+)\}\s*\{([^}]+)\}', replace_frac, s)
    
    # 3. ניקוי סוגריים מסוג \left( ו-\right)
    s = s.replace(r'\left(', '(').replace(r'\right)', ')')
    s = s.replace(r'\left[', '[').replace(r'\right]', ']')
    s = s.replace('{', '(').replace('}', ')')
    
    # 4. הוספת סימן כפל משתמע עבור s (למשל 3s -> 3*s, או s(s+1) -> s*(s+1))
    s = re.sub(r'(\d)(s)', r'\1*\2', s)
    s = re.sub(r'(s)(\()', r'\1*\2', s)
    s = re.sub(r'(\))(\()', r'\1*\2', s)
    s = re.sub(r'(\))(\d)', r'\1*\2', s)
    s = re.sub(r'(\))([a-zA-Z])', r'\1*\2', s)
    
    return s

def extract_poles_and_zeros(latex_formula, frequency_var_str='s'):
    """
    מקבלת נוסחת אימפדנס בפורמט LaTeX, מנתחת אותה סימבולית,
    ומחזירה את הקטבים והאפסים בפורמט LaTeX עבור Desmos.
    """
    try:
        # המרת ה-LaTeX למחרוזת פייתון סטנדרטית
        sympy_friendly_str = latex_to_sympy_string(latex_formula)
        
        # יצירת המשתנה הסימבולי והערכת הביטוי
        freq_var = sp.Symbol(frequency_var_str)
        expr = sp.sympify(sympy_friendly_str)
        
        # פירוק לשבר ומציאת שורשים
        num, den = sp.fraction(sp.cancel(expr))
        
        zeros_set = sp.solve(num, freq_var)
        poles_set = sp.solve(den, freq_var)
        
        # פורמטינג חזרה ל-LaTeX
        zeros_latex = ", ".join([f"{frequency_var_str} = {sp.latex(z)}" for z in zeros_set]) if zeros_set else "None"
        poles_latex = ", ".join([f"{frequency_var_str} = {sp.latex(p)}" for p in poles_set]) if poles_set else "None"
        
        return {
            "zeros": zeros_latex,
            "poles": poles_latex
        }
        
    except Exception as e:
        return {"error": f"Failed to analyze formula: {str(e)}"}

# === בדיקה ===
if __name__ == "__main__":
    example_latex = r"\frac{s}{s^2 + 3 s + 2}"
    result = extract_poles_and_zeros(example_latex, frequency_var_str='s')
    print("Test 1 - Zeros (LaTeX):", result.get("zeros")) # צפוי: s = 0
    print("Test 1 - Poles (LaTeX):", result.get("poles")) # צפוי: s = -2, s = -1