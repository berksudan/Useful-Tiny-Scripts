import re
import sys
import readline

BACK_CYAN = "\x1b[46m"  # Taken from the Back.CYAN of the Colorama package
BACK_YELLOW = "\x1b[43m"  # Taken from the Back.YELLOW of the Colorama package
FORE_BLACK = "\x1b[30m"  # Taken from the Fore.BLACK of the Colorama package
FORE_MAGENTA = "\x1b[35m"  # Taken from the Fore.MAGENTA of the Colorama package
FORE_RED = "\x1b[31m"  # Taken from the Fore.RED of the Colorama package
FORE_YELLOW = "\x1b[33m"  # Taken from the Fore.YELLOW of the Colorama package
STYLE_RESET_ALL = "\x1b[0m"  # Taken from the Style.RESET_ALL of the Colorama package

def print_info(message):
    print(f"{FORE_YELLOW}[INFO] {message}{STYLE_RESET_ALL}")

def print_question(message,end=''):
    # The end='' parameter prevents a newline, similar to `echo -n` in Bash
    print(f"{FORE_MAGENTA}[QUESTION] {message}{STYLE_RESET_ALL}")

def print_error(message):
    print(f"\033[91m[ERROR] {message}{STYLE_RESET_ALL}")


def read_multiline_input():
    lines = []
    while True:
        try:
            line = input()
            lines.append(line)
        except EOFError:
            break
    return "\n".join(lines).strip()

def main():
    print_info("Welcome, let's replace variables in your text!")
    print_question(
        "Enter the text containing variables (e.g., {name}). "
        "When you're done, press Ctrl+D (LNX/Mac) or Ctrl+Z and Enter (Windows):",
        end='\n')
    
    # Read multiline text input
    entry = read_multiline_input()

    # Extract unique variables from the text
    variables = set(re.findall(r'\{(.*?)\}', entry))
    
    if not variables:
        print_error("No variables found in the text. Exiting...")
        return

    print('') # Add a new-line for appearance
    print_info('The text has been received successfully.')

    values = {}
    for var in variables:
        values[var] = input(f"> Please provide a value for {BACK_CYAN}{FORE_BLACK}'{var}'{STYLE_RESET_ALL}: ").strip()

    # Replace variables in the text
    result = entry.format(**values)
    
    print_info("Here is your completed text:")
    print(result)
    print_info("Success! All variables have been replaced. Goodbye!")

if __name__ == "__main__":
    main()
