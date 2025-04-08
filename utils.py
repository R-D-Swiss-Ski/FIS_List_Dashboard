import pandas as pd

def getMeanTopX_Int(df_season, disciplin, top):
    col_name = str(disciplin).lower() + 'pos'
    df_Int = df_season[df_season['nationcode'] != 'SUI']
    df_Int = df_Int.sort_values(by=col_name, ascending=True)
    df_Int = df_Int.head(top)
    mean_dhpos = df_Int[col_name].mean()
    return mean_dhpos

def getMeanTopX_SUI(df_season, disciplin, top):
    col_name = str(disciplin).lower() + 'pos'
    df_SUI = df_season[df_season['nationcode'] == 'SUI']
    df_SUI = df_SUI.sort_values(by=col_name, ascending=True)
    df_SUI = df_SUI.head(top)
    mean_dhpos = df_SUI[col_name].mean()
    return mean_dhpos

def getNoTopX_SUI(df_season, disciplin):
    col_name = str(disciplin).lower() + 'pos'
    df_season = df_season.sort_values(by=col_name, ascending=True)
    count_SUI_TOP30 = df_season.head(30)[df_season['nationcode'] == 'SUI'].shape[0]
    count_SUI_TOP50 = df_season.head(50)[df_season['nationcode'] == 'SUI'].shape[0]
    count_SUI_TOP70 = df_season.head(70)[df_season['nationcode'] == 'SUI'].shape[0]
    return count_SUI_TOP30, count_SUI_TOP50, count_SUI_TOP70

def collect_data(birthyear, FISYear, Gender, top, disciplin, combined_df):
    data = []
    for i in range(11):
        season = birthyear + 16 + FISYear
        df_season = combined_df[(combined_df['birthyear'] == birthyear) &
                                (combined_df['listyear'] == season) &
                                (combined_df['gender'] == Gender)]
        MeanInt = getMeanTopX_Int(df_season, disciplin, top)
        MeanSUI = getMeanTopX_SUI(df_season, disciplin, top)
        data.append({
            'birthyear': birthyear,
            'season': season,
            'meanint': MeanInt,
            'meansui': MeanSUI
        })
        birthyear += 1
    return pd.DataFrame(data)

def collect_data_No(birthyear, FISYear, Gender, disciplin, combined_df):
    data = []
    for i in range(11):
        season = birthyear + 16 + FISYear
        df_season = combined_df[(combined_df['birthyear'] == birthyear) &
                                (combined_df['listyear'] == season) &
                                (combined_df['gender'] == Gender)]
        SUI_TOP30, SUI_TOP50, SUI_TOP70 = getNoTopX_SUI(df_season, disciplin)
        data.append({
            'birthyear': birthyear,
            'season': season,
            'top30': SUI_TOP30,
            'top50': SUI_TOP50,
            'top70': SUI_TOP70
        })
        birthyear += 1
    return pd.DataFrame(data)

def collect_data_Entw(birthyear, FISYear, Gender, top, disciplin, combined_df):
    data = []
    season = birthyear + 16 + FISYear
    for i in range(11):
        df_season = combined_df[(combined_df['birthyear'] == birthyear) &
                                (combined_df['listyear'] == season) &
                                (combined_df['gender'] == Gender)]
        MeanInt = getMeanTopX_Int(df_season, disciplin, top)
        MeanSUI = getMeanTopX_SUI(df_season, disciplin, top)
        data.append({
            'birthyear': birthyear,
            'season': season,
            'meanint': MeanInt,
            'meansui': MeanSUI
        })
        season += 1
    return pd.DataFrame(data)
