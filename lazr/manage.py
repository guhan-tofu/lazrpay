#!/usr/bin/env python
import os
import sys
# this is the main entry for manage commands
def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lazr.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("could not import django make sure it is installed and your env is active") from exc
    execute_from_command_line(sys.argv)
if __name__ == "__main__":
    main()
