import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import pickle
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
from utils import getMeanTopX_Int, getMeanTopX_SUI, collect_data, collect_data_No, collect_data_Entw, collect_data_Entw_Names


### PAGE CONFIGURATION ###

st.set_page_config(
    page_title="Auswertungs-Dashboards",
    layout="wide",
    )

### PAGE CONTENT ###

st.title("FIS Points List Dashboard")

selected = option_menu(
            None, [ "Top 3", "Top 20", "Jahrgang Season", "Jahrgang Season No", "Jahrgang Season Entw.","Jahrgang Season Names" ],
            icons=["trophy-fill", "trophy","archive", "archive-fill","rocket"],
            orientation= "horizontal",
            styles={
                "container": {"padding": "0!important"},
                "icon": {"color": "rgb(0, 104, 201)", "font-size": "22px"},
                "nav-link": {"font-size": "22px", "text-align": "center", "margin":"0px",  "--hover-color": "#d6d6d6"},
                "nav-link-selected": {"background-color": "rgba(0, 104, 201, 0.5)", "font-weight": "normal", "color": "white"},
            })



### HELPER FUNCTIONS ###
def get_latest_fis_list():

    data = pd.read_csv("data/FIS-points-list-AL-2025-408.csv") 
    data.columns = map(str.lower, data.columns)

    return data

def highlight_suiss(val):
    if val == "SUI":
        return 'background-color: rgba(0, 102, 255, 0.8)'
    return ''


def formated_dataframe(df,n):
    height = 750 if n == 20 else None
    df_formated = st.dataframe(
        df,
        hide_index=True,
        use_container_width=True,
        height=height,
        column_config={
            "Name": st.column_config.Column(width=150)
        }
    )

    return df_formated

def create_table(data, discipline, n=3, style=False):

    pos = discipline + "pos"
    points = discipline + "points"

    df_filtered = data.dropna(subset=[pos])
    df_filtered = df_filtered.sort_values(by=pos, ascending=True)
    df_topX = df_filtered.head(n)

    # Format the table
    df_topX_display = df_topX.rename(columns={
        "competitorname": "Name",
        "nationcode": "Nat",
        points: "Best",
        pos: "Rank" 
    })[["Name", "Nat", "Best", "Rank"]]

    if style: 
        styled_df = (df_topX_display.style
                    .map(highlight_suiss, subset=['Nat'])
                    .format({
                        "Rank": "{:.0f}",   # No decimal places
                        "Best": "{:.2f}"    # Two decimal places
                    })
                )
        
        return formated_dataframe(styled_df,n)

    # Display the table in Streamlit
    return formated_dataframe(df_topX_display,n)



