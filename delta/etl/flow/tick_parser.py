import os
from collections import defaultdict
from datetime import datetime
import orjson as json

from glob import glob

import pandas as pd

from delta.config import DELTA_DB_PATH

date = datetime.now().strftime("%Y%m%d")
logs_path = os.path.join(DELTA_DB_PATH, date, "logs", "ebest_ticks.*.log")
paths = glob(logs_path)
sep = b" "

for path in paths:
    table = defaultdict(list)
    with open(path, "rb") as io:
        lines = io.readlines()
        for line in lines:
            topic, _, data = line.split(sep)
            # remove b' of topic = b"b'H1_"
            topic = topic[2:]
            topic = topic.decode("utf-8")
            table[topic].append(json.loads(data[:-2]))
    for key in table.keys():
        rows = table[key]
        df = pd.DataFrame(rows)
        path = os.path.join(DELTA_DB_PATH, date, "ticks", f"{key}.csv")
        if os.path.exists(path):
            df.to_csv(f"{key}.csv", index=False, mode="a", header=False)
        else:
            df.to_csv(f"{key}.csv", index=False, mode="w")

# add rows in table['H1_'] into parquet file
# import pyarrow as pa
# batch = pa.RecordBatch.from_pylist(mapping=table['H1_'])
# table = pa.Table.from_batches([batch])
# import pyarrow as pa
# import pyarrow.csv as csv
# import pyarrow.parquet as pq
# write_options = csv.WriteOptions()
# with pq.ParquetWriter('sample.parquet', table.schema) as out:
#     out.write_table(table, out)
#
# with pa.CompressedOutputStream("tips.csv.gz", "gzip") as out:
#     csv.write_csv(table, out)
