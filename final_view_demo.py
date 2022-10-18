# THIS CODE IS TO CREATE YEAR_BY_YEAR FOR SOME VARIABLES.
# ALSO KNOWN AS PEGGY VIEW

from turtle import shape
from typing import final
import pandas as pd
import numpy as np


def create_final_view(final_pnl_df):
    # pnl_data = pd.read_csv('../Investigation/Python_60_MOB_PNL_airline_3.csv')
    pnl_data = final_pnl_df
    pnl_data["SCENARIO ID"] = pnl_data["SCENARIO ID"].str.replace(" ", "_")

    UNIQUE_SCENARIOS = np.unique(pnl_data["SCENARIO ID"])

    variable_to_show = [
        "SCENARIO ID",
        "YEAR",
        "PBT_DLRS_PER_ORIG",
        "TOTAL_INCOME",
        "NET_INTEREST_INCOME",
        "NET_INTEREST_MARGIN",
        "GROSS_FINANCE_CHARGE_YIELD",
        "CHARGE_OFF_REVERSALS",
        "NET_COST_OF_FUNDS_DLRS_PER_ORIG",
        "BT_FEE_DLRS_PER_ACTV",
        "NET_NON_INTEREST_INCOME",
        "TOTAL_RISK",
        "write_off",
        "Change_in_LLR_DLRS_per_ORIG",
        "TOTAL_OPEX",
        "REVSHARE_AEP_DLRS_PER_ORIG",
        "MARGINAL_OPEX_DLRS_PER_ORIG",
        "ACCOUNT_SETUP",
        "FRAUD_DLRS_PER_ORIG",
        "ACQUISITION_COST_DLRS_PER_ORIG",
    ]

    pnl_data = pnl_data[variable_to_show]

    df_list = []

    for scenario in UNIQUE_SCENARIOS:
        print(scenario)
        scenario_pnl_data = pnl_data[pnl_data["SCENARIO ID"] == scenario]
        grouped_pnl_data = (
            scenario_pnl_data.drop("SCENARIO ID", axis=1, inplace=False)
            .groupby("YEAR")
            .sum()
            .reset_index(drop=False)
        )
        grouped_pnl_data["SCENARIO ID"] = scenario

        pnl_pivot = pd.melt(
            grouped_pnl_data,
            id_vars=["SCENARIO ID", "YEAR"],
            value_vars=grouped_pnl_data.columns,
        ).reset_index(drop=True)

        subtotal = (
            pnl_pivot[["SCENARIO ID", "variable", "value"]]
            .groupby(["SCENARIO ID", "variable"])
            .sum()
            .reset_index(drop=False)
        )
        subtotal = subtotal.rename(columns={"value": "subtotal"}, inplace=False)

        vars = np.unique(pnl_pivot.variable)
        dfs = []

        for var in vars:
            var_df = pnl_pivot[pnl_pivot["variable"] == var]
            # subtotal_row = pd.DataFrame(
            #     {'SCENARIO ID': scenario,
            #     'YEAR': 'TOTAL',
            #     'variable': var,
            #     'value': subtotal[subtotal['variable'] == var]['subtotal'].values[0]},
            # )
            subtotal_row = {
                "SCENARIO ID": scenario,
                "YEAR": "%s TOTAL" % var,
                "variable": var,
                "value": subtotal[subtotal["variable"] == var]["subtotal"].values[0],
            }

            var_df = var_df.append(subtotal_row, ignore_index=True)
            dfs.append(var_df)
        pnl_pivot_2 = pd.concat(dfs, axis=0)

        # pnl_pivot_3 = pnl_pivot_2.pivot(index=['YEAR', 'variable'], columns='SCENARIO ID', values='value').reset_index(drop=False)
        # pnl_pivot_2 = pnl_pivot_2.sort_values(by=['variable', 'YEAR'])

        df_list.append(pnl_pivot_2.reset_index(drop=True))

    # pnl_pivot = pd.melt(pnl_data_years, id_vars=['SCENARIO ID', 'YEAR'], value_vars=pnl_data_years.columns)
    # pnl_pivot_2 = pnl_pivot.pivot(index=['YEAR', 'variable'], columns='SCENARIO ID', values='value').reset_index(drop=False)
    # pnl_pivot_2 = pnl_pivot_2.sort_values(by=['variable', 'YEAR'])

    final_df = pd.concat(df_list, axis=0).reset_index(drop=True)
    # print(final_df[final_df['SCENARIO ID'] != 'Baseline'].head(10))

    final_df.to_csv("before_pivot.csv", index=False)
    final_df = pd.read_csv("before_pivot.csv")
    final_df_2 = final_df.pivot(
        index=["YEAR", "variable"], columns="SCENARIO ID", values="value"
    ).reset_index()
    final_df_2.to_csv("after_pivot_on_py_script.csv", index=False)

    # print(final_df_2.head(10))
    # print(final_df_2.head(10))
    final_df_2.variable = pd.Categorical(
        final_df_2.variable, categories=variable_to_show
    )
    final_df_2 = final_df_2.sort_values(by=["variable", "YEAR"]).reset_index(drop=True)

    # final_df_2.Difference = pd.Series(np.where(final_df_2.YEAR.values not in (1,2,3,4,5), final_df_2.iloc[:, 3] - final_df_2.iloc[:, 2], np.nan))
    final_df_2.to_csv("PEGGY_VIEW.csv", index=False)
    return final_df_2


# pnl_pivot_2.to_csv('../Investigation/PEGGY_VIEW.csv', index=0)
