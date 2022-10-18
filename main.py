import pandas as pd
import numpy as np
import xlwings as xl
from datetime import datetime
import warnings
import math
import xlwings as xw

warnings.filterwarnings("ignore")

from input_ui import create_scenario_master
from preprocessing_demo import create_preprocess_pnl
from final_view_demo import create_final_view
from Final_View_60MOB import create_final_view_60MOB


full_data = create_preprocess_pnl()
# data = data[data['SCENARIO ID'] == 'Baseline']
full_data = full_data.fillna(0)
var_list = pd.read_csv("Full_edgemaster.csv")


full_data = full_data.rename(
    columns={
        "TAX RATE (%)": "Tax_Rate",
        "COST OF CAPITAL (%) (DISCOUNT RATE)": "Cost_of_Equity",
    }
)

# Run the SQL query and generate subrule outcomes
from pandasql import sqldf

mysql = lambda q: sqldf(q, globals())  # Standard Code

full_data["dollarnew1"] = 0

df_list = []


with open("airline_pnl_run_log.txt", "w") as fp:

    for scenario in np.unique(full_data["SCENARIO ID"]):
        data = full_data[full_data["SCENARIO ID"] == scenario].reset_index(drop=True)

        print("##########\n#     %s     #\n##########\n" % scenario)
        fp.write("##########\n#     %s     #\n##########\n" % scenario)

        for index, row in var_list.iterrows():
            if row["NODE_TYPE"] != "raw":
                fp.write("LOOKING AT: %s, %s \n" % (row["NODE_ID"], row["NODE"]))

                if str.lower(row["NODE"]) in data.columns.str.lower():
                    fp.write(
                        "Calculated Node: %s is already in the data\n\n" % (row["NODE"])
                    )
                else:
                    fp.write("Calculated Node: %s is NOT in the data\n" % (row["NODE"]))
                    fp.write(
                        "Calculated Node: %s  has formula: %s\n"
                        % (row["NODE"], row["FULL_SQL"])
                    )
                    if row["NODE"] == "PROFIT_SHARE":
                        fp.write("Looking at Special Case: PROFIT SHARE\n")
                        data["c_PBT_DLRS_per_ORIG"] = 0
                        data["c_OS_DLRS_per_ORIG"] = 0
                        data["c_profit_share"] = 0
                        data["c_PBT_DLRS_per_ORIG"] = (
                            data["c_PBT_DLRS_per_ORIG"] + data["PBT_DLRS_PER_ORIG"]
                        )
                        data["c_OS_DLRS_per_ORIG"] = (
                            data["c_OS_DLRS_per_ORIG"] + data["OS_DLRS_PER_ORIG"]
                        )

                        data["avg_c_OS_DLRS_per_ORIG"] = (
                            data["c_OS_DLRS_per_ORIG"] / data["MOB"]
                        )
                        data["Roo"] = (
                            data["c_PBT_DLRS_per_ORIG"] / data["avg_c_OS_DLRS_per_ORIG"]
                        ) / data["MOB"]

                        data["c_Change_in_LLR_DLRS_per_ORIG"] = 0
                        data["c_Change_in_LLR_DLRS_per_ORIG"] = (
                            data["c_Change_in_LLR_DLRS_per_ORIG"]
                            + data["Change_in_LLR_DLRS_per_ORIG"]
                        )
                        data["PBT_BFR_LLR"] = (
                            data["c_PBT_DLRS_per_ORIG"]
                            - data["c_Change_in_LLR_DLRS_per_ORIG"]
                        )
                        data["profit_share1"] = pd.Series(
                            np.where(
                                data["PBT_BFR_LLR"] > 0,
                                0.45 * data["PBT_BFR_LLR"],
                                np.nan,
                            )
                        )
                        data["l_profit_share1"] = data.groupby(
                            [
                                "SCENARIO ID",
                                "PAQ_UNIQUE",
                                "PRODUCT",
                                "CHANNEL",
                                "OFFER",
                                "FICO",
                                "PARTNER_SEGMENT",
                                "PAQ #",
                            ]
                        )["profit_share1"].shift(+1)
                        data["profit_share"] = data["profit_share1"] + (
                            data["l_profit_share1"] * -1
                        )
                        data = data.fillna(0)
                        fp.write(
                            "Calculated Node: %s has been added to data\n\n"
                            % (row["NODE"])
                        )
                    elif row["NODE"] == "DISCOUNTED_EC_DLRS_PER_ORIG":
                        # Change_in_EC_DLRS_per_ORIG / power((1+ Cost_of_Equity / 12), MOB)
                        data["c_Change_in_EC_DLRS_per_ORIG"] = data[
                            "CHANGE_IN_EC_DLRS_PER_ORIG"
                        ]
                        data["c_Cost_of_Equity"] = 1 + data["Cost_of_Equity"] / 12
                        data["c_pow_res"] = data.apply(
                            lambda r: math.pow(r["c_Cost_of_Equity"], r["MOB"]), axis=1
                        )
                        # data['c_pow_res']=data.apply(math.pow(data['c_Cost_of_Equity'],data['MOB']),axis=1)
                        data["DISCOUNTED_EC_DLRS_PER_ORIG"] = (
                            data["c_Change_in_EC_DLRS_per_ORIG"] / data["c_pow_res"]
                        )
                        fp.write(
                            "Calculated Node: %s has been added to data\n\n"
                            % (row["NODE"])
                        )

                    elif row["NODE"] == "PV_OF_PAT_DLRS_PER_ORIG":

                        # (PBT_DLRS_per_ORIG + ((-1) * profit_share) ) * (1- Tax_Rate)
                        # data['PAT_DLRS_PER_ORIG']=(data['PBT_DLRS_per_ORIG'] + ((-1) * data['profit_share']) ) * (1- data['Tax_Rate'])
                        data["c_PAT_DLRS_per_ORIG"] = data["PAT_DLRS_PER_ORIG"]
                        data["c_Cost_of_Equity"] = 1 + data["Cost_of_Equity"] / 12
                        data["c_pow_res"] = data.apply(
                            lambda r: math.pow(r["c_Cost_of_Equity"], r["MOB"]), axis=1
                        )
                        # data['c_pow_res']=data.apply(math.pow(data['c_Cost_of_Equity'],data['MOB']),axis=1)
                        data["PV_OF_PAT_DLRS_PER_ORIG"] = (
                            data["c_PAT_DLRS_per_ORIG"] / data["c_pow_res"]
                        )
                        fp.write(
                            "Calculated Node: %s has been added to data\n\n"
                            % (row["NODE"])
                        )
                    else:
                        # if row['NODE'] == 'CHANGE_IN_EC_DLRS_PER_ORIG':
                        #     l = np.sum(data['L_ECONOMIC_CAPITAL_DLRS_PER_ORIG'])
                        #     print('L_ECONOMIC_CAPITAL_DLRS_PER_ORIG has value: %s' % l)
                        #     ec = np.sum(data['ECONOMIC_CAPITAL_DLRS_PER_ORIG'])
                        #     print('ECONOMIC_CAPITAL_DLRS_PER_ORIG has value: %s' % ec)
                        #     print(l - ec)

                        data[row["NODE"]] = mysql(row["FULL_SQL"])[row["NODE"]]
                        if str.lower(row["NODE"]) in data.columns.str.lower():
                            fp.write(
                                "Calculated Node: %s has been added to data\n\n"
                                % (row["NODE"])
                            )

        data = data.reset_index(drop=True)
        df_list.append(data)

final_df = pd.concat(df_list, axis=0).reset_index(drop=True)

wb = xw.Book("Input_UI_demo.xlsm")

ws3 = wb.sheets["PnL_Output"]
ws3["A1"].options(pd.DataFrame, header=1, index=True, expand="table").value = final_df

final_df.to_csv("testing_code2outcome.csv", index=0)
print("$" * 60)
print(final_df)
print("$" * 60)
final_view_df = create_final_view(final_df)
# print(final_view_df)

# print(final_view_df.head(10))

timestr = str(datetime.now().date())

final_view_df.to_csv("%s_final_view.csv" % timestr, index=False)


try:
    ws4 = wb.sheets.add(name = "Final_View", after = "Overlay")
except:
    wb.sheets("Final_View").delete()
    ws4 = wb.sheets.add(name = "Final_View", after = "Overlay")

#ws4 = wb.sheets["Final_View"]

ws4["A1"].options(
    pd.DataFrame, header=1, index=False, expand="table"
).value = final_view_df

create_final_view_60MOB(final_df)
