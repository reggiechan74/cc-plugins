from meta_compiler.compiler.runner import generate_runner

def test_generate_runner_contains_check_call():
    script = generate_runner("my_model.model.md")
    assert "check_document" in script
    assert "my_model.model.md" in script
    assert "strict=True" in script
    assert script.startswith("#!/usr/bin/env python3")

def test_generate_runner_is_valid_python():
    script = generate_runner("test.model.md")
    compile(script, "<runner>", "exec")  # should not raise
