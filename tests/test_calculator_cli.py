from aws_ebs_optimizer.calculator_cli import calculate, main


def test_calculate_addition():
    assert calculate(2, "+", 3) == 5


def test_calculate_division():
    assert calculate(10, "/", 4) == 2.5


def test_calculate_division_by_zero_raises():
    try:
        calculate(10, "/", 0)
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "Division by zero" in str(exc)


def test_main_prints_result(capsys):
    exit_code = main(["7", "*", "6"])
    out = capsys.readouterr().out.strip()
    assert exit_code == 0
    assert out == "42.0"
