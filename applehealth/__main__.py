"""Allow running as `python -m applehealth`."""

from applehealth.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
