# Helm chart diff

Get a quick preview of the changes in an Helm chart `values.yaml` between versions.


Usage:

```
poetry run python main.py <CHART-REPO-URL> <CHART-NAME> -o <OLD-VERSION> -n <NEW-VERSION> [ -f <CURRENT-VALUES-FILE> ]

Example:
poetry run python main.py https://stakater.github.io/stakater-charts forecastle -o v1.0.98 -n v1.0.143 -f ./values.yaml
```


Sample output:
```
+---------+---------+---------------------------------+---------+---------------------------+--------------------------------+
| Level   | Type    | Path                            | Old     | Yours                     | New                            |
+=========+=========+=================================+=========+===========================+================================+
| DEBUG   | ADDED   | root['forecastle']['pod']       |         |                           | {'annotations': {}}            |
+---------+---------+---------------------------------+---------+---------------------------+--------------------------------+
| DEBUG   | ADDED   | root['forecastle']['container'] |         |                           | {'securityContext': {}}        |
+---------+---------+---------------------------------+---------+---------------------------+--------------------------------+
| DEBUG   | ADDED   | root['forecastle']['podDisrupti |         |                           | {}                             |
|         |         | onBudget']                      |         |                           |                                |
+---------+---------+---------------------------------+---------+---------------------------+--------------------------------+
| DEBUG   | ADDED   | root['forecastle']['networkPoli |         |                           | {'enabled': False, 'ingress':  |
|         |         | cy']                            |         |                           | {'enabled': False,             |
|         |         |                                 |         |                           | 'podSelector': {},             |
|         |         |                                 |         |                           | 'namespaceSelector': {}},      |
|         |         |                                 |         |                           | 'egress':                      |
|         |         |                                 |         |                           | {'denyExternalTraffic': False, |
|         |         |                                 |         |                           | 'apiServer':                   |
|         |         |                                 |         |                           | {'masterCidrBlock':            |
|         |         |                                 |         |                           | '127.0.0.1/32', 'masterPort':  |
|         |         |                                 |         |                           | 443}}}                         |
+---------+---------+---------------------------------+---------+---------------------------+--------------------------------+
| DEBUG   | ADDED   | root['forecastle']['deployment' |         |                           | {}                             |
|         |         | ]['podSecurityContext']         |         |                           |                                |
+---------+---------+---------------------------------+---------+---------------------------+--------------------------------+
| DEBUG   | ADDED   | root['forecastle']['openshiftOa |         |                           | {}                             |
|         |         | uthProxy']['securityContext']   |         |                           |                                |
+---------+---------+---------------------------------+---------+---------------------------+--------------------------------+
| DEBUG   | CHANGED | root['forecastle']['labels']['v | v1.0.98 |                           | v1.0.143                       |
|         |         | ersion']                        |         |                           |                                |
+---------+---------+---------------------------------+---------+---------------------------+--------------------------------+
| DEBUG   | CHANGED | root['forecastle']['image']['ta | v1.0.98 |                           | v1.0.143                       |
|         |         | g']                             |         |                           |                                |
+---------+---------+---------------------------------+---------+---------------------------+--------------------------------+
| INFO    | DELETED | root['forecastle']['config']['c |         | True                      |                                |
|         |         | rdEnabled']                     |         |                           |                                |
+---------+---------+---------------------------------+---------+---------------------------+--------------------------------+
```
