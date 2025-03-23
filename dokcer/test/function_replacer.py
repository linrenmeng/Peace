import re


def replace_function_in_file(file_path, class_name, func_name, new_signature_and_body):
    """
    Replace the function signature and body in a Python file based on the file path, class name, and function name,
    while maintaining consistent indentation.

    Args:
        file_path (str): The path to the Python file.
        class_name (str): The name of the class. If None, the function will be searched in the global scope.
        func_name (str): The name of the function to be replaced.
        new_signature_and_body (str): The new function signature and body.

    Returns:
        int: 1 if the replacement is successful, 0 otherwise.
    """
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Initialize variables
        inside_target_function = False
        func_start_line = None
        func_end_line = None
        func_indent = None
        class_indent = None

        # Compile the regular expression pattern for function matching
        func_pattern = re.compile(r'^\s*def\s+' + re.escape(func_name) + r'\s*\(.*\)\s*')

        # Iterate through each line in the file
        for i, line in enumerate(lines):
            if class_name:
                if f"class {class_name}" in line:
                    class_indent = len(line) - len(line.lstrip())
                    inside_target_function = False
                elif inside_target_function:
                    if line.strip() == '' or len(line) - len(line.lstrip()) <= func_indent:
                        func_end_line = i
                        break

            if func_pattern.match(line):
                if class_name:
                    if (len(line) - len(line.lstrip())) == class_indent + 4:
                        func_start_line = i
                        func_indent = len(line) - len(line.lstrip())
                        inside_target_function = True
                        continue
                else:
                    func_start_line = i
                    func_indent = len(line) - len(line.lstrip())
                    inside_target_function = True
                    continue

        # Find the end line of the function if the start line is found
        if inside_target_function and func_start_line is not None:
            for i in range(func_start_line + 1, len(lines)):
                line = lines[i]
                if len(line) - len(line.lstrip()) <= func_indent:
                    func_end_line = i
                    break

        # Replace the function if both start and end lines are found
        if func_start_line is not None and func_end_line is not None:
            indent = ' ' * func_indent
            new_func_lines = [indent + line if line.strip() else line for line in new_signature_and_body.split('\n')]
            lines = lines[:func_start_line] + new_func_lines + lines[func_end_line:]

            # Write the modified content back to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

            print(f"Function '{func_name}' has been replaced successfully in file '{file_path}'.")
            return 1
        else:
            print(f"Function '{func_name}' not found in the file '{file_path}'.")
            return 0
    except Exception as e:
        print(f"An error occurred while replacing the function in file '{file_path}': {e}")
        return 0


if __name__ == "__main__":
    # Example usage
    replace_function_in_file("your_file_path.py", "", "your_function_name", """
def your_function_name():
    # Function body
    pass
""")
