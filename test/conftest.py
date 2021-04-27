"""Configuration file for pytest."""


def pytest_configure(config) -> None:
    """A configuration hook for pytest at this scope."""
    config.addinivalue_line(
        "markers",
        "unit: Run only unit tests.",
    )
