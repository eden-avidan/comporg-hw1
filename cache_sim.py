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


def print_all(config, trace):
    print("=== Config ===")
    for key, val in config.items():
        print(f"  {key}: {val}")
    print("\n=== Trace ===")
    for i, (addr, action) in enumerate(trace):
        print(f"  [{i}] addr={addr}  action={action}")


def main():
    parser = argparse.ArgumentParser(description="Cache Simulator")
    parser.add_argument("config_file", help="Cache configuration file (.txt)")
    parser.add_argument("trace_file", help="Memory access trace file (.txt)")
    parser.add_argument("output_file", help="Output file (.txt)")
    args = parser.parse_args()

    config = parse_config(args.config_file)
    trace = parse_trace(args.trace_file)

    print_all(config, trace)


if __name__ == "__main__":
    main()
