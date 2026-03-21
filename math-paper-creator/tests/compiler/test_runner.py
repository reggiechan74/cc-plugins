from meta_compiler.compiler.runner import generate_runner


def test_generate_runner_contains_check_call():
    script = generate_runner([], model_path="my_model.model.md")
    assert "check_document" in script
    assert "my_model.model.md" in script
    assert "strict=True" in script
    assert script.startswith("#!/usr/bin/env python3")


def test_generate_runner_is_valid_python():
    script = generate_runner([], model_path="test.model.md")
    compile(script, "<runner>", "exec")  # should not raise


def test_generate_runner_blocks_first_signature():
    """generate_runner takes blocks as first positional arg, model_path as keyword-only."""
    from meta_compiler.compiler.runner import generate_runner
    from meta_compiler.compiler.parser import parse_document

    source = '''
Some prose.

```python:fixture
W = ["alice", "bob"]
```

```python:validate
Set("W", description="workers")
```
'''
    blocks = parse_document(source)
    script = generate_runner(blocks, model_path="test.model.md")
    assert "test.model.md" in script
    assert "#!/usr/bin/env python3" in script
