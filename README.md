# cm-time

<p align="center">
  <a href="https://github.com/34j/cm-time/actions/workflows/ci.yml?query=branch%3Amain">
    <img src="https://img.shields.io/github/actions/workflow/status/34j/cm-time/ci.yml?branch=main&label=CI&logo=github&style=flat-square" alt="CI Status">
  </a>
  <a href="https://cm-time.readthedocs.io">
    <img src="https://img.shields.io/readthedocs/cm-time.svg?logo=read-the-docs&logoColor=fff&style=flat-square" alt="Documentation Status">
  </a>
  <a href="https://codecov.io/gh/34j/cm-time">
    <img src="https://img.shields.io/codecov/c/github/34j/cm-time.svg?logo=codecov&logoColor=fff&style=flat-square" alt="Test coverage percentage">
  </a>
</p>

A simple context manager and decorator for measuring execution time with `perf_counter()`.

**Documentation**: <https://cm-time.readthedocs.io>

**Source Code**: <https://github.com/34j/cm-time>

## Installation

```shell
pip install cm-time
```

## Usage

```python
from cm_time import timer

with timer() as t:
    pass

print(t.elapsed)
```

Output:

```text
Elapsed time: 0.000
0.0
```

```python
from cm_time import timer_wrapped


@timer_wrapped()
def foo():
    pass
```

Output:

```text
foo: Elapsed time: 0.000
```
