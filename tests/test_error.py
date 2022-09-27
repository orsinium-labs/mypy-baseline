from mypy_baseline._config import Config
from mypy_baseline._error import Error


LINE1 = 'my_project/api/views.py:69: \x1b[1m\x1b[31merror:\x1b[m\x0f Incompatible types in assignment (expression has type \x1b[m\x0f\x1b[1m"List[Type[RawRenderer]]"\x1b[m\x0f, base class \x1b[m\x0f\x1b[1m"BaseAPI"\x1b[m\x0f defined the type as \x1b[m\x0f\x1b[1m"Tuple[Any, Type[RawRenderer]]"\x1b[m\x0f)  \x1b[m\x0f\x1b[33m[assignment]\x1b[m\x0f\r\n'  # noqa
LINE1EXP = 'my_project/api/views.py:0: error: Incompatible types in assignment (expression has type "List[Type[RawRenderer]]", base class "BaseAPI" defined the type as "Tuple[Any, Type[RawRenderer]]")  [assignment]'  # noqa


def test_line1_parse():
    e = Error.new(LINE1)
    assert e is not None
    assert e.path.parts == ('my_project', 'api', 'views.py')
    assert e.line_number == 69
    assert e.severity == 'error'
    assert e.message.startswith('Incompatible types in')
    assert e.category == 'assignment'
    assert e.get_clean_line(Config()) == LINE1EXP


LINE2 = 'my_project/api/views.py:0: note: This violates the Liskov substitution principle\r\n'  # noqa
LINE2EXP = 'my_project/api/views.py:0: note: This violates the Liskov substitution principle'  # noqa


def test_line2_parse():
    e = Error.new(LINE2)
    assert e is not None
    assert e.path.parts == ('my_project', 'api', 'views.py')
    assert e.line_number == 0
    assert e.severity == 'note'
    assert e.message == 'This violates the Liskov substitution principle'
    assert e.category == 'note'
    assert e.get_clean_line(Config()) == LINE2EXP
