from collections import Counter, defaultdict
from random import Random
from time import perf_counter

from main import RAW_RECORDS, build_registry

records, _ = build_registry(RAW_RECORDS)

try:
    unique_records = {records[0]}
except TypeError as error:
    print("1) set(запись) ->",
          type(error).__name__ + ":", error)

variants = {
    "tuple(items)": {tuple(r.items()) for r in records},
    "frozenset(items)": {frozenset(r.items()) for r in records},
}

for name, values in variants.items():
    print(f"2) {name}: уникальных записей {len(values)}") 

by_field = Counter(r["field"] for r in records)
print("3) Counter:", dict(sorted(by_field.items())))

groups = defaultdict(list)
for record in records:
    groups[record["status"]].append(record["id"])
print("defaultdict:", {
    k: sorted(v) for k, v in sorted(groups.items())
})

pairs = defaultdict(float)
for record in records:
    pairs[(record["field"], record["status"])] += record["debit"]
print("4) сумма по парам (месторождение, статус):")
for key in sorted(pairs):
    print(f"{key[0]:<10} {key[1]:<14} {pairs[key]:>7.1f}")
print("сумма по парам:", round(sum(pairs.values()), 1),
      "| общая сумма:",
      round(sum(r["debit"] for r in records), 1))


rng = Random(42)

def make_rows(n):
    return [
        {"id": f"SK-{i:06d}", "debit": rng.random() * 100}
        for i in range(n)
    ]

def find_by_scan(rows, target):
    for row in rows:
        if row["id"] == target:
            return row
    return None

def time_queries(lookup, queries, passes=1, repeats=3):
    best = float("inf")

    for _ in range(repeats):
        start = perf_counter()

        for _ in range(passes):
            for target in queries:
                lookup(target)

        best = min(best, (perf_counter() - start) / passes)

    return best * 1000

print("N; перебор; индекс; ускорение")

for n in (100, 1000, 10000, 100000):
    rows = make_rows(n)
    index = {row["id"]: row for row in rows}
    queries = [
        rows[rng.randrange(n)]["id"]
        for _ in range(1000)
    ]
    scan_ms = time_queries(
        lambda target: find_by_scan(rows, target),
        queries
    )
    index_ms = time_queries(
        lambda target: index[target],
        queries,
        passes=50
    )
    print(
        f"{n}; {scan_ms:.2f}; "
        f"{index_ms:.3f}; "
        f"{scan_ms / index_ms:.0f}x"
    )
    