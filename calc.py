import math

# --- two-number helpers (kept for reuse) ---
def add(a, b): return a + b
def subtract(a, b): return a - b
def multiply(a, b): return a * b
def divide(a, b):
    if b == 0: return "Error: Division by zero"
    return a / b
def power(a, b): return a ** b
def modulus(a, b): return a % b

def square_root(a):
    if a < 0: return "Error: Negative number"
    return math.sqrt(a)

def factorial(a):
    if a < 0: return "Error: Negative number"
    return math.factorial(a)

# --- multi-number variants for 1–4 ---
def get_count(min_count=2):
    while True:
        try:
            count = int(input(f"How many numbers? (min {min_count}): ").strip())
            if count >= min_count:
                return count
            print(f"Please enter an integer >= {min_count}.")
        except ValueError:
            print("Invalid input. Please enter a whole number.")

def get_numbers(count):
    nums = []
    for i in range(count):
        while True:
            try:
                n = float(input(f"Enter number {i+1}: ").strip())
                nums.append(n)
                break
            except ValueError:
                print("Invalid input. Please enter a valid number.")
    return nums

def addition_list(nums): return sum(nums)
def subtraction_list(nums):
    result = nums[0]
    for n in nums[1:]: result -= n
    return result
def multiplication_list(nums):
    result = 1.0
    for n in nums: result *= n
    return result
def division_list(nums):
    result = nums[0]
    for n in nums[1:]:
        if n == 0: return "Error: Division by zero"
        result /= n
    return result

# --- simple helpers for trig mode ---
ANGLE_MODE = "rad"  # "rad" or "deg"

def maybe_to_radians(x):
    return math.radians(x) if ANGLE_MODE == "deg" else x

def apply_constant_with_number(const_val, const_name):
    """Prompt for a number and an operation with a constant (pi/e)."""
    try:
        x = float(input(f"Enter number x to combine with {const_name}: ").strip())
    except ValueError:
        print("Invalid number input.")
        return
    op = input("Choose operation with the constant (+, -, *, /, **): ").strip()
    if op not in {"+", "-", "*", "/", "**"}:
        print("Invalid operation.")
        return

    # For power, let user choose orientation
    if op == "**":
        orient = input("Power orientation: 1) x ** const  2) const ** x  (enter 1 or 2): ").strip()
        if orient == "1":
            print("Result:", x ** const_val)
        elif orient == "2":
            print("Result:", const_val ** x)
        else:
            print("Invalid choice.")
        return

    # Non-power operations are x op const
    try:
        if op == "+":  print("Result:", x + const_val)
        elif op == "-": print("Result:", x - const_val)
        elif op == "*": print("Result:", x * const_val)
        elif op == "/":
            if const_val == 0:
                print("Error: Division by zero")
            else:
                print("Result:", x / const_val)
    except Exception as e:
        print("Error:", e)

