from meta_compiler.compiler.codegen import generate_codebase
from meta_compiler.compiler.parser import parse_document
from meta_compiler.compiler.executor import execute_blocks


def test_codegen_produces_file_dict():
    """Code generator returns a dict of filename → content."""
    doc = '''
```python:validate
Set("W", description="Workers")
Set("P", description="Projects")
```

```python:validate
cap = Parameter("cap", index=["W"], units="hours", description="Capacity")
```

```python:validate
x = Variable("x", index=["W", "P"], domain="continuous",
             bounds=(0, 1), description="Allocation")
```
'''
    blocks = parse_document(doc)
    result = execute_blocks(blocks)
    files = generate_codebase(result.registry)

    assert "sets.py" in files
    assert "parameters.py" in files
    assert "variables.py" in files
    assert "__main__.py" in files
    assert "registry.py" in files


def test_codegen_sets_content():
    """sets.py contains Set declarations."""
    doc = '''
```python:validate
Set("W", description="Workers")
Set("P", description="Projects")
```
'''
    blocks = parse_document(doc)
    result = execute_blocks(blocks)
    files = generate_codebase(result.registry)

    assert 'Set("W"' in files["sets.py"]
    assert 'Set("P"' in files["sets.py"]
    assert "Workers" in files["sets.py"]


def test_codegen_parameters_content():
    """parameters.py contains Parameter declarations with all fields."""
    doc = '''
```python:validate
Set("W", description="Workers")
cap = Parameter("cap", index=["W"], domain="nonneg_real",
                units="hours", description="Maximum capacity")
```
'''
    blocks = parse_document(doc)
    result = execute_blocks(blocks)
    files = generate_codebase(result.registry)

    assert 'Parameter(' in files["parameters.py"]
    assert '"cap"' in files["parameters.py"]
    assert "nonneg_real" in files["parameters.py"]
    assert "hours" in files["parameters.py"]


def test_codegen_main_imports_all_modules():
    """__main__.py imports all modules in dependency order."""
    doc = '''
```python:validate
Set("W", description="Workers")
```
'''
    blocks = parse_document(doc)
    result = execute_blocks(blocks)
    files = generate_codebase(result.registry)

    main = files["__main__.py"]
    assert "import sets as model_sets" in main
    assert "import parameters as model_parameters" in main
    assert "import variables as model_variables" in main
    assert "import expressions as model_expressions" in main
    assert "import constraints as model_constraints" in main
    assert "import objectives as model_objectives" in main
    assert "run_tests" in main


def test_codegen_empty_module_still_generated():
    """Modules with no symbols are still generated (empty but valid)."""
    doc = '''
```python:validate
Set("W", description="Workers")
```
'''
    blocks = parse_document(doc)
    result = execute_blocks(blocks)
    files = generate_codebase(result.registry)

    assert "constraints.py" in files
