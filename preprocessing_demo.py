# Import dependencies
import pandas as pd
import math
import numpy as np
import os
import warnings

warnings.filterwarnings("ignore")

from input_ui import create_scenario_master


def create_preprocess_pnl():

    # df_in= pd.read_excel('../data_in/Input_UI_Demo.xlsx', sheet_name='Input_Data_v2')
    df_in = create_scenario_master()

    df_in.columns = df_in.columns.str.upper()

    df_list = []

    for seg in np.unique(list(df_in["SCENARIO ID"])):

        print("Looking at scenario:", seg)

        df = df_in[df_in["SCENARIO ID"] == seg]
        print("df has shape", df.shape)

        # Create the preprocessed fields

        # L_First_Ever_PCT_per_ACTV
        df["L_First_Ever_PCT_per_ACTV"] = df.groupby(
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
        )["FIRST_EVER_PCT_PER_ACTV"].shift(-1)

        # L_Second_Ever_PCT_per_ACTV
        df["L_Second_Ever_PCT_per_ACTV"] = df.groupby(
            (
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
            )
        )["SECOND_EVER_PCT_PER_ACTV"].shift(-1)

        # OS_DLRS_PER_ORIG
        df["OS_DLRS_PER_ORIG"] = (
            df["AVERAGE_OS_DLRS_PER_ACTV"] * df["ACTIVE_ACCOUNTS_PCT_PER_ORIG"]
        )

        # ECONOMIC_CAPITAL_DLRS_PER_ORIG
        df["ECONOMIC_CAPITAL_DLRS_PER_ORIG"] = (
            df["OS_DLRS_PER_ORIG"] * df["BLENDED_CAPITAL_RATE_FINANCE"]
        )

        # L_ECONOMIC_CAPITAL_DLRS_PER_ORIG
        df["L_ECONOMIC_CAPITAL_DLRS_PER_ORIG"] = df.groupby(
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
        )["ECONOMIC_CAPITAL_DLRS_PER_ORIG"].shift(-1)

        # Bad_Dollar_CO_Net_DLRS_per_ORIG
        df["Bad_Dollar_CO_Net_DLRS_per_ORIG"] = (
            df["CALC_NCL_DOLLAR_RATE_PCT_PER_OR"] * df["OS_DLRS_PER_ORIG"]
        ) / 12

        # LLR
        # First convert Bad_Dollar_CO_Net_DLRS_per_ORIG into a list
        # print(df['Bad_Dollar_CO_Net_DLRS_per_ORIG'].shape)
        Bad_Dollar_CO_Net_DLRS_per_ORIG_values = list(
            df["Bad_Dollar_CO_Net_DLRS_per_ORIG"].values
        )
        # print(len(Bad_Dollar_CO_Net_DLRS_per_ORIG_values))

        # print(np.where(np.array(Bad_Dollar_CO_Net_DLRS_per_ORIG_values[1:-1]) == 0))

        for i in range(12):
            avg = np.average(Bad_Dollar_CO_Net_DLRS_per_ORIG_values[48:60])
            Bad_Dollar_CO_Net_DLRS_per_ORIG_values.append(avg * 0.925)

        # Adding MOB 73-84
        for i in range(12):
            avg = np.average(Bad_Dollar_CO_Net_DLRS_per_ORIG_values[60:72])
            Bad_Dollar_CO_Net_DLRS_per_ORIG_values.append(avg * 0.925)

        # Adding MOB 85-96
        for i in range(12):
            avg = np.average(Bad_Dollar_CO_Net_DLRS_per_ORIG_values[72:84])
            Bad_Dollar_CO_Net_DLRS_per_ORIG_values.append(avg * 0.925)

        # print('AFTER\n',Bad_Dollar_CO_Net_DLRS_per_ORIG_values)

        # df['Bad_Dollar_CO_Net_DLRS_per_ORIG'] = pd.Series(Bad_Dollar_CO_Net_DLRS_per_ORIG_values)
        # print(df['Bad_Dollar_CO_Net_DLRS_per_ORIG'].values)

        # with open('data_out/list.txt', 'w') as fp:
        #     for val in Bad_Dollar_CO_Net_DLRS_per_ORIG_values:
        #         # write each item on a new line
        #         fp.write("%s\n" % val)
        #     print('Done')

        LLR = []

        for i in range(0, 60):
            if i < 12:
                LLR.append(
                    np.sum(Bad_Dollar_CO_Net_DLRS_per_ORIG_values[i + 1 : i + 13])
                )
                # print('LLR_appended')

            elif i < 24:
                LLR.append(
                    np.sum(Bad_Dollar_CO_Net_DLRS_per_ORIG_values[i + 1 : i + 22])
                )
                # print('LLR_appended')

            elif i < 36:
                # print(Bad_Dollar_CO_Net_DLRS_per_ORIG_values[i+1:i+37])
                LLR.append(
                    np.sum(Bad_Dollar_CO_Net_DLRS_per_ORIG_values[i + 1 : i + 37])
                )
                # print(sum(df['Bad_Dollar_CO_Net_DLRS_per_ORIG'].values[i+1:i+36]))

            elif i < 48:
                LLR.append(
                    np.sum(Bad_Dollar_CO_Net_DLRS_per_ORIG_values[i + 1 : i + 31])
                )
                # print('LLR_appended')

            else:
                LLR.append(
                    np.sum(Bad_Dollar_CO_Net_DLRS_per_ORIG_values[i + 1 : i + 22])
                )
                # print('LLR_appended')

        s = pd.Series([i * -1 for i in LLR]).reset_index(drop=True)
        df = df.reset_index(drop=True)
        df["LLR"] = s
        # print(df.LLR)
        # df['LLR'] = pd.Series(LLR)
        # print(LLR)

        # L_LLR

        ####### HERE  #############
        df["L_LLR"] = df.groupby(
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
        )["LLR"].shift(+1)

        # Change_in_LLR_DLRS_per_ORIG

        df["Change_in_LLR_DLRS_per_ORIG"] = np.where(
            df.MOB == 1, df.LLR, df.LLR - df.L_LLR
        )

        ##### Write_Off #####

        print(
            "len of Bad_Dollar_CO_Net_DLRS_per_ORIG_values before truncating: ",
            len(Bad_Dollar_CO_Net_DLRS_per_ORIG_values),
        )

        Bad_Dollar_CO_Net_DLRS_per_ORIG_values = Bad_Dollar_CO_Net_DLRS_per_ORIG_values[
            0:60
        ]

        wowyn12m = 0.1
        wowyn18m = 0.3
        wowyn24m = 1.01
        wowyn36m = 1.08
        wowyn48m = 1.05
        wowyn60m = 1.11

        write_off = []

        print(
            "len of Bad_Dollar_CO_Net_DLRS_per_ORIG_values after truncating: ",
            len(Bad_Dollar_CO_Net_DLRS_per_ORIG_values),
        )

        for i in range(0, 60):
            if i < 12:
                write_off.append(Bad_Dollar_CO_Net_DLRS_per_ORIG_values[i] * wowyn12m)
                # print('LLR_appended')

            elif i < 18:
                write_off.append(Bad_Dollar_CO_Net_DLRS_per_ORIG_values[i] * wowyn18m)
                # print('LLR_appended')

            elif i < 24:
                write_off.append(
                    Bad_Dollar_CO_Net_DLRS_per_ORIG_values[i - 12] * wowyn24m
                )
                # print(sum(df['Bad_Dollar_CO_Net_DLRS_per_ORIG'].values[i+1:i+36]))

            elif i < 36:
                write_off.append(
                    Bad_Dollar_CO_Net_DLRS_per_ORIG_values[i - 12] * wowyn36m
                )
                # print('LLR_appended')

            elif i < 48:
                write_off.append(
                    Bad_Dollar_CO_Net_DLRS_per_ORIG_values[i - 12] * wowyn48m
                )
                # print('LLR_appended')

            elif i < 60:
                write_off.append(
                    Bad_Dollar_CO_Net_DLRS_per_ORIG_values[i - 12] * wowyn60m
                )

        df["write_off"] = pd.Series([i * -1 for i in write_off])

        df_list.append(df)

        print(seg, "Segment done")

    final_df = pd.concat(df_list, axis=0)
    return final_df

    # final_df.to_csv('../Investigation/processed_airline_segment.csv', index = False)
