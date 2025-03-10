import csv
import random
import pandas as pd
from auth import global_sign_in

# Alpha Setting
INSTRUMENTTYPE = "EQUITY"
REGION = "USA"
UNIVERSE = "TOP3000"
DELAY = 1
DECAY = 0
NEUTRALIZATION = "SUBINDUSTRY"
TRUNCATION = 0.01
PASTEURIZATION = "ON"
UNITHANDLING = "VERIFY"
NANHANDLING = "ON"
LANGUAGE = "FASTEXPR"
VISUALIZATION = False
# TESTPERIOD = "P2Y"

# Dataset Field
DATASET_FILED = "fundamental6"
DATASET_TYPE = "MATRIX"


def get_datafields(
    sess,
    instrument_type: str,
    region: str,
    delay: int,
    universe: str,
    dataset_filed: str,
    search: str = "",
):
    if len(search) == 0:
        print("search is empty")
        url_template = (
            "https://api.worldquantbrain.com/data-fields?"
            + f"&instrumentType={instrument_type}"
            + f"&region={region}&delay={str(delay)}&universe={universe}&dataset.id={dataset_filed}&limit=50"
            + "&offset={x}"
        )
        count = sess.get(url_template.format(x=0)).json()["count"]
    else:
        print("search is not empty")
        url_template = (
            "https://api.worldquantbrain.com/data-fields?"
            + f"&instrumentType={instrument_type}"
            + f"&region={region}&delay={str(delay)}&universe={universe}&limit=50"
            + f"&search={search}"
            + "&offset={x}"
        )
        count = 100

    datafields_list = []
    for x in range(0, count, 50):
        datafields = sess.get(url_template.format(x=x))
        datafields_list.append(datafields.json()["results"])

    datafields_list_flat = [item for sublist in datafields_list for item in sublist]

    datafields_df = pd.DataFrame(datafields_list_flat)
    return datafields_df


def create_alpha():
    datafields = get_datafields(
        SESS,
        instrument_type=INSTRUMENTTYPE,
        region=REGION,
        universe=UNIVERSE,
        delay=DELAY,
        dataset_filed=DATASET_FILED,
    )

    # 使用try-except块处理可能的键错误
    try:
        company_datafields = datafields[datafields["type"] == DATASET_TYPE][
            "id"
        ].tolist()
        print(f"Successfully retrieved {len(company_datafields)} company datafields")
    except KeyError as e:
        print(f"Error accessing datafields: {e}")
        print("Using backup fundamental fields instead")
        # 提供备用字段列表
        company_datafields = [
            "f1_totalassets",
            "f1_cashequivalents",
            "f1_totalrevenue",
            "f1_totalliabilities",
            "f1_netincome",
            "f2_ebit",
            "f2_ebitda",
            "f2_freecashflow",
            "f2_totaldebt",
        ]

    # 参照示例代码设置操作符和参数
    group_compare_op = ["group_rank", "group_zscore", "group_percentile"]
    ts_compare_op = ["ts_zscore", "ts_av_rank", "ts_av_zscore"]
    days = [120, 240]  # 回溯天数
    group = [
        "market",
        "industry",
        "sector",
        "densify(py13_h_f1_sector)",
        "densify(pv13_revere_company_total)",
        "densify(pv13_revere_key_sector_total)",
    ]

    # # 限制使用的字段数量，避免生成过多的alpha
    # max_fields = 10
    # if len(company_datafields) > max_fields:
    #     print(f"Limiting to {max_fields} fields to avoid generating too many alphas")
    #     company_datafields = company_datafields[:max_fields]

    alpha_expressions = []

    # 使用嵌套循环生成所有可能的组合
    for gco in group_compare_op:
        for tco in ts_compare_op:
            for cf in company_datafields:
                for d in days:
                    for grp in group:
                        alpha_expression = f"{gco}({tco}({cf}, {d}), {grp})"
                        alpha_expressions.append(alpha_expression)

    print(f"there are total {len(alpha_expressions)} alpha expressions")
    alpha_list = []

    for alpha_expression in alpha_expressions:
        simulation_data = {
            "type": "REGULAR",
            "settings": {
                "instrumentType": INSTRUMENTTYPE,
                "region": REGION,
                "universe": UNIVERSE,
                "delay": DELAY,
                "decay": DECAY,
                "neutralization": NEUTRALIZATION,
                "truncation": TRUNCATION,
                "pasteurization": PASTEURIZATION,
                "unitHandling": UNITHANDLING,
                "nanHandling": NANHANDLING,
                "language": LANGUAGE,
                "visualization": VISUALIZATION,
            },
            "regular": alpha_expression,
        }
        alpha_list.append(simulation_data)

    random.shuffle(alpha_list)
    return alpha_list


if __name__ == "__main__":
    SESS = global_sign_in()
    ALPHA_LIST = create_alpha()

    with open("pending_simulated_list.csv", "w", newline="") as output_file:
        dict_writer = csv.DictWriter(
            output_file, fieldnames=["type", "settings", "regular"]
        )
        dict_writer.writeheader()
        dict_writer.writerows(ALPHA_LIST)
