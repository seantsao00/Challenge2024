import pstats
from pstats import SortKey

p = pstats.Stats('out.log')
p.strip_dirs().sort_stats(SortKey.TIME).print_stats(10)
