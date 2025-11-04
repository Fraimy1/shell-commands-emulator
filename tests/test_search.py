import pytest
from src.commands.search import Grep
from src.core.errors import ExecutionError
from .conftest import pc, strip_ansi

def test_grep_file(tmp_path, ctx, capsys):
    p = tmp_path / "g.txt"
    p.write_text("hello\nx\ny\nhello again\n")
    Grep().execute(pc("grep", pos=["hello", str(p)]), ctx)
    out = strip_ansi(capsys.readouterr().out)
    assert "g.txt:1:hello" in out
    assert "g.txt:4:hello again" in out

def test_grep_dir_requires_recursive(tmp_path, ctx):
    d = tmp_path / "gg"
    d.mkdir()
    (d / "f.txt").write_text("hello")
    with pytest.raises(ExecutionError):
        Grep().execute(pc("grep", pos=["hello", str(d)]), ctx)

def test_grep_case_insensitive(tmp_path, ctx, capsys):
    p = tmp_path / "ci.txt"
    p.write_text("Hello\nHELLO\nheLlo\nnone\n")
    Grep().execute(pc("grep", flags={"i"}, pos=["hello", str(p)]), ctx)
    out = strip_ansi(capsys.readouterr().out)
    assert "ci.txt:1:Hello" in out and "ci.txt:2:HELLO" in out and "ci.txt:3:heLlo" in out
