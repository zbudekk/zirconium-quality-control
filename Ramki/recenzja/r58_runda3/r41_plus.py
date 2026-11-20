import re, sys
L = open(sys.argv[1], encoding='utf-8').read().split('\n')
for i, l in enumerate(L):
    if l.startswith('+') and not l.startswith('+++'):
        s = l.encode('ascii', 'replace').decode()
        print('%d: %s' % (i + 1, s[:int(sys.argv[2])]))