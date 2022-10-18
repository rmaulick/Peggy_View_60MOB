## To create a function that will create an MOB level view of PnL Output

from turtle import shape
from typing import final
import pandas as pd
import numpy as np
import xlwings as xl


def create_final_view_60MOB(final_pnl_df):
    pnl_data = final_pnl_df
    pnl_data["SCENARIO ID"] = pnl_data["SCENARIO ID"].str.replace(" ", "_")

    UNIQUE_SCENARIOS = np.unique(pnl_data["SCENARIO ID"])
    UNIQUE_SEGMENTS = np.unique(pnl_data["PAQ_UNIQUE"])

    variable_to_show = [
        "SCENARIO ID",
        "PAQ_UNIQUE",
        "MOB",
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
    
    for segment in UNIQUE_SEGMENTS:      
        for scenario in UNIQUE_SCENARIOS:
            print(scenario + " - For 60 MOB View")
            scenario_pnl_data = pnl_data[pnl_data["SCENARIO ID"] == scenario]
    
            scenario_pnl_data_temp = scenario_pnl_data.drop(['SCENARIO ID', 'PAQ_UNIQUE'], axis = 1)
            
            scenario_pnl_data_melt = scenario_pnl_data_temp.melt(id_vars = 'MOB', var_name = 'PnL_Metrics', value_name = 'PnL_Value').reset_index(drop=True)
            scenario_pnl_data_melt["MOB"] = "MOB" + scenario_pnl_data_melt["MOB"].astype(str)
        
            scenario_pnl_data_pivot = pd.pivot_table(scenario_pnl_data_melt, values = 'PnL_Value', index = 'PnL_Metrics', columns = 'MOB').reset_index()
            Column_order =["PnL_Metrics", "MOB1", "MOB2", "MOB3", "MOB4", "MOB5", "MOB6", "MOB7", "MOB8", "MOB9", "MOB10",
                        "MOB11", "MOB12", "MOB13", "MOB14", "MOB15", "MOB16", "MOB17", "MOB18", "MOB19", "MOB20",
                        "MOB21", "MOB22", "MOB23", "MOB24", "MOB25", "MOB26", "MOB27", "MOB28", "MOB29", "MOB30",
                        "MOB31", "MOB32", "MOB33", "MOB34", "MOB35", "MOB36", "MOB37", "MOB38", "MOB39", "MOB40",
                        "MOB41", "MOB42", "MOB43", "MOB44", "MOB45", "MOB46", "MOB47", "MOB48", "MOB49", "MOB50",
                        "MOB51", "MOB52", "MOB53", "MOB54", "MOB55", "MOB56", "MOB57", "MOB58", "MOB59", "MOB60"]
            
            scenario_pnl_data_pivot = scenario_pnl_data_pivot[Column_order]
        
            scenario_pnl_data_pivot["Year_1"] = scenario_pnl_data_pivot["MOB1"] + scenario_pnl_data_pivot["MOB2"] + scenario_pnl_data_pivot["MOB3"] + scenario_pnl_data_pivot["MOB4"] + scenario_pnl_data_pivot["MOB5"] + scenario_pnl_data_pivot["MOB6"] + scenario_pnl_data_pivot["MOB7"] + scenario_pnl_data_pivot["MOB8"] + scenario_pnl_data_pivot["MOB9"] + scenario_pnl_data_pivot["MOB10"] + scenario_pnl_data_pivot["MOB11"] + scenario_pnl_data_pivot["MOB12"]
            scenario_pnl_data_pivot["Year_2"] = scenario_pnl_data_pivot["MOB13"] + scenario_pnl_data_pivot["MOB14"] + scenario_pnl_data_pivot["MOB15"] + scenario_pnl_data_pivot["MOB16"] + scenario_pnl_data_pivot["MOB17"] + scenario_pnl_data_pivot["MOB18"] + scenario_pnl_data_pivot["MOB19"] + scenario_pnl_data_pivot["MOB20"] + scenario_pnl_data_pivot["MOB21"] + scenario_pnl_data_pivot["MOB22"] + scenario_pnl_data_pivot["MOB23"] + scenario_pnl_data_pivot["MOB24"]
            scenario_pnl_data_pivot["Year_3"] = scenario_pnl_data_pivot["MOB25"] + scenario_pnl_data_pivot["MOB26"] + scenario_pnl_data_pivot["MOB27"] + scenario_pnl_data_pivot["MOB28"] + scenario_pnl_data_pivot["MOB29"] + scenario_pnl_data_pivot["MOB30"] + scenario_pnl_data_pivot["MOB31"] + scenario_pnl_data_pivot["MOB32"] + scenario_pnl_data_pivot["MOB33"] + scenario_pnl_data_pivot["MOB34"] + scenario_pnl_data_pivot["MOB35"] + scenario_pnl_data_pivot["MOB36"]
            scenario_pnl_data_pivot["Year_4"] = scenario_pnl_data_pivot["MOB37"] + scenario_pnl_data_pivot["MOB38"] + scenario_pnl_data_pivot["MOB39"] + scenario_pnl_data_pivot["MOB40"] + scenario_pnl_data_pivot["MOB41"] + scenario_pnl_data_pivot["MOB42"] + scenario_pnl_data_pivot["MOB43"] + scenario_pnl_data_pivot["MOB44"] + scenario_pnl_data_pivot["MOB45"] + scenario_pnl_data_pivot["MOB46"] + scenario_pnl_data_pivot["MOB47"] + scenario_pnl_data_pivot["MOB48"]
            scenario_pnl_data_pivot["Year_5"] = scenario_pnl_data_pivot["MOB49"] + scenario_pnl_data_pivot["MOB50"] + scenario_pnl_data_pivot["MOB51"] + scenario_pnl_data_pivot["MOB52"] + scenario_pnl_data_pivot["MOB53"] + scenario_pnl_data_pivot["MOB54"] + scenario_pnl_data_pivot["MOB55"] + scenario_pnl_data_pivot["MOB56"] + scenario_pnl_data_pivot["MOB57"] + scenario_pnl_data_pivot["MOB58"] + scenario_pnl_data_pivot["MOB59"] + scenario_pnl_data_pivot["MOB60"]
            scenario_pnl_data_pivot["Total"] = scenario_pnl_data_pivot["Year_1"] + scenario_pnl_data_pivot["Year_2"] + scenario_pnl_data_pivot["Year_3"] + scenario_pnl_data_pivot["Year_4"] + scenario_pnl_data_pivot["Year_5"]
    
            wb = xl.Book("Input_UI_demo.xlsm")
            
            sheet_name = scenario
            
            try:
                ws1 = wb.sheets.add(name = sheet_name, after = "Final_View")
            except:
                wb.sheets(sheet_name).delete()
                ws1 = wb.sheets.add(name = sheet_name, after = "Final_View")
            
            ws1.range('A1').value = "Segment"
            ws1.range('B1').value = segment  
    
            ws1["A3"].options(pd.DataFrame, header=1, index=False, expand="table").value = scenario_pnl_data_pivot
        
    