#------------------------------------------------------------TOP 3------------------------------------------------------------
if selected == "Top 3":

    st.title("FIS List 17th of 2025 (408 - 23-02-2025)")
    # Load the data (Change to read from pickle for easier solution)
    data = get_latest_fis_list()

    # Sort the data so the most recent year is at index 0 
    birthyear_options = data["birthyear"].unique().tolist()
    birthyear_options.sort(reverse=True)

    col1, col2, col3 = st.columns([1,1,2])

    with col1:
        option_birthyear = st.selectbox(
                                    "Birthyear",
                                    birthyear_options,
                                    index=0
                                )
    
    with col2:
        option_gender = st.selectbox(
                                    "Gender",
                                    ["M", "W"],
                                    index=0
                                )

    filtered_data = data[(data["birthyear"] == option_birthyear) & (data["gender"] == option_gender)]

    col2_1, col2_2, col2_3, col2_4 = st.columns([1,1,1,1])

    with col2_1:
        st.subheader("Slalom")
        create_table(filtered_data, "sl")

    with col2_2:
        st.subheader("Giant Slalom")
        create_table(filtered_data, "gs")

    with col2_3:
        st.subheader("Super G")
        create_table(filtered_data, "sg")

    with col2_4:
        st.subheader("Downhill")
        create_table(filtered_data, "dh")

    # Only swiss athletes
    col3_1, col3_2, col3_3, col3_4 = st.columns([1,1,1,1])
    SUI_data = filtered_data[filtered_data["nationcode"] == "SUI"]

    with col3_1:
        st.markdown("<h3 style='color:blue;'>Slalom SUI</h3>", unsafe_allow_html=True)
        create_table(SUI_data, "sl")

    with col3_2:
        st.markdown("<h3 style='color:blue;'>Giant Slalom SUI</h3>", unsafe_allow_html=True)
        create_table(SUI_data, "gs")

    with col3_3:
        st.markdown("<h3 style='color:blue;'>Super G SUI</h3>", unsafe_allow_html=True)
        create_table(SUI_data, "sg")

    with col3_4:
        st.markdown("<h3 style='color:blue;'>Downhill SUI</h3>", unsafe_allow_html=True)
        create_table(SUI_data, "dh")


    col4_1, col4_2, col4_3 = st.columns([1,1,2])

    with col4_1:
        option_birthyear2 = st.selectbox(
                                    "Birthyear",
                                    birthyear_options,
                                    key="by2",
                                    index=0
                                )
    
    with col4_2:
        option_gender2 = st.selectbox(
                                    "Gender",
                                    ["M", "W"],
                                    key="gen2",
                                    index=0
                                )
        
    filtered_data2 = data[(data["birthyear"] == option_birthyear2) & (data["gender"] == option_gender2)]

    col5_1, col5_2, col5_3, col5_4 = st.columns([1,1,1,1])

    with col5_1:
        st.subheader("Slalom")
        create_table(filtered_data2, "sl")

    with col5_2:
        st.subheader("Giant Slalom")
        create_table(filtered_data2, "gs")

    with col5_3:
        st.subheader("Super G")
        create_table(filtered_data2, "sg")

    with col5_4:
        st.subheader("Downhill")
        create_table(filtered_data2, "dh")

    # Only swiss athletes
    col6_1, col6_2, col6_3, col6_4 = st.columns([1,1,1,1])
    SUI_data2 = filtered_data2[filtered_data2["nationcode"] == "SUI"]

    with col6_1:
        st.markdown("<h3 style='color:blue;'>Slalom SUI</h3>", unsafe_allow_html=True)
        create_table(SUI_data2, "sl")

    with col6_2:
        st.markdown("<h3 style='color:blue;'>Giant Slalom SUI</h3>", unsafe_allow_html=True)
        create_table(SUI_data2, "gs")

    with col6_3:
        st.markdown("<h3 style='color:blue;'>Super G SUI</h3>", unsafe_allow_html=True)
        create_table(SUI_data2, "sg")

    with col6_4:
        st.markdown("<h3 style='color:blue;'>Downhill SUI</h3>", unsafe_allow_html=True)
        create_table(SUI_data2, "dh")


#------------------------------------------------------------TOP 20------------------------------------------------------------
if selected == "Top 20":

    data = get_latest_fis_list()

    # Sort the data so the most recent year is at index 0 
    birthyear_options = data["birthyear"].unique().tolist()
    birthyear_options.sort(reverse=True)

    col1, col2, col3 = st.columns([1,1,2])

    with col1:
        option_birthyear = st.selectbox(
                                    "Birthyear",
                                    birthyear_options,
                                    index=0
                                )
    
    with col2:
        option_gender = st.selectbox(
                                    "Gender",
                                    ["M", "W"],
                                    index=0
                                )
        
    filtered_data = data[(data["birthyear"] == option_birthyear) & (data["gender"] == option_gender)]

    col1_1, col1_2, col1_3, col1_4 = st.columns([1,1,1,1])

    with col1_1:
        st.subheader("Slalom")
        create_table(filtered_data, "sl", 20, True)

    with col1_2:
        st.subheader("Giant Slalom")
        create_table(filtered_data, "gs", 20, True)

    with col1_3:
        st.subheader("Super G")
        create_table(filtered_data, "sg", 20, True)

    with col1_4:
        st.subheader("Downhill")
        create_table(filtered_data, "dh", 20, True)


    col2_1, col2_2, col2_3, col2_4 = st.columns([1,1,1,1])
    SUI_data = filtered_data[filtered_data["nationcode"] == "SUI"]

    with col2_1:
        st.subheader("Slalom SUI")
        create_table(SUI_data, "sl", 5)

    with col2_2:
        st.subheader("Giant Slalom SUI")
        create_table(SUI_data, "gs", 5)

    with col2_3:
        st.subheader("Super G SUI")
        create_table(SUI_data, "sg", 5)

    with col2_4:
        st.subheader("Downhill")
        create_table(SUI_data, "dh", 5)



