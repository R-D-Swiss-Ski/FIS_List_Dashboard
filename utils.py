import pandas as pd 
def getMeanTopX_Int(df_season, disciplin, top):
    df_Int = df_season[df_season['Nationcode'] != 'SUI']
    df_Int = df_Int.sort_values(by=str(disciplin) + 'pos', ascending=True)
    df_Int = df_Int.head(top)       
    mean_dhpos = df_Int[str(disciplin) + 'pos'].mean()
    return mean_dhpos

def getMeanTopX_SUI(df_season, disciplin, top):
    df_SUI = df_season[df_season['Nationcode'] == 'SUI']
    df_SUI = df_SUI.sort_values(by=str(disciplin) + 'pos', ascending=True)
    df_SUI = df_SUI.head(top)       
    mean_dhpos = df_SUI[str(disciplin) + 'pos'].mean()
    return mean_dhpos

def getNoTopX_SUI(df_season, disciplin):
    df_season = df_season.sort_values(by=str(disciplin) + 'pos', ascending=True)
    count_SUI_TOP30 = df_season.head(30)[df_season['Nationcode'] == 'SUI'].shape[0]
    count_SUI_TOP50 = df_season.head(50)[df_season['Nationcode'] == 'SUI'].shape[0]  
    count_SUI_TOP70 = df_season.head(70)[df_season['Nationcode'] == 'SUI'].shape[0] 
    print(count_SUI_TOP30)
    return count_SUI_TOP30,count_SUI_TOP50, count_SUI_TOP70


def collect_data(birthyear, FISYear, Gender, top, disciplin, combined_df):
    data = []
    for i in range(11):
        season = birthyear + 16 + FISYear
        df_season = combined_df[(combined_df['Birthyear'] == birthyear) & 
                                (combined_df['Listyear'] == str(season)) & 
                                (combined_df['Gender'] == Gender)]
        MeanInt = getMeanTopX_Int(df_season, disciplin, top)
        MeanSUI = getMeanTopX_SUI(df_season, disciplin, top)
        data.append({
            'birthyear': birthyear,
            'Season': season,
            'MeanInt': MeanInt,
            'MeanSUI': MeanSUI
        })
        birthyear += 1
    return pd.DataFrame(data)


def collect_data_No(birthyear, FISYear, Gender, disciplin, combined_df):
    data = []
    for i in range(11):
        season = birthyear + 16 + FISYear
        df_season = combined_df[(combined_df['Birthyear'] == birthyear) & 
                                (combined_df['Listyear'] == str(season)) & 
                                (combined_df['Gender'] == Gender)]
        getNoTopX_SUI(df_season, disciplin)
        SUI_TOP30, SUI_TOP50, SUI_TOP70 = getNoTopX_SUI(df_season, disciplin)
        data.append({
            'birthyear': birthyear,
            'Season': season,
            'Top30': SUI_TOP30,
            'Top50': SUI_TOP50,
            'Top70' : SUI_TOP70
        })
        birthyear += 1
    return pd.DataFrame(data)

def collect_data_Entw(birthyear, FISYear, Gender, top, disciplin, combined_df):
    data = []
    season = birthyear + 16 + FISYear
    for i in range(11):
        df_season = combined_df[(combined_df['Birthyear'] == birthyear) & 
                                (combined_df['Listyear'] == str(season)) & 
                                (combined_df['Gender'] == Gender)]
        MeanInt = getMeanTopX_Int(df_season, disciplin, top)
        MeanSUI = getMeanTopX_SUI(df_season, disciplin, top)
        data.append({
            'birthyear': birthyear,
            'Season': season,
            'MeanInt': MeanInt,
            'MeanSUI': MeanSUI
        })
        season += 1
    return pd.DataFrame(data)


def FIS_Year_Compare(Gender, top, disciplin, df_names):

    df_names = df_names[(df_names['Gender'] == Gender)] 
    df_names = df_names[(df_names['Birthyear'] >= 1998) & (df_names['Birthyear'] <= 2011)]
    df_listyear_Int = pd.DataFrame()
    df_listyear_SUI = pd.DataFrame()

    for listyear in range(1, 11):
        df_temp_Int = df_names[(df_names['FISyearAthlete'] == listyear) & (df_names['Nationcode'] != 'SUI')]
        df_temp_Int = df_temp_Int.sort_values(by=str(disciplin) + 'pos', ascending=True).head(top)
        df_listyear_Int = pd.concat([df_listyear_Int, df_temp_Int])

        df_temp_SUI = df_names[(df_names['FISyearAthlete'] == listyear) & (df_names['Nationcode'] == 'SUI')]
        df_temp_SUI = df_temp_SUI.sort_values(by=str(disciplin) + 'pos', ascending=True).head(top)
        df_listyear_SUI = pd.concat([df_listyear_SUI, df_temp_SUI])

    df_listyear_Int = df_listyear_Int.sort_values(by='FISyearAthlete', ascending=True).rename(columns={'Listyear': 'Season'})
    df_listyear_SUI = df_listyear_SUI.sort_values(by='FISyearAthlete', ascending=True).rename(columns={'Listyear': 'Season'})
    return df_listyear_Int, df_listyear_SUI  # return the dataframes of the top x athletes

def getTopXAthletes(df_FIS_List, Gender, disciplin, top):
    df_FIS_List = df_FIS_List[(df_FIS_List['gender'] == Gender)]
    df_topX = df_FIS_List.sort_values(by=str(disciplin) + 'pos', ascending=True)
    df_topX = df_topX.head(top)
    return df_topX