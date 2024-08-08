import subprocess
import deepdiff
import argparse
import yaml
import tabulate
import logging
from enum import Enum
from itertools import chain

logger = logging.getLogger(__name__)


class ChangeKind(Enum):
    DELETED = 1
    CHANGED = 2
    ADDED = 3

    def __str__(self):
        return self.name


class ChangeLevel(Enum):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4

    def __str__(self):
        return self.name

class ValueChange:
    def __init__(self, level, kind: ChangeKind, key, old=None, current=None, new=None):
        self.level = level
        self.kind = kind
        self.key = key
        self.old = old
        self.current = current
        self.new = new

    def __repr__(self):
        return f"{self.level} {self.kind} {self.key}"

    def to_array_record(self):
        return [
            str(self.level),
            str(self.kind),
            self.key,
            "" if self.old is None else self.old,
            "" if self.current is None else self.current,
            "" if self.new is None else self.new,
        ]



class AddedChangesIterator:
    def __init__(self, diff, old, new, current=None):
        self.diff = diff
        self.old = old
        self.new = new
        self.current = current
        if "dictionary_item_added" in diff:
            self.data = diff["dictionary_item_added"]
        else:
            self.data = []
        self.index = 0

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        try:
            record = self.data[self.index]
            self.index += 1
            try:
                current = deepdiff.path.extract(self.current, record)
            except KeyError:
                current = None
            return ValueChange(
                ChangeLevel.DEBUG,
                ChangeKind.ADDED,
                record,
                None,
                current,
                deepdiff.path.extract(self.new, record),
            )
        except IndexError:
            raise StopIteration


class DeletedChangesIterator:
    def __init__(self, diff, old, new, current=None):
        self.diff = diff
        self.old = old
        self.new = new
        self.current = current
        if "dictionary_item_removed" in diff:
            self.data = diff["dictionary_item_removed"]
        else:
            self.data = []
        self.index = 0

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        try:
            record = self.data[self.index]
            self.index += 1
            try:
                current = deepdiff.path.extract(self.current, record)
            except KeyError:
                current = None
            return ValueChange(
                ChangeLevel.DEBUG if current is None else ChangeLevel.WARNING,
                ChangeKind.DELETED,
                record,
                deepdiff.path.extract(self.old, record),
                current,
                None,
            )
        except IndexError:
            raise StopIteration


class EditedChangesIterator:
    def __init__(self, diff, old, new, current=None):
        self.diff = diff
        self.old = old
        self.new = new
        self.current = current
        if "values_changed" in diff:
            self.data = list(diff["values_changed"].keys())
        else:
            self.data = []
        self.index = 0

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        try:
            record = self.data[self.index]
            self.index += 1
            try:
                current = deepdiff.path.extract(self.current, record)
            except KeyError:
                current = None
            return ValueChange(
                ChangeLevel.DEBUG if current is None else ChangeLevel.WARNING,
                ChangeKind.CHANGED,
                record,
                deepdiff.path.extract(self.old, record),
                current,
                deepdiff.path.extract(self.new, record),
            )
        except IndexError:
            raise StopIteration


class UnknownValuesIterator:
    def __init__(self, diff, current, new):
        self.diff = diff
        self.new = new
        self.current = current
        if "dictionary_item_removed" in diff:
            self.data = diff["dictionary_item_removed"]
        else:
            self.data = []
        self.index = 0

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        try:
            record = self.data[self.index]
            self.index += 1
            current = deepdiff.path.extract(self.current, record)
            return ValueChange(
                ChangeLevel.INFO, ChangeKind.DELETED, record, None, current, None
            )
        except IndexError:
            raise StopIteration


def fetch_chart_values(repo: str, chart: str, version: str):
    res = subprocess.run([
        "helm", "show", "values",
        "--repo", repo,
        chart,
        "--version", version
        ], capture_output=True, check=True)
    return res.stdout.decode('utf-8')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("repo")
    parser.add_argument("chart")
    parser.add_argument("-f", "--values-file", dest="values")
    parser.add_argument("-o", "--old-version", dest="oldv", required=True)
    parser.add_argument("-n", "--new-version", dest="newv", required=True)

    return parser.parse_args()

args = parse_args()


old = yaml.safe_load(fetch_chart_values(args.repo, args.chart, args.oldv))
new = yaml.safe_load(fetch_chart_values(args.repo, args.chart, args.newv))
values = None
if args.values is not None:
    with open(args.values, "r") as f:
        values = yaml.safe_load(f)

diff_old_new = deepdiff.DeepDiff(old, new)
diff_current_new = None
if values is not None:
    diff_current_new = deepdiff.DeepDiff(values, new)
changes = map(
    lambda x: x.to_array_record(),
    chain(
        AddedChangesIterator(diff_old_new, old, new, values),
        DeletedChangesIterator(diff_old_new, old, new, values),
        EditedChangesIterator(diff_old_new, old, new, values),
        UnknownValuesIterator(diff_current_new, values, new)
        if values is not None
        else [],
    ),
)
import os
maxw = os.get_terminal_size().columns // 5
print(tabulate.tabulate(changes, headers=['Level', 'Type', 'Path', 'Old', 'Yours', 'New'], tablefmt="grid", maxcolwidths=maxw))
