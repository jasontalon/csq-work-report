import argparse
import csv
from datetime import datetime
import os
from os.path import isfile, join


def execute_command(cmd) -> str:
    return os.popen(cmd).read()


def get_args():
    parser = argparse.ArgumentParser(description="Generates report of commits for Toolbox")

    subparsers = parser.add_subparsers(dest='command')

    create_report_subparser = subparsers.add_parser('create')

    create_report_subparser.add_argument("--targets"
                                         , type=str
                                         , nargs='+'
                                         , dest="target_dirs"
                                         , required=True
                                         , help="Specify target directory")

    create_report_subparser.add_argument("--author"
                                         , type=str
                                         , required=True
                                         , dest="author"
                                         , help="Specify author name")

    create_report_subparser.add_argument("--since"
                                         , type=int
                                         , default=31
                                         , dest="since"
                                         , help="Specify desired number of days since today. Default is 31 days")

    subparsers.add_parser('consolidate')

    return parser.parse_args()


def create_report(args, target_dir):
    cmd = f'cd {target_dir}'

    dir_name = execute_command(f'{cmd} && pwd')

    dir_name = dir_name[dir_name.rfind('/') + 1:].strip()

    log = f'git log --since="{args.since} days" --no-merges --author="{args.author}"'

    pretty = f'--pretty="format:%as\t{dir_name}\t%h\t%ae\t%s"'

    cmd = f'{cmd} && {log} {pretty}'

    res = execute_command(cmd)

    if len(res.splitlines()) == 0:
        print(f'no commits for {dir_name}')
        return

    return res.splitlines()


def create_reports(args):
    target_dirs = args.target_dirs

    lines = []

    for target_dir in target_dirs:
        result = create_report(args, target_dir)
        if result is None:
            continue
        lines.extend(result)

    lines.sort(key=lambda row: datetime.strptime(row.split("\t")[0], "%Y-%m-%d"), reverse=True)

    file_name = f'./reports/report.csv'

    os.makedirs(os.path.dirname(file_name), exist_ok=True)

    with open(file_name, 'w', encoding='UTF8') as file:
        writer = csv.writer(file)

        header = ['project', 'date', 'commit_id', 'author', 'subject']

        writer.writerow(header)

        for line in lines:
            writer.writerow(line.split("\t"))


def main():
    args = get_args()

    if args.command == 'create':
        create_reports(args)


if __name__ == "__main__":
    main()
