import sys
p = sys.argv[1]; a = int(sys.argv[2]); b = int(sys.argv[3]); w = int(sys.argv[4]) if len(sys.argv) > 4 else 700
with open(p, encoding='utf-8', errors='replace') as f:
    L = f.read().split('\n')
for i in range(a - 1, min(b, len(L))):
    s = L[i].rstrip('\r')
    print('%d: %s' % (i + 1, s[:w]))
print('-- total lines', len(L))