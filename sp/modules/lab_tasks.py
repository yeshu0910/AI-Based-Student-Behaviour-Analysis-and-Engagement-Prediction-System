"""
Laboratory Tasks for Python and C:
Task 1: Write a Program From Scratch
Task 2: Arrange Jumbled Code
Task 3: Fill in Missing Code
Task 4: Debug Incorrect Code
Task 5: Predict Program Output
"""

LAB_TASKS = {
    'python': {
        1: {
            'title': 'Task 1: Write a Program From Scratch',
            'type': 'scratch',
            'instructions': 'Write a Python program that accepts two numbers as input (separated by a space or newlines) and prints their sum.',
            'starter_code': '# Write your Python program below:\nnum1 = int(input())\nnum2 = int(input())\n# Compute and print the sum\n',
            'sample_input': '5\n10',
            'expected_output': '15',
            'solution_hint': 'Use print(num1 + num2)'
        },
        2: {
            'title': 'Task 2: Arrange Jumbled Code',
            'type': 'jumble',
            'instructions': 'The lines of code for computing the factorial of a number are jumbled. Arrange the lines in the correct sequential order to make the program work.',
            'jumbled_lines': [
                'n = 5',
                'fact = 1',
                'for i in range(1, n + 1):',
                '    fact = fact * i',
                'print(f"Factorial of {n} is {fact}")'
            ],
            'correct_order': [0, 1, 2, 3, 4],
            'starter_code': '# Arrange the code statements in logical execution order:\n# 1. fact = 1\n# 2. print(f"Factorial of {n} is {fact}")\n# 3. for i in range(1, n + 1):\n# 4. n = 5\n# 5. fact = fact * i\n\nn = 5\nfact = 1\nfor i in range(1, n + 1):\n    fact = fact * i\nprint(f"Factorial of {n} is {fact}")\n',
            'expected_output': 'Factorial of 5 is 120'
        },
        3: {
            'title': 'Task 3: Fill in Missing Code',
            'type': 'fill',
            'instructions': 'Fill in the blanks (marked with ____) to complete the function that checks if a given integer is even or odd.',
            'starter_code': 'def check_even_odd(number):\n    # Complete the condition to check if the number is even\n    if number % 2 == ____:\n        return "Even"\n    else:\n        return "____"\n\nprint(check_even_odd(14))\nprint(check_even_odd(7))\n',
            'expected_output': 'Even\nOdd',
            'solution_hint': 'Replace the first blank with 0 and the second blank with Odd.'
        },
        4: {
            'title': 'Task 4: Debug Incorrect Code',
            'type': 'debug',
            'instructions': 'The following code is intended to print all prime numbers between 2 and 10, but it contains syntax and logical bugs. Identify and fix the bugs.',
            'starter_code': 'primes = []\nfor num in range(2, 11):\n    is_prime = True\n    for i in range(2, num):\n        if (num % i = 0):\n            is_prime = False\n            break\n    if is_prime == True\n        primes.append(num)\nprint(primes)\n',
            'fixed_code': 'primes = []\nfor num in range(2, 11):\n    is_prime = True\n    for i in range(2, num):\n        if (num % i == 0):\n            is_prime = False\n            break\n    if is_prime == True:\n        primes.append(num)\nprint(primes)\n',
            'expected_output': '[2, 3, 5, 7]'
        },
        5: {
            'title': 'Task 5: Predict Program Output',
            'type': 'predict',
            'instructions': 'Carefully read the Python code snippet below. Mentally trace its execution and predict the exact console output.',
            'code_snippet': 'numbers = [1, 2, 3, 4, 5]\nresult = [x * 2 for x in numbers if x % 2 != 0]\nprint(result)\n',
            'options': [
                '[2, 4, 6, 8, 10]',
                '[2, 6, 10]',
                '[4, 8]',
                '[1, 3, 5]'
            ],
            'correct_option': '[2, 6, 10]',
            'explanation': 'The list comprehension filters odd numbers (1, 3, 5) and multiplies each by 2, resulting in [2, 6, 10].'
        }
    },
    'c': {
        1: {
            'title': 'Task 1: Write a Program From Scratch',
            'type': 'scratch',
            'instructions': 'Write a C program that accepts two integers from standard input and prints their sum.',
            'starter_code': '#include <stdio.h>\n\nint main() {\n    int a, b;\n    scanf("%d %d", &a, &b);\n    // Print the sum\n    printf("%d", a + b);\n    return 0;\n}\n',
            'sample_input': '12 8',
            'expected_output': '20',
            'solution_hint': 'Use printf("%d", a + b);'
        },
        2: {
            'title': 'Task 2: Arrange Jumbled Code',
            'type': 'jumble',
            'instructions': 'The statements of a simple C program to calculate the square of a number are jumbled. Reorder them into a valid, functioning C program.',
            'jumbled_lines': [
                '#include <stdio.h>',
                'int main() {',
                '    int x = 7;',
                '    int sq = x * x;',
                '    printf("Square: %d", sq);',
                '    return 0;',
                '}'
            ],
            'correct_order': [0, 1, 2, 3, 4, 5, 6],
            'starter_code': '#include <stdio.h>\n\nint main() {\n    int x = 7;\n    int sq = x * x;\n    printf("Square: %d", sq);\n    return 0;\n}\n',
            'expected_output': 'Square: 49'
        },
        3: {
            'title': 'Task 3: Fill in Missing Code',
            'type': 'fill',
            'instructions': 'Fill in the blanks (marked with ____) to complete the C program that finds the maximum of two numbers.',
            'starter_code': '#include <stdio.h>\n\nint main() {\n    int x = 25, y = 40;\n    int max;\n    if (x ____ y) {\n        max = x;\n    } else {\n        max = ____;\n    }\n    printf("Max: %d", max);\n    return 0;\n}\n',
            'expected_output': 'Max: 40',
            'solution_hint': 'Replace the first blank with > and the second blank with y.'
        },
        4: {
            'title': 'Task 4: Debug Incorrect Code',
            'type': 'debug',
            'instructions': 'The following C program is supposed to print numbers from 1 to 5, but contains loop and syntax bugs. Fix the bugs.',
            'starter_code': '#include <stdio.h>\n\nint main() {\n    int i;\n    for(i = 1; i <= 5; i++) {\n        print("%d ", i)\n    }\n    return 0;\n}\n',
            'fixed_code': '#include <stdio.h>\n\nint main() {\n    int i;\n    for(i = 1; i <= 5; i++) {\n        printf("%d ", i);\n    }\n    return 0;\n}\n',
            'expected_output': '1 2 3 4 5 '
        },
        5: {
            'title': 'Task 5: Predict Program Output',
            'type': 'predict',
            'instructions': 'Carefully inspect the C code snippet below and predict the output displayed on standard output.',
            'code_snippet': '#include <stdio.h>\n\nint main() {\n    int a = 10, b = 20;\n    int *p = &a;\n    *p = b;\n    printf("%d %d", a, b);\n    return 0;\n}\n',
            'options': [
                '10 20',
                '20 20',
                '20 10',
                'Runtime Error'
            ],
            'correct_option': '20 20',
            'explanation': 'Pointer p points to variable a. Setting *p = b assigns the value of b (20) to a, so both a and b are 20.'
        }
    }
}

