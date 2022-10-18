import numpy as np
import pandas as pd
import xlwings as xw


def create_scenario_master():

    xlsm_file = "Input_UI_Demo.xlsm"
    xw.Book(xlsm_file).set_mock_caller()
    xlsm = xw.Book.caller()

    seg_sheet = pd.read_excel("Input_UI_Demo.xlsm", sheet_name="Segment_Specific")
    mob_sheet = pd.read_excel("Input_UI_Demo.xlsm", sheet_name="MOB_&_Overlay_Combined")
    overlay_df = pd.read_excel(
        "Input_UI_Demo.xlsm", sheet_name="Overlay", skiprows=1, nrows=5
    ).iloc[:5, 1:18]

    seg_sheet["key"] = 0
    mob_sheet["key"] = 0

    final_df = seg_sheet.merge(mob_sheet, on="key", how="outer")
    final_df["Scenario ID"] = "Baseline"
    first_column = final_df.pop("Scenario ID")
    final_df.insert(0, "Scenario ID", first_column)

    ui_sheet = xlsm.sheets["Input_UI_V3"]

    user_df = ui_sheet.range("A2").options(pd.DataFrame, expand="table").value

    user_df = user_df.replace({np.nan: None})

    user_df = user_df.dropna(how="all")

    user_df = user_df[1:]

    user_df.reset_index(inplace=True)

    data = {"MOB": np.arange(1, 61)}
    dep_df = pd.DataFrame(data)
    dep_df.loc[:, "key"] = 0

    user_df = user_df.assign(key=[0] * len(user_df))

    user_df = user_df.merge(dep_df, on="key", how="outer")

    def yr(mob):
        if mob < 13:
            return "Y1"
        elif mob < 25:
            return "Y2"
        elif mob < 37:
            return "Y3"
        elif mob < 49:
            return "Y4"
        else:
            return "Y5"

    user_df["Year"] = user_df["MOB"].apply(yr)

    user_df = user_df.dropna(axis=1, how="all")

    overlay_df = overlay_df.replace(np.NaN, 1)

    possible_pcf_columns = [
        "Fed_Funds_Rate",
        "Prime_Assets_Only_Rate",
        "Revolver_Funding_Curve_Rate",
        "Transactor_0pct_Existing_Rate",
        "Transactor_0pct_New_Rate",
        "equity_rate",
        "Stress_Airline",
        "Stress_TAP",
        "Active_Accounts_PCT_per_ORIG",
        "Open_Accounts_PCT_per_ORIG",
        "Average_OS_DLRS_per_ACTV",
        "Sales_DLRS_per_ACTV",
        "On_Spend_PCT_per_ORIG",
        "First_Ever_PCT_per_ACTV",
        "Second_Ever_PCT_per_ACTV",
        "BT_Fee_DLRS_per_ACTV",
        "Fc_Fee_DLRS_per_ACTV",
        "Ca_Fee_DLRS_per_ACTV",
        "Late_Fees_Incident_PCT_per_ACTV",
        "Gross_Annual_Fees_DLRS_per_ACTV",
        "Reversed_Annual_Fees_DLRS_per_AC",
        "Check_Fees_DLRS_per_ACTV",
        "Other_Fees_DLRS_per_ACTV",
        "BT_Amt_DLRS_per_ACTV",
        "Check_DLRS_per_ACTV",
        "Cash_Advance_DLRS_per_ACTV",
        "Sac_Bal_PCT_per_ORIG",
        "Revolve_Rate_PCT_per_ORIG",
        "Chk_Bal_PCT_per_ORIG",
        "Cash_Bal_PCT_per_ORIG",
        "Bt_Bal_PCT_per_ORIG",
        "Penalty_Bal_PCT_per_ORIG",
        "Calc_Ncl_Dollar_Rate_PCT_per_OR",
        "reversal_dollar_rate",
    ]

    available_pcf_columns = [
        i for i in possible_pcf_columns if i in list(user_df.columns)
    ]

    yrs = [j for j in overlay_df["Project Curve Factor"]]
    pcfs = list(overlay_df.columns)[1:]

    for yr in yrs:
        for pcf in pcfs:
            for pcf_col in available_pcf_columns:
                user_df.loc[
                    (user_df["Year"] == yr) & (user_df[pcf_col] == pcf), pcf_col
                ] = overlay_df.loc[
                    (overlay_df["Project Curve Factor"] == yr), pcf
                ].iloc[
                    0
                ]

    for pcf_col in available_pcf_columns:
        user_df[pcf_col] = user_df[pcf_col].replace(np.NaN, 1)

    user_df.Year = user_df.Year.str.replace("Y", "")

    for pcf_col in available_pcf_columns:
        print(pcf_col)
        current_paq = user_df.PAQ_Unique.values[0]
        bool_series = final_df.PAQ_Unique == current_paq
        test_df = final_df[bool_series]
        base_col = test_df[pcf_col]
        user_df[pcf_col] = user_df[pcf_col] * base_col

    user_df = user_df.loc[:, ~user_df.columns.duplicated()]

    wb = xw.Book("Input_UI_Demo.xlsm")

    ws1 = wb.sheets["User_Assumptions"]
    ws1["A1"].options(
        pd.DataFrame, header=1, index=False, expand="table"
    ).value = user_df

    # for pcf_col in possible_pcf_columns:
    #     final_df[pcf_col] = final_df[pcf_col].replace(np.NaN, 1)

    for col in final_df.columns:
        if col not in user_df.columns:
            user_df[col] = final_df[col]

    final_df = pd.concat([final_df, user_df], axis=0)

    ws2 = wb.sheets["Input_Data_v2"]
    ws2["A1"].options(
        pd.DataFrame, header=1, index=False, expand="table"
    ).value = final_df

    return final_df