#------------------------------------------------------------Jahrgang Season------------------------------------------------------------
if selected == "Jahrgang Season":

    # User inputs
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        birthyear = st.number_input("Enter birth year:", value=1998, min_value=1994, max_value=2011)
    
    with col2:
        FISYear = st.number_input("Enter FIS Year:", value=1, min_value=1, max_value=5)
    
    with col3:
        Gender = st.selectbox("Select Gender:", options=['M', 'W'])
    
    with col4:
        disciplin = st.selectbox("Select Discipline:", options=['DH', 'SL', 'GS', 'SG', 'AC'])

    # Load the data
    pickle_file_path = 'data/fis_list_combined_export_new.pkl'
    if os.path.exists(pickle_file_path):
        with open(pickle_file_path, 'rb') as f:
            combined_df = pickle.load(f)
    else:
        st.error(f"Pickle file not found at {pickle_file_path}")

    #st.write(combined_df)
    combined_df['Listname'] = combined_df['Listname'].astype(str)
    combined_df['Listyear'] = combined_df['Listname'].str[-4:]
    combined_df['Listyear'] = combined_df['Listyear'].replace("4/25", "2025")

    # Collect data for top 3, 10, and 15
    df_results_top3 = collect_data(birthyear, FISYear, Gender, 3, disciplin, combined_df)
    df_results_top10 = collect_data(birthyear, FISYear, Gender, 10, disciplin, combined_df)
    df_results_top15 = collect_data(birthyear, FISYear, Gender, 15, disciplin, combined_df)

    def format_season_column(df, birthyear_col='birthyear'):
        df['Season'] = df['Season'].astype(str).str[2:]
        df['Season'] = df['Season'].astype(int).apply(lambda x: f"{x-1}/{x}")
        df['Season'] = "S" + df['Season'].astype(str) + " BY" + df[birthyear_col].astype(str)
        return df

    df_results_top3 = format_season_column(df_results_top3)
    df_results_top10 = format_season_column(df_results_top10)
    df_results_top15 = format_season_column(df_results_top15)

    # Plotting
    fig, ax = plt.subplots(1, 3, figsize=(24, 6), dpi=300)  # Set dpi to 300 for higher resolution
    col1, col2, col3 = st.columns(3)
    with col1:
        # Top 3 Plot
        ax[0].plot(df_results_top3['Season'], df_results_top3['MeanInt'], label='Int', marker='o', color= '#0328fc')
        ax[0].plot(df_results_top3['Season'], df_results_top3['MeanSUI'], label='SUI', marker='o', color= '#4a0a13')
        ax[0].set_title('Top 3 ' + str(disciplin))
        ax[0].invert_yaxis()
        ax[0].set_xlabel('Season')
        ax[0].set_ylabel('Weltranglistenposition')
        ax[0].legend()
        ax[0].grid(True)
        ax[0].set_xticks(df_results_top3['Season'])  # Add tick for every year
        ax[0].set_xticklabels(df_results_top3['Season'], rotation=45)

        # Add value labels
        for i, txt in enumerate(df_results_top3['MeanInt']):
            ax[0].annotate(f'{txt:.2f}', (df_results_top3['Season'][i], df_results_top3['MeanInt'][i]), textcoords="offset points", xytext=(0,10), ha='center', color='#0328fc')
        for i, txt in enumerate(df_results_top3['MeanSUI']):
            ax[0].annotate(f'{txt:.2f}', (df_results_top3['Season'][i], df_results_top3['MeanSUI'][i]), textcoords="offset points", xytext=(0,10), ha='center', color='#4a0a13')

    with col2:
        # Top 10 Plot
        ax[1].plot(df_results_top10['Season'], df_results_top10['MeanInt'], label='Int', marker='o', color= '#0328fc')
        ax[1].plot(df_results_top10['Season'], df_results_top10['MeanSUI'], label='SUI', marker='o', color= '#4a0a13')
        ax[1].set_title('Top 10 ' + str(disciplin))
        ax[1].invert_yaxis()
        ax[1].set_xlabel('Season')
        ax[1].set_ylabel('Weltranglistenposition')
        ax[1].legend()
        ax[1].grid(True)
        ax[1].set_xticks(df_results_top10['Season'])  # Add tick for every year
        ax[1].set_xticklabels(df_results_top10['Season'], rotation=45)

         # Add value labels
        for i, txt in enumerate(df_results_top10['MeanInt']):
            ax[1].annotate(f'{txt:.2f}', (df_results_top10['Season'][i], df_results_top10['MeanInt'][i]), textcoords="offset points", xytext=(0,10), ha='center', color='#0328fc')
        for i, txt in enumerate(df_results_top10['MeanSUI']):
            ax[1].annotate(f'{txt:.2f}', (df_results_top10['Season'][i], df_results_top10['MeanSUI'][i]), textcoords="offset points", xytext=(0,10), ha='center', color='#4a0a13')

    with col3:
        # Top 15 Plot
        ax[2].plot(df_results_top15['Season'], df_results_top15['MeanInt'], label='Int', marker='o', color= '#0328fc')
        ax[2].plot(df_results_top15['Season'], df_results_top15['MeanSUI'], label='SUI', marker='o', color= '#4a0a13') 
        ax[2].set_title('Top 15 ' + str(disciplin))
        ax[2].invert_yaxis()
        ax[2].set_xlabel('Season')
        ax[2].set_ylabel('Weltranglistenposition')
        ax[2].legend()
        ax[2].grid(True)
        ax[2].set_xticks(df_results_top15['Season'])  # Add tick for every year
        ax[2].set_xticklabels(df_results_top15['Season'], rotation=45)
     
        # Add value labels
        for i, txt in enumerate(df_results_top15['MeanInt']):
            ax[2].annotate(f'{txt:.2f}', (df_results_top15['Season'][i], df_results_top15['MeanInt'][i]), textcoords="offset points", xytext=(0,10), ha='center', color='#0328fc')
        for i, txt in enumerate(df_results_top15['MeanSUI']):
            ax[2].annotate(f'{txt:.2f}', (df_results_top15['Season'][i], df_results_top15['MeanSUI'][i]), textcoords="offset points", xytext=(0,10), ha='center', color='#4a0a13')


    st.pyplot(fig)

