"""
Filename: maxpolygon.diagram._fraction_str.py
---
Author: TravisGK
Date: 20 July 2025

Description: This file contains a function which can take
             a decimal number of inches
             and return it as a string using fractions.
"""

def decimal_inches_to_fraction(inches, to_32th: bool=False) -> str:
    """ 
    Takes a number of inches and returns it as a str with fractions. 
    
    Params:
        - inches (number): the number of inches.
        - to_32th (bool): if True, the fraction is rounded to the nearest 32nd.
                          otherwise, it's rounded to the nearest 16th.
    """
    # Unicode single-character fractions for common fractions
    # These are indexed by 32ths.
    FRACTIONS = {
        0: "",
        1: "¹⁄₃₂",
        2: "¹⁄₁₆",  # no single char, so superscript+subscript notation
        3: "³⁄₃₂",
        4: "⅛",
        5: "⁵⁄₃₂",
        6: "³⁄₁₆",
        7: "⁷⁄₃₂",
        8: "¼",
        9: "⁹⁄₃₂",
        10: "⁵⁄₁₆",
        11: "¹¹⁄₃₂",
        12: "⅜",
        13: "¹³⁄₃₂",
        14: "⁷⁄₁₆",
        15: "¹⁵⁄₃₂",
        16: "½",
        17: "¹⁷⁄₃₂",
        18: "⁹⁄₁₆",
        19: "¹⁹⁄₃₂",
        20: "⅝",
        21: "²¹⁄₃₂",
        22: "¹¹⁄₁₆",
        23: "²³⁄₃₂",
        24: "¾",
        25: "²⁵⁄₃₂",
        26: "¹³⁄₁₆",
        27: "²⁷⁄₃₂",
        28: "⅞",
        29: "²⁹⁄₃₂",
        30: "¹⁵⁄₁₆",
        31: "³¹⁄₃₂",
    }

    # 1) Initialize necessary variables.
    # Round to the nearest 1/16 or 1/32.
    whole = int(inches)
    frac = inches - whole
    denominator = 32 if to_32th else 16
    numerator = round(frac * denominator)

    # Fix the rounding overflow (e.g. 0.9999 rounds to 1).
    if numerator >= denominator:
        whole += 1  # numerator becomes 0.
        return str(whole)  # whole number only

    # 2) Construct the string.
    # Get the unicode fraction or fallback.
    if not to_32th:
        numerator = 2 * numerator  # doubled to use the right index.
    fraction_str = FRACTIONS.get(numerator, "")

    if whole == 0 and fraction_str != "":
        return fraction_str  # fraction number only
    else:
        return f"{whole}{fraction_str}"  # whole + fraction