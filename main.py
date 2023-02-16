import argparse
from multiprocessing import Process
from typing import Any

from grammar_web_parser import PARSER_STORAGE
from utils import get_domain


def parsers_task(parser_obj: Any) -> None:
    """Task for parser object.

    Args:
        parser_obj (Any): parser object.
    """
    parser_obj().write_all()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Grammar websites content parser.")
    parser.add_argument("-u", "--url", help="Specify the single website url to parse.")
    parser.add_argument(
        "-p", "--parralel", action="store_true", help="Parralelize parsers execution."
    )

    args = parser.parse_args()

    if args.url:
        domain_name = get_domain(args.url)
        parse_obj = PARSER_STORAGE[domain_name]
        parse_obj().write_all()

    if not args.parralel:
        for parse_obj in PARSER_STORAGE.values():
            parse_obj().write_all()

    else:
        processes = []
        for parse_obj in PARSER_STORAGE.values():
            proc = Process(target=parsers_task, args=(parse_obj,))
            processes.append(proc)
            proc.start()

        for p in processes:
            p.join()
