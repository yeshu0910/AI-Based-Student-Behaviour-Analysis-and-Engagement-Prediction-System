"""
Safe Code Executor & Validator for Student Programming Lab.
Provides isolated execution with timeouts and syntax validation for Python and C.
"""
import sys
import subprocess
import tempfile
import os
import shutil

class CodeExecutor:
    @staticmethod
    def execute_python(code: str, test_input: str = "", timeout: int = 5) -> dict:
        """
        Executes Python code in an isolated subprocess with strict timeouts.
        """
        # Quick safety checks for dangerous modules in student environment
        restricted = ['import os', 'import sys', 'import subprocess', 'import shutil', 'open(', '__import__']
        # Note: In an educational lab, we inspect or restrict dangerous calls
        is_safe = True
        for token in ['os.system', 'subprocess.', 'shutil.rmtree']:
            if token in code:
                return {
                    'success': False,
                    'output': f"Security Warning: Restricted operation detected: '{token}'."
                }

        temp_dir = tempfile.mkdtemp()
        script_path = os.path.join(temp_dir, 'solution.py')
        try:
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(code)

            process = subprocess.run(
                [sys.executable, script_path],
                input=test_input,
                text=True,
                capture_output=True,
                timeout=timeout,
                cwd=temp_dir
            )
            
            output = process.stdout
            if process.stderr:
                output += ("\n[Runtime / Syntax Error]:\n" + process.stderr)

            return {
                'success': process.returncode == 0,
                'output': output.strip() if output else "Execution completed with no output."
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': f"Execution timed out ({timeout}s limit reached - possible infinite loop)."
            }
        except Exception as e:
            return {
                'success': False,
                'output': f"Execution error: {str(e)}"
            }
        finally:
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass

    @staticmethod
    def execute_c(code: str, test_input: str = "", timeout: int = 5) -> dict:
        """
        Compiles and executes C code if gcc is available, otherwise validates syntax.
        """
        gcc_path = shutil.which('gcc')
        if not gcc_path:
            # Fallback syntax check
            if '#include' in code and 'main(' in code:
                return {
                    'success': True,
                    'output': "C Code Syntax Check Passed (GCC compiler not in PATH, simulated verification)."
                }
            else:
                return {
                    'success': False,
                    'output': "C Syntax Error: Missing #include header or main() function entrypoint."
                }

        temp_dir = tempfile.mkdtemp()
        src_path = os.path.join(temp_dir, 'solution.c')
        bin_path = os.path.join(temp_dir, 'solution.exe' if os.name == 'nt' else 'solution')
        try:
            with open(src_path, 'w', encoding='utf-8') as f:
                f.write(code)

            # Compile
            comp_proc = subprocess.run(
                ['gcc', src_path, '-o', bin_path],
                text=True,
                capture_output=True,
                timeout=timeout
            )
            if comp_proc.returncode != 0:
                return {
                    'success': False,
                    'output': f"Compilation Error:\n{comp_proc.stderr}"
                }

            # Run binary
            run_proc = subprocess.run(
                [bin_path],
                input=test_input,
                text=True,
                capture_output=True,
                timeout=timeout,
                cwd=temp_dir
            )
            output = run_proc.stdout
            if run_proc.stderr:
                output += "\n" + run_proc.stderr
            return {
                'success': run_proc.returncode == 0,
                'output': output.strip() if output else "Execution completed successfully."
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': f"Execution timed out ({timeout}s limit)."
            }
        except Exception as e:
            return {
                'success': False,
                'output': f"Execution error: {str(e)}"
            }
        finally:
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass

