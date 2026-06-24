"""Demo voltage measurement helper for a TestStand-style workflow."""


def measure_voltage():
    """Return a simulated voltage reading."""
    return 12.1


if __name__ == "__main__":
    print(measure_voltage())