#------------------------------------------------------------Jahrgang Season No------------------------------------------------------------
if selected == "Jahrgang Season No":

  # User inputs
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        birthyear = st.number_input("Enter birth year:", value=1998, min_value=1994, max_value=2011)
    
    with col2:
        FISYear = st.number_input("Enter FIS Year:", value=1, min_value=1, max_value=5)
    
    with col3:
        Gender = st.selectbox("Select Gender:", options=['M', 'W'])
    
    with col4:
        disciplin = st.selectbox("Select Discipline:", options=['DH', 'SL', 'GS', 'SG', 'AC'])

    # Load the data
    pickle_file_path = 'data/fis_list_combined_export_new.pkl'
    if os.path.exists(pickle_file_path):
        with open(pickle_file_path, 'rb') as f:
            combined_df = pickle.load(f)
    else:
        st.error(f"Pickle file not found at {pickle_file_path}")

    #st.write(combined_df)
    combined_df['Listname'] = combined_df['Listname'].astype(str)
    combined_df['Listyear'] = combined_df['Listname'].str[-4:]
    combined_df['Listyear'] = combined_df['Listyear'].replace("4/25", "2025")

   
    df_results_top = collect_data_No(birthyear, FISYear, Gender, disciplin, combined_df)


    col1, col2 = st.columns(2)

    with col1:
        st.dataframe(df_results_top.style.format(precision=0))

    with col2:
       
        df_results_top['Season'] = df_results_top['Season'].astype(str).str[2:]
        df_results_top['Season'] = df_results_top['Season'].apply(lambda x: f"{int(x)-1}/{int(x)}" if x.isdigit() else x)
        df_results_top['Season'] = "S" + df_results_top['Season'].astype(str) + " BY" + df_results_top['birthyear'].astype(str)

        # Create bar plot
        fig, ax = plt.subplots(figsize=(10, 6))
        bar_width = 0.25
        index = range(len(df_results_top['Season']))
        bar1 = ax.bar(index, df_results_top['Top30'], bar_width, label='Top 30', color='#F5921B')
        bar2 = ax.bar([i + bar_width for i in index], df_results_top['Top50'], bar_width, label='Top 50', color='#87BB62')
        bar3 = ax.bar([i + 2 * bar_width for i in index], df_results_top['Top70'], bar_width, label='Top 70', color='#876FD4')

        ax.set_xlabel('Season and Birth Year')
        ax.set_ylabel('Count')
        ax.set_title('Number of SUI Athletes in Top 30, 50, and 70')
        ax.set_xticks([i + bar_width for i in index])
        ax.set_xticklabels(df_results_top['Season'], rotation=45)
        ax.legend()
        ax.grid(False)

        # Add value labels on bars
        for bar in bar1:
            height = bar.get_height()
            ax.annotate(f'{height:.0f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', color='#F5921B')
        for bar in bar2:
            height = bar.get_height()
            ax.annotate(f'{height:.0f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', color='#87BB62')
        for bar in bar3:
            height = bar.get_height()
            ax.annotate(f'{height:.0f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', color='#876FD4')

        st.pyplot(fig)

