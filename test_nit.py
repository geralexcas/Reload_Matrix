def calculate_dv(nit):
    clean_nit = nit.replace(/[-\s]/g, '') # This is JS, fixing for python
    pass

def calculate_dv_py(nit):
    import re
    clean_nit = re.sub(r"[-\s.]", "", nit or "")
    weights = [71, 67, 59, 53, 47, 43, 41, 37, 29, 23, 19, 17, 13, 7, 3]
    reversed_digits = clean_nit[::-1]
    total = 0
    for i, digit in enumerate(reversed_digits):
        total += int(digit) * weights[i % len(weights)]
    remainder = total % 11
    if remainder == 0: return "0"
    if remainder == 1: return "K"
    return str(11 - remainder)

nit = "59827327"
dv = "0"
expected_dv = calculate_dv_py(nit)
print(f"NIT: {nit}, Expected DV: {expected_dv}, Provided DV: {dv}")
assert expected_dv == dv, f"Expected {expected_dv} but got {dv}"
