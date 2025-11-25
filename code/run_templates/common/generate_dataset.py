import itertools
import os
import pathlib
import random
import tempfile
from csv import DictWriter

import numpy as np
from cosmotech.coal.cosmotech_api.apis.dataset import DatasetApi
from cosmotech.orchestrator.utils.logger import get_logger
from cosmotech.orchestrator.utils.logger import log_data
from faker import Faker

LOGGER = get_logger("Brewery/DatasetV5")

LOGGER.info("Generating dataset content")

ORG_ID = os.environ.get("CSM_ORGANIZATION_ID")
WS_ID = os.environ.get("CSM_WORKSPACE_ID")
RUNNER_ID = os.environ.get("CSM_RUNNER_ID")
RUN_ID = os.environ.get("CSM_RUN_ID")

fake_generator = Faker()
rng = np.random.default_rng(random.randint(500, 50000))

headers_customer = ["id", "Thirsty", "Satisfaction", "SurroundingSatisfaction"]
headers_bar = ["id", "Stock", "RestockQty", "NbWaiters"]
headers_bar_vertex = ["source", "target"]
headers_arc_satisfaction = ["source", "target"]

customer_content = []
bar_content = []
bar_vertex_content = []
arc_satisfaction_content = []

bars_name = ["MyBar"]
existing_names = set()
dup_counter = 0

for bar in bars_name:
    customers = list(fake_generator.name() for _ in range(random.randint(30, 150)))
    n_customers = len(customers)
    _stock = random.randint(30, 500)
    bar_content.append({
        "id": bar,
        "Stock": _stock,
        "RestockQty": random.randint(10, _stock),
        "NbWaiters": random.randint(1, n_customers // 2),
    })
    mask = np.random.randint(2, size=(n_customers, n_customers), dtype=bool)
    r_customer = []
    for i in range(n_customers):
        _name = customers[i]
        if _name in existing_names:
            _name = f"{_name} {dup_counter}"
            dup_counter += 1
        r_customer.append(_name)
        customer_content.append({
            "id": _name,
            "Thirsty": "false",
            "Satisfaction": 100,
            "SurroundingSatisfaction": 100
        })
        bar_vertex_content.append({
            "source": bar,
            "target": _name
        })

    for i, j in itertools.combinations(range(n_customers), 2):
        if mask[i][j] or mask[j][i]:
            arc_satisfaction_content.append({
                "source": r_customer[i],
                "target": r_customer[j],
            })
            arc_satisfaction_content.append({
                "source": r_customer[j],
                "target": r_customer[i],
            })

with tempfile.TemporaryDirectory(suffix="dataset") as temp_dir:
    temp_dir_path = pathlib.Path(temp_dir)
    for _name, _headers, _content in [
        ("Customer.csv", headers_customer, customer_content),
        ("Bar.csv", headers_bar, bar_content),
        ("Bar_vertex.csv", headers_bar_vertex, bar_vertex_content),
        ("arc_Satisfaction.csv", headers_arc_satisfaction, arc_satisfaction_content),
    ]:
        _path = temp_dir_path / _name
        with _path.open("w") as _file:
            _dw = DictWriter(_file, fieldnames=_headers)
            _dw.writeheader()
            _dw.writerows(_content)

    dataset_api = DatasetApi()

    dataset = dataset_api.upload_dataset(
        dataset_name = f"{RUNNER_ID} - {RUN_ID}",
        as_files=list(temp_dir_path.glob("*.csv"))
    )
    dataset_id = dataset.id

log_data("dataset_id", dataset_id)

LOGGER.info(f"Generated dataset {dataset_id}")