#------------------------------------------------------------Jahrgang Season Entw------------------------------------------------------------

if selected == "Jahrgang Season Entw.":


    # User inputs
    col1, col2, col3 = st.columns(3)

    with col1:
        birthyear = st.number_input("Enter birth year:", value=1998, min_value=1994, max_value=2011)
    
    with col2:
        Gender = st.selectbox("Select Gender:", options=['M', 'W'])

    with col3:
        top = st.number_input("Select Top X:", value=10, min_value=3, max_value=50)

    FISYear = 1
    # Load the data
    pickle_file_path = 'data/fis_list_combined_export_new.pkl'
    if os.path.exists(pickle_file_path):
        with open(pickle_file_path, 'rb') as f:
            combined_df = pickle.load(f)
    else:
        st.error(f"Pickle file not found at {pickle_file_path}")

    #st.write(combined_df)
    combined_df['Listname'] = combined_df['Listname'].astype(str)
    combined_df['Listyear'] = combined_df['Listname'].str[-4:]
    combined_df['Listyear'] = combined_df['Listyear'].replace("4/25", "2025")

    # Collect data for top 3, 10, and 15
    #'SL', 'GS', 'SG'])
    

    def format_season_column(df, birthyear_col='birthyear'):
        df['Season'] = df['Season'].astype(str).str[2:]
        df['Season'] = df['Season'].astype(int).apply(lambda x: f"{x-1}/{x}")
        df['Season'] = "S" + df['Season'].astype(str) + " BY" + df[birthyear_col].astype(str)
        return df
    
    # Plotting
    fig, ax = plt.subplots(2, 2, figsize=(24, 12), dpi=300)  # Set dpi to 300 for higher resolution
    fig.subplots_adjust(hspace=0.4)  # Add space between rows
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    
    disciplines = ['DH', 'SG', 'SL', 'GS']
    
    for i, disciplin in enumerate(disciplines):
        df_results_top = collect_data_Entw(birthyear, FISYear, Gender, top, disciplin, combined_df)
        df_results_top = format_season_column(df_results_top)
        
        row = i // 2
        col = i % 2
        
        ax[row, col].plot(df_results_top['Season'], df_results_top['MeanInt'], label='Int', marker='o', color= '#0328fc')
        ax[row, col].plot(df_results_top['Season'], df_results_top['MeanSUI'], label='SUI', marker='o', color= '#4a0a13')
        ax[row, col].set_title('Top ' + str(top) + ' ' + str(disciplin))
        ax[row, col].invert_yaxis()
        ax[row, col].set_xlabel('Season')
        ax[row, col].set_ylabel('Weltranglistenposition')
        ax[row, col].legend()
        ax[row, col].grid(True)
        ax[row, col].set_xticks(df_results_top['Season'])  # Add tick for every year
        ax[row, col].set_xticklabels(df_results_top['Season'], rotation=45)

        # Add value labels
        for i, txt in enumerate(df_results_top['MeanInt']):
            ax[row, col].annotate(f'{txt:.2f}', (df_results_top['Season'][i], df_results_top['MeanInt'][i]), textcoords="offset points", xytext=(0,10), ha='center', color='#0328fc')
        for i, txt in enumerate(df_results_top['MeanSUI']):
            ax[row, col].annotate(f'{txt:.2f}', (df_results_top['Season'][i], df_results_top['MeanSUI'][i]), textcoords="offset points", xytext=(0,10), ha='center', color='#4a0a13')
    
    st.pyplot(fig)

