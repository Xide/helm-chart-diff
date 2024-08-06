import deepdiff
import argparse
import yaml
import tabulate

parser = argparse.ArgumentParser()
parser.add_argument('old')
parser.add_argument('new')
parser.add_argument('values')

args = parser.parse_args()

old = None
with open(args.old, 'r') as f:
    old = yaml.safe_load(f)
new = None
with open(args.new, 'r') as f:
    new = yaml.safe_load(f)

values = None
with open(args.values, 'r') as f:
    values = yaml.safe_load(f)

diff = deepdiff.DeepDiff(old, new)
print(diff)
results = []

if 'dictionary_item_added' in diff:
    for adds in diff['dictionary_item_added']:
        results += [['D', '+', adds, '', '', deepdiff.path.extract(new, adds)]]
if 'dictionary_item_removed' in diff:
    for dels in diff['dictionary_item_removed']:
        try:
            value = deepdiff.path.extract(values, dels)
        except KeyError:
            results += [['D', '-', dels, deepdiff.path.extract(old, dels), '', '']]
        else:
            results += [['W', '-', dels, deepdiff.path.extract(old, dels), value, '']]

if 'values_changed' in diff:
    for changek in diff['values_changed'].keys():
        change = diff['values_changed'][changek]
        try:
            value = deepdiff.path.extract(values, changek)
        except KeyError:
            results += [['D', '~', changek, change['old_value'], '', change['new_value']]]
        else:
            results += [['W', '~', changek, change['old_value'], value, change['new_value']]]

print(tabulate.tabulate(results, headers=['Level', 'Type', 'Path', 'Old', 'Yours', 'New']))