# --- main loop ---
def main():
    global ANGLE_MODE
    while True:
        print("\n=== Advanced Calculator ===")
        print("Basic ops (multi-number):")
        print(" 1. Addition (+)")
        print(" 2. Subtraction (-)")
        print(" 3. Multiplication (*)")
        print(" 4. Division (/)")
        print("Two-number ops:")
        print(" 5. Power (^)")
        print(" 6. Modulus (%)")
        print("Single-number ops:")
        print(" 7. Square Root")
        print(" 8. Factorial")
        print("Scientific (single-number unless noted):")
        print(" 9.  sin(x)          10. cos(x)          11. tan(x)")
        print("12. asin(x)         13. acos(x)         14. atan(x)")
        print("15. exp(x)          16. log(x) (ln)     17. log10(x)")
        print("18. floor(x)        19. ceil(x)         20. round(x, n)")
        print("Utilities:")
        print("21. Show constants (pi, e, tau)")
        print("22. Toggle angle mode (current: " + ANGLE_MODE + ")")
        print("23. Use π with a number")
        print("24. Use e with a number")
        print("Q. Quit")

        choice = input("Enter choice: ").strip().lower()

        if choice in {'q', 'quit', 'exit'}:
            print("Goodbye!")
            break

        # Multi-number basic ops
        if choice in {'1','2','3','4'}:
            count = get_count(min_count=2)
            nums = get_numbers(count)
            if choice == '1':
                print("Result:", addition_list(nums))
            elif choice == '2':
                print("Result:", subtraction_list(nums))
            elif choice == '3':
                print("Result:", multiplication_list(nums))
            else:
                print("Result:", division_list(nums))

        # Two-number ops
        elif choice in {'5','6'}:
            try:
                a = float(input("Enter first number: ").strip())
                b = float(input("Enter second number: ").strip())
            except ValueError:
                print("Invalid number input.")
                continue
            if choice == '5':
                print("Result:", power(a, b))
            else:
                print("Result:", modulus(a, b))

        # Single-number ops (sqrt, factorial)
        elif choice == '7':
            try:
                a = float(input("Enter number: ").strip())
                print("Result:", square_root(a))
            except ValueError:
                print("Invalid number input.")
        elif choice == '8':
            try:
                a = int(input("Enter number (integer): ").strip())
                print("Result:", factorial(a))
            except ValueError:
                print("Invalid integer input.")

        # Trig + scientific
        elif choice in {'9','10','11','12','13','14','15','16','17','18','19','20'}:
            # round(x, n) needs two inputs; others need one
            if choice == '20':
                try:
                    x = float(input("Enter x: ").strip())
                    n = int(input("Enter n (digits): ").strip())
                    print("Result:", round(x, n))
                except ValueError:
                    print("Invalid inputs.")
                continue

            try:
                x = float(input("Enter x: ").strip())
            except ValueError:
                print("Invalid number input.")
                continue

            # trig (respect angle mode for sin/cos/tan)
            if choice == '9':   # sin
                print("Result:", math.sin(maybe_to_radians(x)))
            elif choice == '10': # cos
                print("Result:", math.cos(maybe_to_radians(x)))
            elif choice == '11': # tan
                print("Result:", math.tan(maybe_to_radians(x)))
            # inverse trig (outputs in current angle mode)
            elif choice == '12': # asin
                if x < -1 or x > 1:
                    print("Error: domain for asin is [-1, 1]")
                else:
                    val = math.asin(x)
                    print("Result:", math.degrees(val) if ANGLE_MODE == "deg" else val)
            elif choice == '13': # acos
                if x < -1 or x > 1:
                    print("Error: domain for acos is [-1, 1]")
                else:
                    val = math.acos(x)
                    print("Result:", math.degrees(val) if ANGLE_MODE == "deg" else val)
            elif choice == '14': # atan
                val = math.atan(x)
                print("Result:", math.degrees(val) if ANGLE_MODE == "deg" else val)
            elif choice == '15': # exp
                print("Result:", math.exp(x))
            elif choice == '16': # log (natural)
                if x <= 0:
                    print("Error: log domain is (0, ∞)")
                else:
                    print("Result:", math.log(x))
            elif choice == '17': # log10
                if x <= 0:
                    print("Error: log10 domain is (0, ∞)")
                else:
                    print("Result:", math.log10(x))
            elif choice == '18': # floor
                print("Result:", math.floor(x))
            elif choice == '19': # ceil
                print("Result:", math.ceil(x))

        # Constants & angle modes & constants-with-number
        elif choice == '21':
            print(f"pi  = {math.pi}")
            print(f"e   = {math.e}")
            print(f"tau = {math.tau}")
        elif choice == '22':
            ANGLE_MODE = "deg" if ANGLE_MODE == "rad" else "rad"
            print("Angle mode set to:", ANGLE_MODE)
        elif choice == '23':
            apply_constant_with_number(math.pi, "π")
        elif choice == '24':
            apply_constant_with_number(math.e, "e")

        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
