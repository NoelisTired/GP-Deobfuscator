"""
Author: NoelP
Website: https://noelp.dev
Date: 6th October 2024 
Description: This script deobfuscates layers of obfuscated code by replacing 'exec' statements with 'print' statements and executing the modified code to reveal the next layer.
"""

import os
import sys
import subprocess
import tempfile
import base64
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

os.environ['PYTHONIOENCODING'] = 'utf-8'

class Deobfuscator:
    def __init__(self, initial_file, max_layers=100):
        self.initial_file = initial_file
        self.layer = 0
        self.max_layers = max_layers
        self.temp_dir = tempfile.TemporaryDirectory()

    def deobfuscate(self):
        file_path = self.initial_file

        while self.layer < self.max_layers:
            self.layer += 1  # Increment layer at the start
            print(f"\n--- Processing Layer {self.layer} ---")
            code = self._read_file(file_path)

            # Replace 'exec' with 'print' to reveal the next layer
            modified_code = code.replace('exec', 'print')

            # Execute the modified code to reveal the next layer
            revealed_code = self._execute_code(modified_code)

            # Add debugging information
            print(f"[Layer {self.layer}] Revealed Code:\n{revealed_code[:5]}\n")

            # Handle bytecode (byte string notation)
            revealed_code = self._handle_bytecode(revealed_code)

            # Decode Base64-encoded exec statements
            revealed_code = self._decode_base64_exec(revealed_code)

            print(f"Deobfuscation completed for layer {self.layer}")

            # Check if further transformations are possible
            if not self._contains_obfuscation(revealed_code):
                print(f"Final layer reached at layer {self.layer}.")
                final_output_path = os.path.join('final_output.py')
                with open(final_output_path, 'w', encoding='utf-8') as file:
                    file.write(revealed_code)
                print(f"Final output written to {final_output_path}")
                break  # Exit the loop since we've reached the final layer

            # Prepare for the next iteration
            file_path = self._prepare_next_layer(revealed_code)
        else:
            print(f"Maximum layer limit of {self.max_layers} reached. Exiting to prevent infinite loop.")

    def _read_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            sys.exit(1)

    def _execute_code(self, code):
        # Write the modified code to a temporary file
        temp_file_path = os.path.join(self.temp_dir.name, f'temp_exec_{self.layer}.py')
        try:
            with open(temp_file_path, 'w', encoding='utf-8') as temp_file:
                temp_file.write(code)
        except Exception as e:
            print(f"Error writing temporary file {temp_file_path}: {e}")
            sys.exit(1)

        # Execute the code and capture the output
        try:
            result = subprocess.run(
                [sys.executable, temp_file_path],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=10  # Prevent hanging
            )
            os.remove(temp_file_path)
            if result.stdout.strip():
                return result.stdout.strip()
            else:
                # If stdout is empty, return stderr (useful for certain obfuscated code)
                return result.stderr.strip()
        except subprocess.TimeoutExpired:
            print(f"Execution timed out for layer {self.layer}.")
            os.remove(temp_file_path)
            return ""
        except Exception as e:
            print(f"Error executing temporary file {temp_file_path}: {e}")
            os.remove(temp_file_path)
            return ""

    def _handle_bytecode(self, code):
        # Check if the code starts with a byte string notation
        if code.startswith(("b'", 'b"')):
            try:
                # Remove the leading 'b' and the surrounding quotes
                byte_str = code[2:-1]
                # Decode the byte string using 'unicode_escape'
                decoded_code = byte_str.encode('utf-8').decode('unicode_escape')
                print(f"Bytecode detected and decoded at layer {self.layer}.")
                return decoded_code
            except Exception as e:
                print(f"Error decoding bytecode at layer {self.layer}: {e}")
                return code  # Return the original code if decoding fails
        return code

    def _decode_base64_exec(self, code):
        # Function to decode Base64-encoded exec statements
        def replace_exec_b64(match):
            b64_encoded = match.group(2)
            try:
                decoded_bytes = base64.b64decode(b64_encoded)
                decoded_code = decoded_bytes.decode('utf-8')
                print(f"Decoded Base64 exec at layer {self.layer}.")
                return decoded_code
            except Exception as e:
                print(f"Error decoding Base64 at layer {self.layer}: {e}")
                return match.group(0)  # Return the original match if decoding fails

        # Pattern to find exec(base64.b64decode('...').decode("utf-8")) or exec(base64.b64decode("..."))
        pattern = r'import base64;exec\s*\(\s*base64\.b64decode\s*\(\s*([\'"])(.*?)\1\s*\)\s*(?:\.decode\s*\(\s*[\'"]utf-8[\'"]\s*\))?\s*\)'

        # Replace all occurrences with decoded code
        code = re.sub(pattern, replace_exec_b64, code, flags=re.DOTALL)

        return code

    def _contains_obfuscation(self, code):
        # Check if the code contains signs of obfuscation
        patterns = [
            r'exec\(',
            r'eval\(',
            r'base64\.b64decode\(',
            r'compile\(',
            r'__import__\(',
            r'import\s+base64'
        ]
        combined_pattern = '|'.join(patterns)
        return re.search(combined_pattern, code) is not None

    def _prepare_next_layer(self, code):
        # Write the revealed code to a temporary file for the next iteration
        temp_file_path = os.path.join(self.temp_dir.name, f'layer_{self.layer}_next.py')
        try:
            with open(temp_file_path, 'w', encoding='utf-8') as temp_file:
                temp_file.write(code)
            return temp_file_path
        except Exception as e:
            print(f"Error preparing next layer file {temp_file_path}: {e}")
            sys.exit(1)

    def cleanup(self):
        self.temp_dir.cleanup()

if __name__ == "__main__":
    initial_file = sys.argv[1] if len(sys.argv) > 1 else input("Enter the path to the initial file: ")
    deobfuscator = Deobfuscator(initial_file)
    try:
        deobfuscator.deobfuscate()
    finally:
        deobfuscator.cleanup()
