import argparse


CONFIG_KEYS = [
    "CACHE_LINE_SIZE",
    "CACHE_INCLUSIVE",
    "L1_NUM_WAYS",
    "L1_DATA_SIZE",
    "L2_NUM_WAYS",
    "L2_DATA_SIZE",
]


def parse_config(path):
    with open(path) as f:
        raw = f.read().replace(",", " ").split()
    parsed = []
    for i, val in enumerate(raw):
        if i == 1:
            parsed.append(val.upper() == "TRUE")
        else:
            parsed.append(int(val))
    return {key: val for key, val in zip(CONFIG_KEYS, parsed)}


def parse_trace(path):
    accesses = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            # format: <address> , <W/R>
            addr = parts[0]
            action = parts[2]
            accesses.append((addr, action))
    return accesses


class Cache:
    def __init__(self, num_ways, data_size, line_size):
        self.num_ways = num_ways
        self.data_size = data_size
        self.line_size = line_size
        self.num_sets = (data_size // line_size) // num_ways
        # ways[k][set_index] = [tag, lru_status]
        self.ways = [
            [[None, 0] for _ in range(self.num_sets)]
            for _ in range(num_ways)
        ]


def get_set_index(addr, cache):
    return (int(addr, 16) // cache.line_size) % cache.num_sets


def find_in_cache(cache, addr):
    set_idx = get_set_index(addr, cache)
    return any(way[set_idx][0] == addr for way in cache.ways)


def load_into_cache(cache, addr):
    """Returns the evicted address, or None if an empty slot was used."""
    set_idx = get_set_index(addr, cache)
    for way in cache.ways:
        if way[set_idx][0] is None:
            way[set_idx][0] = addr
            return None
    for way in cache.ways:
        if way[set_idx][1] == 0:
            evicted = way[set_idx][0]
            way[set_idx][0] = addr
            return evicted
    return None


def evict_from_cache(cache, addr):
    set_idx = get_set_index(addr, cache)
    for way in cache.ways:
        if way[set_idx][0] == addr:
            way[set_idx][0] = None
            way[set_idx][1] = 0
            return


def update_lru(cache, addr):
    set_idx = get_set_index(addr, cache)
    for way in cache.ways:
        if way[set_idx][0] == addr:
            way[set_idx][1] = cache.num_ways - 1
        elif way[set_idx][0] is not None and way[set_idx][1] > 0:
            way[set_idx][1] -= 1


def execute(addr, action, l1, l2, inclusive):
    if action == 'R':
        if find_in_cache(l1, addr):
            print("L1HIT")
            update_lru(l1, addr)
            return
        if find_in_cache(l2, addr):
            print("L2HIT")
            update_lru(l2, addr)
            load_into_cache(l1, addr)
            update_lru(l1, addr)
            return
        print("MEMACC")
        load_into_cache(l1, addr)
        update_lru(l1, addr)
        evicted = load_into_cache(l2, addr)
        update_lru(l2, addr)
        if inclusive and evicted and find_in_cache(l1, evicted):
            evict_from_cache(l1, evicted)

    elif action == 'W':
        if find_in_cache(l1, addr):
            print("L1HIT")
            update_lru(l1, addr)
            return
        if find_in_cache(l2, addr):
            print("L2HIT")
            update_lru(l2, addr)
            return
        print("MEMACC")


def main():
    parser = argparse.ArgumentParser(description="Cache Simulator")
    parser.add_argument("config_file", help="Cache configuration file (.txt)")
    parser.add_argument("trace_file", help="Memory access trace file (.txt)")
    parser.add_argument("output_file", help="Output file (.txt)")
    args = parser.parse_args()

    config = parse_config(args.config_file)
    trace = parse_trace(args.trace_file)

    line_size = config["CACHE_LINE_SIZE"]
    l1 = Cache(config["L1_NUM_WAYS"], config["L1_DATA_SIZE"], line_size)
    l2 = Cache(config["L2_NUM_WAYS"], config["L2_DATA_SIZE"], line_size)

    inclusive = config["CACHE_INCLUSIVE"]
    for addr, action in trace:
        execute(addr, action, l1, l2, inclusive)


if __name__ == "__main__":
    main()