#------------------------------------------------------------Jahrgang Season Names------------------------------------------------------------

if selected == "Jahrgang Season Names":
    st.markdown("<h3 style='color:blue;'>International</h3><h3 style='color:#4a0a13; display:inline;'> vs Swiss</h3>", unsafe_allow_html=True)

    # User inputs
    col1, col2, col3 = st.columns(3)

    with col1:
        birthyear = st.number_input("Enter birth year:", value=1998, min_value=1991, max_value=2011)
    
    with col2:
        Gender = st.selectbox("Select Gender:", options=['M', 'W'])

    with col3:
        top = st.number_input("Select Top X:", value=3, min_value=3, max_value=20)

    FISYear = 1
    # Load the data
    pickle_file_path = 'data/fis_list_combined_export_new.pkl'
    if os.path.exists(pickle_file_path):
        with open(pickle_file_path, 'rb') as f:
            combined_df = pickle.load(f)
    else:
        st.error(f"Pickle file not found at {pickle_file_path}")

    #st.write(combined_df)
    combined_df['Listname'] = combined_df['Listname'].astype(str)
    combined_df['Listyear'] = combined_df['Listname'].str[-4:]
    combined_df['Listyear'] = combined_df['Listyear'].replace("4/25", "2025")


    def format_season_column(df, birthyear_col='birthyear'):
        df['Season'] = df['Season'].astype(str).str[2:]
        df['Season'] = df['Season'].astype(int).apply(lambda x: f"{x-1}/{x}")
        df['Season'] = "S" + df['Season'].astype(str) + " BY" + df[birthyear_col].astype(str)
        return df
    
    # Plotting
    fig, ax = plt.subplots(2, 2, figsize=(24, 12), dpi=300)  # Set dpi to 300 for higher resolution
    fig.subplots_adjust(hspace=0.4)  # Add space between rows
    
    disciplines = ['DH', 'SG', 'SL', 'GS']
    
    for i, disciplin in enumerate(disciplines):
        df_results_top = collect_data_Entw_Names(birthyear, FISYear, Gender, top, disciplin, combined_df)

        # Ensure 'Season' is treated as a categorical variable for correct plotting
        df_results_top['Season'] = pd.Categorical(df_results_top['Season'], ordered=True)

        # Group and calculate mean positions for non-SUI and SUI athletes
        mean_pos_int = df_results_top[df_results_top['Nationcode'] != "SUI"].groupby('Season')[str(disciplin) + 'pos'].mean()
        mean_pos_sui = df_results_top[df_results_top['Nationcode'] == "SUI"].groupby('Season')[str(disciplin) + 'pos'].mean()

        # Calculate the range for non-SUI and SUI athletes
        range_pos_int = df_results_top[df_results_top['Nationcode'] != "SUI"].groupby('Season')[str(disciplin) + 'pos'].agg(['min', 'max'])
        range_pos_sui = df_results_top[df_results_top['Nationcode'] == "SUI"].groupby('Season')[str(disciplin) + 'pos'].agg(['min', 'max'])

        # Create the plot
        fig = go.Figure()

        # Add traces for mean positions
        fig.add_trace(go.Scatter(x=mean_pos_int.index, y=mean_pos_int, mode='lines+markers', name='meanINT', marker=dict(color='#0328fc')))
        fig.add_trace(go.Scatter(x=mean_pos_sui.index, y=mean_pos_sui, mode='lines+markers', name='meanSUI', marker=dict(color='#4a0a13')))

        # Add traces for range (shaded area)
        fig.add_trace(go.Scatter(x=range_pos_int.index, y=range_pos_int['min'], mode='lines', line=dict(width=0), showlegend=False))
        fig.add_trace(go.Scatter(x=range_pos_int.index, y=range_pos_int['max'], mode='lines', fill='tonexty', name='INT Range', fillcolor='rgba(3, 40, 252, 0.2)', line=dict(width=0)))

        fig.add_trace(go.Scatter(x=range_pos_sui.index, y=range_pos_sui['min'], mode='lines', line=dict(width=0), showlegend=False))
        fig.add_trace(go.Scatter(x=range_pos_sui.index, y=range_pos_sui['max'], mode='lines', fill='tonexty', name='SUI Range', fillcolor='rgba(74, 10, 19, 0.2)', line=dict(width=0)))

        # Add hover text with athlete names and positions
        added_names = set()
        for season in df_results_top['Season'].unique():
            season_data = df_results_top[df_results_top['Season'] == season]
            for _, row in season_data.iterrows():
                athlete_name = f"{row['Firstname']} {row['Lastname']}"
                position = row[str(disciplin) + 'pos']
                fig.add_trace(go.Scatter(
                    x=[season],
                    y=[position],
                    mode='markers',
                    marker=dict(size=10, color='#0328fc' if row['Nationcode'] != 'SUI' else '#4a0a13'),
                    text=f"{athlete_name}: {position}",
                    hoverinfo='text',
                    showlegend=False  # Hide legend for individual athletes
                ))

        # Generate a list of unique Swiss athlete names
        unique_athletes = df_results_top[df_results_top['Nationcode'] == "SUI"][['Firstname', 'Lastname']].drop_duplicates()
        athlete_names = unique_athletes.apply(lambda row: f"{row['Firstname']} {row['Lastname']}", axis=1).tolist()

        st.subheader(f'Top {top} {disciplin}')
        # Add a selectbox for selecting an athlete
        selected_athlete = st.selectbox("Select Athlete", ["None"] + athlete_names)

        # Highlight the selected athlete in the plot
        if selected_athlete != "None":
            selected_firstname, selected_lastname = selected_athlete.split(' ', 1)
            selected_data = df_results_top[(df_results_top['Firstname'] == selected_firstname) & (df_results_top['Lastname'] == selected_lastname)]
            for _, row in selected_data.iterrows():
                fig.add_trace(go.Scatter(
                    x=[row['Season']],
                    y=[row[str(disciplin) + 'pos']],
                    mode='markers',
                    marker=dict(size=12, color='red'),
                    text=f"{row['Firstname']} {row['Lastname']}: {row[str(disciplin) + 'pos']}",
                    hoverinfo='text',
                    showlegend=False  # Hide legend for individual athletes
                ))

        # Update layout again to include the highlighted athlete
        fig.update_layout(
            #title=f'Top {top} {disciplin}',
            xaxis_title='Season',
            yaxis_title='Weltranglistenposition',
            yaxis=dict(autorange='reversed'),
            legend_title='Legend',
            hovermode='closest'
        )

        # Display the updated plot in Streamlit
        st.plotly_chart(fig, key=f"highlighted_plot_{disciplin}")


