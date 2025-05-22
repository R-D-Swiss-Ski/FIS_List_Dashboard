import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import pickle
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
from utils import getMeanTopX_Int, getMeanTopX_SUI, collect_data, collect_data_No, collect_data_Entw


### PAGE CONFIGURATION ###

st.set_page_config(
    page_title="Auswertungs-Dashboards",
    layout="wide",
    )

### PAGE CONTENT ###

st.title("FIS Points List Dashboard")
st.header("FIS Pointlist 1.5.2025")

selected = option_menu(
            None, [ "Top 3", "Top X", "Year of birth and Season #", "Year of birth over seasons", "Year of birth Development over Seasons", "Current Top Athletes - Development", "Athlete - All Disciplines - Development"],
            icons=["trophy-fill", "trophy","clipboard2-pulse-fill", "receipt","rocket","speedometer2"],
            orientation= "horizontal",
            styles={
                "container": {"padding": "0!important"},
                "icon": {"color": "rgb(0, 104, 201)", "font-size": "22px"},
                "nav-link": {"font-size": "22px", "text-align": "center", "margin":"0px",  "--hover-color": "#d6d6d6"},
                "nav-link-selected": {"background-color": "rgba(0, 104, 201, 0.5)", "font-weight": "normal", "color": "white"},
            })

### PATHS ###
path_latest_fis_list_combinded = "data/fis_list_combined_1_05_25.pkl"
path_latest_fis_list = "data/FIS-points-list-AL-2025-413.csv"

### HELPER FUNCTIONS ###
@st.cache_data(show_spinner=False)
def get_latest_fis_list():
    data = pd.read_csv(path_latest_fis_list) 
    data.columns = map(str.lower, data.columns)
    return data

@st.cache_data(show_spinner=False)
def load_combined_data(path_latest_fis_list_combinded):
    if os.path.exists(path_latest_fis_list_combinded):
        with open(path_latest_fis_list_combinded, 'rb') as f:
            combined_df = pickle.load(f)
        combined_df.columns = list(map(str.lower, combined_df.columns))
        return combined_df
    else:
        st.error(f"Pickle file not found at {path_latest_fis_list_combinded}")
        return None

def highlight_suiss(val):
    if val == "SUI":
        return 'background-color: rgba(0, 102, 255, 0.8)'
    return ''

def formated_dataframe(df, n):
    height = 750 if n == 20 else None
    df_formated = st.dataframe(
        df,
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

    # Reset the 
    df_topX_display.reset_index(drop=True, inplace=True)
    df_topX_display.index += 1  # Start index at 1



    if style:
        styled_df = (df_topX_display.style
                    .map(highlight_suiss, subset=['Nat'])
                    .format({
                        "Rank": "{:.0f}",   # No decimal places
                        "Best": "{:.2f}"    # Two decimal places
                    })
                )
        return formated_dataframe(styled_df, n)

    # Display the table in Streamlit
    return formated_dataframe(df_topX_display, n)


def plot_fisyear_data(fig, df_grouped, comp_data, competitor_name, col_name, disciplin, use_log_scale):
    """
    Helper function to add traces to the plot for grouped data and competitor-specific data.
    """
    # Plot the mean line
    fig.add_trace(go.Scatter(
        name='Mean',
        x=df_grouped['fisyear'],
        y=df_grouped['mean'],
        mode='lines+markers',
        line=dict(color='blue')
    ))
    # Plot the upper bound (invisible, for fill)
    fig.add_trace(go.Scatter(
        name='Upper Bound',
        x=df_grouped['fisyear'],
        y=df_grouped['upper'],
        mode='lines',
        line=dict(width=0),
        showlegend=False
    ))
    # Plot the lower bound and fill to the previous trace
    fig.add_trace(go.Scatter(
        name='Lower Bound',
        x=df_grouped['fisyear'],
        y=df_grouped['lower'],
        mode='lines',
        line=dict(width=0),
        fill='tonexty',
        fillcolor='rgba(0, 0, 255, 0.2)',
        showlegend=False
    ))

    # Add competitor-specific data as a separate trace
    if not comp_data.empty:
        fig.add_trace(go.Scatter(
            name=competitor_name,
            x=comp_data['fisyear'],
            y=comp_data[col_name],
            mode='lines+markers',
            marker=dict(color='red', size=10),
            line=dict(color='red', dash='dash')
        ))

    # Update layout with the toggle for logarithmic scale
    fig.update_layout(
        title=f"{disciplin} Position vs FIS Year Athlete (with Std)",
        xaxis_title='FIS Year Athlete',
        yaxis_title=f"{disciplin} Position",
        yaxis_autorange='reversed',
        yaxis_type="log" if use_log_scale else "linear"
    )
    return fig


def calculate_statistics(fisyear_pos, col_name):
    """
    Helper function to calculate mean, standard deviation, and bounds.
    The lower bound is clamped at 0 to avoid negative position values.
    """
    df_grouped = fisyear_pos.groupby('fisyear')[col_name].agg(['mean', 'std']).reset_index()
    df_grouped['upper'] = df_grouped['mean'] + df_grouped['std']
    df_grouped['lower'] = (df_grouped['mean'] - df_grouped['std']).clip(lower=0)
    return df_grouped


#------------------------------------------------------------TOP 3------------------------------------------------------------
if selected == "Top 3":

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
            index=birthyear_options.index(1997) if 1997 in birthyear_options else 0
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
                                    index=birthyear_options.index(1997) if 1997 in birthyear_options else 0
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


#------------------------------------------------------------TOP X------------------------------------------------------------
if selected == "Top X":
    data = get_latest_fis_list()

    # Sort the data so the most recent year is at index 0 
    birthyear_options = data["birthyear"].unique().tolist()
    birthyear_options.sort(reverse=True)

    col1, col2, col3 = st.columns([1,2,3])

    with col1:
        birthyear_min = min(birthyear_options)
        birthyear_max = max(birthyear_options)
        birthyear_from = st.selectbox(
            "Birthyear from",
            birthyear_options,
            index=birthyear_options.index(1997) if 1997 in birthyear_options else 0,
            key="birthyear_from"
        )
        birthyear_to = st.selectbox(
            "Birthyear to",
            birthyear_options,
            index=0,
            key="birthyear_to"
        )

    with col2:
        option_gender = st.selectbox(
            "Gender",
            ["M", "W"],
            index=0
        )
    with col3:
        top = st.number_input("Select Top X:", value=20, min_value=3, max_value=300)

    # Ensure correct order for filtering
    by_from = min(birthyear_from, birthyear_to)
    by_to = max(birthyear_from, birthyear_to)
    filtered_data = data[
        (data["birthyear"] >= by_from) &
        (data["birthyear"] <= by_to) &
        (data["gender"] == option_gender)
    ]

    col1_1, col1_2, col1_3, col1_4 = st.columns([1,1,1,1])

    with col1_1:
        st.subheader("Slalom")
        create_table(filtered_data, "sl", top, True)

    with col1_2:
        st.subheader("Giant Slalom")
        create_table(filtered_data, "gs", top, True)

    with col1_3:
        st.subheader("Super G")
        create_table(filtered_data, "sg", top, True)

    with col1_4:
        st.subheader("Downhill")
        create_table(filtered_data, "dh", top, True)


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
        st.subheader("Downhill SUI")
        create_table(SUI_data, "dh", 5)


#------------------------------------------------------------Jahrgang Season No------------------------------------------------------------
if selected == "Year of birth and Season #":

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
    combined_df = load_combined_data(path_latest_fis_list_combinded)
    combined_df.columns = combined_df.columns.str.lower()

    combined_df['listname'] = combined_df['listname'].astype(str)
    combined_df['listyear'] = (
        combined_df['listname']
        .str[-4:]
        .replace("4/25", "2025")
    )
    combined_df['listyear'] = pd.to_numeric(combined_df['listyear'], errors='coerce').fillna(0).astype(int)
    combined_df['birthyear'] = pd.to_numeric(combined_df['birthyear'], errors='coerce').fillna(0).astype(int)
    combined_df['fisyearathlete'] = combined_df['listyear'] - combined_df['birthyear'] - 16
    combined_df['fisyearathlete'] = combined_df['fisyearathlete'].clip(lower=0).astype(int)

    df_results_top = collect_data_No(birthyear, FISYear, Gender, disciplin, combined_df)


    col1, col2 = st.columns(2)

    with col1:
        st.table(df_results_top.style.format(precision=0))

    with col2:
       
        df_results_top['season'] = df_results_top['season'].astype(str).str[2:]
        df_results_top['season'] = df_results_top['season'].apply(lambda x: f"{int(x)-1}/{int(x)}" if x.isdigit() else x)
        df_results_top['season'] = "S" + df_results_top['season'].astype(str) + " BY" + df_results_top['birthyear'].astype(str)

        # Create bar plot
        fig, ax = plt.subplots(figsize=(10, 6))
        bar_width = 0.25
        index = range(len(df_results_top['season']))
        bar1 = ax.bar(index, df_results_top['top30'], bar_width, label='Top 30', color='#F5921B')
        bar2 = ax.bar([i + bar_width for i in index], df_results_top['top50'], bar_width, label='Top 50', color='#87BB62')
        bar3 = ax.bar([i + 2 * bar_width for i in index], df_results_top['top70'], bar_width, label='Top 70', color='#876FD4')

        ax.set_xlabel('Season and Birth Year')
        ax.set_ylabel('Count')
        ax.set_title('Number of SUI Athletes in Top 30, 50, and 70')
        ax.set_xticks([i + bar_width for i in index])
        ax.set_xticklabels(df_results_top['season'], rotation=45)
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

#------------------------------------------------------------Jahrgang Season------------------------------------------------------------
if selected == "Year of birth over seasons":

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
    combined_df = load_combined_data(path_latest_fis_list_combinded)
    combined_df.columns = combined_df.columns.str.lower()

    combined_df['listname'] = combined_df['listname'].astype(str)
    combined_df['listyear'] = (
        combined_df['listname']
        .str[-4:]
        .replace("4/25", "2025")
    )
    combined_df['listyear'] = pd.to_numeric(combined_df['listyear'], errors='coerce').fillna(0).astype(int)
    combined_df['birthyear'] = pd.to_numeric(combined_df['birthyear'], errors='coerce').fillna(0).astype(int)
    combined_df['fisyearathlete'] = combined_df['listyear'] - combined_df['birthyear'] - 16
    combined_df['fisyearathlete'] = combined_df['fisyearathlete'].clip(lower=0).astype(int)

    # Collect data for top 3, 10, and 15
    df_results_top3 = collect_data(birthyear, FISYear, Gender, 3, disciplin, combined_df)
    df_results_top10 = collect_data(birthyear, FISYear, Gender, 10, disciplin, combined_df)
    df_results_top15 = collect_data(birthyear, FISYear, Gender, 15, disciplin, combined_df)

    def format_season_column(df, birthyear_col='birthyear'):
        df['season'] = df['season'].astype(str).str[2:]
        df['season'] = df['season'].astype(int).apply(lambda x: f"{x-1}/{x}")
        df['season'] = "S" + df['season'].astype(str) + " BY" + df[birthyear_col].astype(str)
        return df

    df_results_top3 = format_season_column(df_results_top3)
    df_results_top10 = format_season_column(df_results_top10)
    df_results_top15 = format_season_column(df_results_top15)

    # Plotting
    fig, ax = plt.subplots(1, 3, figsize=(24, 6), dpi=300)  # Set dpi to 300 for higher resolution
    col1, col2, col3 = st.columns(3)
    with col1:
        # Top 3 Plot
        ax[0].plot(df_results_top3['season'], df_results_top3['meanint'], label='Int', marker='o', color= '#0328fc')
        ax[0].plot(df_results_top3['season'], df_results_top3['meansui'], label='SUI', marker='o', color= '#4a0a13')
        ax[0].set_title('Top 3 ' + str(disciplin))
        ax[0].invert_yaxis()
        ax[0].set_xlabel('Season')
        ax[0].set_ylabel('Weltranglistenposition')
        ax[0].legend()
        ax[0].grid(True)
        ax[0].set_xticks(df_results_top3['season'])  # Add tick for every year
        ax[0].set_xticklabels(df_results_top3['season'], rotation=45)

        # Add value labels
        for i, txt in enumerate(df_results_top3['meanint']):
            ax[0].annotate(f'{txt:.2f}', (df_results_top3['season'][i], df_results_top3['meanint'][i]), textcoords="offset points", xytext=(0,10), ha='center', color='#0328fc')
        for i, txt in enumerate(df_results_top3['meansui']):
            ax[0].annotate(f'{txt:.2f}', (df_results_top3['season'][i], df_results_top3['meansui'][i]), textcoords="offset points", xytext=(0,10), ha='center', color='#4a0a13')

    with col2:
        # Top 10 Plot
        ax[1].plot(df_results_top10['season'], df_results_top10['meanint'], label='Int', marker='o', color= '#0328fc')
        ax[1].plot(df_results_top10['season'], df_results_top10['meansui'], label='SUI', marker='o', color= '#4a0a13')
        ax[1].set_title('Top 10 ' + str(disciplin))
        ax[1].invert_yaxis()
        ax[1].set_xlabel('Season')
        ax[1].set_ylabel('Weltranglistenposition')
        ax[1].legend()
        ax[1].grid(True)
        ax[1].set_xticks(df_results_top10['season'])  # Add tick for every year
        ax[1].set_xticklabels(df_results_top10['season'], rotation=45)

         # Add value labels
        for i, txt in enumerate(df_results_top10['meanint']):
            ax[1].annotate(f'{txt:.2f}', (df_results_top10['season'][i], df_results_top10['meanint'][i]), textcoords="offset points", xytext=(0,10), ha='center', color='#0328fc')
        for i, txt in enumerate(df_results_top10['meansui']):
            ax[1].annotate(f'{txt:.2f}', (df_results_top10['season'][i], df_results_top10['meansui'][i]), textcoords="offset points", xytext=(0,10), ha='center', color='#4a0a13')

    with col3:
        # Top 15 Plot
        ax[2].plot(df_results_top15['season'], df_results_top15['meanint'], label='Int', marker='o', color= '#0328fc')
        ax[2].plot(df_results_top15['season'], df_results_top15['meansui'], label='SUI', marker='o', color= '#4a0a13') 
        ax[2].set_title('Top 15 ' + str(disciplin))
        ax[2].invert_yaxis()
        ax[2].set_xlabel('Season')
        ax[2].set_ylabel('Weltranglistenposition')
        ax[2].legend()
        ax[2].grid(True)
        ax[2].set_xticks(df_results_top15['season'])  # Add tick for every year
        ax[2].set_xticklabels(df_results_top15['season'], rotation=45)
     
        # Add value labels
        for i, txt in enumerate(df_results_top15['meanint']):
            ax[2].annotate(f'{txt:.2f}', (df_results_top15['season'][i], df_results_top15['meanint'][i]), textcoords="offset points", xytext=(0,10), ha='center', color='#0328fc')
        for i, txt in enumerate(df_results_top15['meansui']):
            ax[2].annotate(f'{txt:.2f}', (df_results_top15['season'][i], df_results_top15['meansui'][i]), textcoords="offset points", xytext=(0,10), ha='center', color='#4a0a13')


    st.pyplot(fig)
#------------------------------------------------------------Jahrgang Season Entw------------------------------------------------------------

if selected == "Year of birth Development over Seasons":


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
    combined_df = load_combined_data(path_latest_fis_list_combinded)
    combined_df.columns = combined_df.columns.str.lower()

    combined_df['listname'] = combined_df['listname'].astype(str)
    combined_df['listyear'] = (
        combined_df['listname']
        .str[-4:]
        .replace("4/25", "2025")
    )
    combined_df['listyear'] = pd.to_numeric(combined_df['listyear'], errors='coerce').fillna(0).astype(int)
    combined_df['birthyear'] = pd.to_numeric(combined_df['birthyear'], errors='coerce').fillna(0).astype(int)
    combined_df['fisyearathlete'] = combined_df['listyear'] - combined_df['birthyear'] - 16
    combined_df['fisyearathlete'] = combined_df['fisyearathlete'].clip(lower=0).astype(int)

    def format_season_column(df, birthyear_col='birthyear'):
        df['season'] = df['season'].astype(str).str[2:]
        df['season'] = df['season'].astype(int).apply(lambda x: f"{x-1}/{x}")
        df['season'] = "S" + df['season'].astype(str) + " BY" + df[birthyear_col].astype(str)
        return df
    
    
    # Plotting
    fig, ax = plt.subplots(2, 2, figsize=(24, 12), dpi=300)  # Set dpi to 300 for higher resolution
    fig.subplots_adjust(hspace=0.4)  # Add space between rows

    disciplines = ['DH', 'SG', 'SL', 'GS']
    
    for i, disciplin in enumerate(disciplines):
        df_results_top = collect_data_Entw(birthyear, FISYear, Gender, top, disciplin, combined_df)
        df_results_top = format_season_column(df_results_top)
        # Create positional indices for categorical x-values
        positions = list(range(len(df_results_top)))
        
        row = i // 2
        col = i % 2
        
        ax[row, col].plot(positions, df_results_top['meanint'], label='Int', marker='o', color='#0328fc')
        ax[row, col].plot(positions, df_results_top['meansui'], label='SUI', marker='o', color='#4a0a13')
        ax[row, col].set_title('Top ' + str(top) + ' ' + str(disciplin))
        ax[row, col].invert_yaxis()
        ax[row, col].set_xlabel('Season')
        ax[row, col].set_ylabel('Weltranglistenposition')
        ax[row, col].legend()
        ax[row, col].grid(True)
        ax[row, col].set_xticks(positions)  # Add tick for every season
        ax[row, col].set_xticklabels(df_results_top['season'], rotation=45)
        
        # Set x-axis maximum to the season that contains "S24/25"
        if df_results_top['season'].str.contains("S24/25").any():
            max_index = df_results_top.index[df_results_top['season'].str.contains("S24/25")][0]
            ax[row, col].set_xlim(-0.5, max_index + 0.5)
        
        # Add value labels on the points using positions
        for j, txt in enumerate(df_results_top['meanint']):
            ax[row, col].annotate(f'{txt:.2f}', (positions[j], df_results_top['meanint'].iloc[j]),
                                   textcoords="offset points", xytext=(0,10), ha='center', color='#0328fc')
        for j, txt in enumerate(df_results_top['meansui']):
            ax[row, col].annotate(f'{txt:.2f}', (positions[j], df_results_top['meansui'].iloc[j]),
                                   textcoords="offset points", xytext=(0,10), ha='center', color='#4a0a13')
    
    st.pyplot(fig)


#------------------------------------------------------------Current Top Athletes - Development------------------------------------------------------------

if selected == "Current Top Athletes - Development":
    st.markdown("<h3><span style='color:blue;'>TopX</span><span style='color:#4a0a13;'> vs Swiss</span></h3>", unsafe_allow_html=True)
  
    col1, col2, col3 = st.columns(3)
    with col1:
        Gender = st.selectbox("Select Gender:", options=['M', 'W'], index=0)
    with col2:
        top = st.number_input("Select Top X:", value=30, min_value=10, max_value=100)
    with col3:
        # Add a dropdown menu to select the discipline
        disciplin = st.selectbox("Select Discipline:", options=['DH', 'SG', 'SL', 'GS'])

    # Load the data
    combined_df = load_combined_data(path_latest_fis_list_combinded)
    combined_df.columns = combined_df.columns.str.lower()
    df_FIS_list = get_latest_fis_list()

    # Filter the FIS list DataFrame for the selected gender and "nationcode" SUI
    df_FIS_list = df_FIS_list[
        (df_FIS_list["gender"].str.upper() == Gender.upper()) & 
        (df_FIS_list["nationcode"] == "SUI")
    ]

    ### Data formatting
    combined_df['listname'] = combined_df['listname'].astype(str)
    combined_df['listyear'] = (
        combined_df['listname']
        .str[-4:]
        .replace("4/25", "2025")
    )
    combined_df['listyear'] = pd.to_numeric(combined_df['listyear'], errors='coerce').fillna(0).astype(int)
    combined_df['birthyear'] = pd.to_numeric(combined_df['birthyear'], errors='coerce').fillna(0).astype(int)
    combined_df['fisyearathlete'] = (combined_df['listyear'] - combined_df['birthyear'] - 16).clip(lower=0).astype(int)
    df_FIS_list['competitorid'] = df_FIS_list['competitorid'].astype(str)
    combined_df['competitorid'] = combined_df['competitorid'].astype(str)
    combined_df.columns = combined_df.columns.str.lower()

    # Filter combined_df for SUI athletes
    combined_df_sui = combined_df[
        (combined_df["nationcode"] == "SUI") & (combined_df["gender"].str.upper() == Gender.upper())
    ]

    # Add toggle for logarithmic scale
    use_log_scale = st.checkbox("Use Logarithmic Scale for Y-Axis", value=False)

    # Determine the column name based on discipline (e.g., 'dhpos', 'sgpos', etc.)
    col_name = f"{disciplin.lower()}pos"

    # Get the top X athletes from the FIS list DataFrame for this discipline
    df_topX = df_FIS_list.nsmallest(top, col_name)[["competitorid", "competitorname"]]

    # --- Performance improvement with vectorized filtering ---
    # Instead of looping over each unique FIS year and iterating over rows,
    # filter combined_df for rows with competitorid in df_topX and drop rows with missing values in the position column.
    fisyear_pos = combined_df[
        combined_df['competitorid'].isin(df_topX['competitorid'])
    ][['fisyearathlete', 'competitorid', col_name, 'listyear']].dropna(subset=[col_name]).copy()
    fisyear_pos.rename(columns={'fisyearathlete': 'fisyear'}, inplace=True)

    # Combine competitor selections from top X and from SUI filtered data
    competitors_topX = df_topX.drop_duplicates(subset=["competitorid"])
    competitors_sui = combined_df_sui[['competitorid', 'competitorname']].drop_duplicates()

    competitor_mapping_topX = competitors_topX.set_index("competitorid")["competitorname"].to_dict()
    competitor_mapping_sui = competitors_sui.set_index("competitorid")["competitorname"].to_dict()

    col1, col2 = st.columns(2)
    with col1:
        selected_competitor_topX = st.selectbox(
            f"Select Athlete from Top {top} ({disciplin})",
            list(competitor_mapping_topX.keys()),
            format_func=lambda cid: competitor_mapping_topX[cid]
        )
    with col2:
        selected_competitor_sui = st.selectbox(
            f"Select SUI Athlete ({disciplin})",
            list(competitor_mapping_sui.keys()),
            format_func=lambda cid: competitor_mapping_sui[cid]
        )

    # Get competitor-specific data for SUI and for top X
    comp_data_sui = combined_df_sui[
        combined_df_sui['competitorid'] == selected_competitor_sui
    ][['fisyearathlete', col_name]].rename(columns={'fisyearathlete': 'fisyear'}).sort_values(by='fisyear')

    comp_data_topX = fisyear_pos[fisyear_pos['competitorid'] == selected_competitor_topX].sort_values(by='fisyear')

    # Calculate statistics for grouped data using the helper function
    df_grouped = calculate_statistics(fisyear_pos, col_name)

    # Create a line plot and add traces using the helper function for top X data
    fig = go.Figure()
    fig = plot_fisyear_data(
        fig=fig,
        df_grouped=df_grouped,
        comp_data=comp_data_topX,
        competitor_name=competitor_mapping_topX[selected_competitor_topX],
        col_name=col_name,
        disciplin=disciplin,
        use_log_scale=use_log_scale
    )

    # Add trace for SUI competitor if available
    if not comp_data_sui.empty:
        fig.add_trace(go.Scatter(
            name=f"{competitor_mapping_sui[selected_competitor_sui]} (SUI)",
            x=comp_data_sui['fisyear'],
            y=comp_data_sui[col_name],
            mode='lines+markers',
            marker=dict(color='gray', size=10),
            line=dict(color='gray', dash='dash')
        ))

    st.plotly_chart(fig)


#------------------------------------------------------------Athlete - All Disciplines - Development------------------------------------------------------------
if selected == "Athlete - All Disciplines - Development":
    st.markdown("<h3><span style='color:blue;'>TopX</span><span style='color:#4a0a13;'> vs Swiss</span></h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        Gender = st.selectbox("Select Gender:", options=['M', 'W'], index=0)
    with col2:
        top = st.number_input("Select Top X International:", value=30, min_value=10, max_value=100)

    # Load the data
    combined_df = load_combined_data(path_latest_fis_list_combinded)
    combined_df.columns = combined_df.columns.str.lower()
    df_FIS_list = get_latest_fis_list()

    # Filter the FIS list DataFrame to include only rows matching the selected gender and nationcode "SUI"
    df_FIS_list = df_FIS_list[
        (df_FIS_list["gender"].str.upper() == Gender.upper()) & 
        (df_FIS_list["nationcode"] == "SUI")
    ]

    ### Format:
    combined_df['listname'] = combined_df['listname'].astype(str)
    combined_df['listyear'] = (
        combined_df['listname']
        .str[-4:]
        .replace("4/25", "2025")
    )
    combined_df['listyear'] = pd.to_numeric(combined_df['listyear'], errors='coerce').fillna(0).astype(int)
    combined_df['birthyear'] = pd.to_numeric(combined_df['birthyear'], errors='coerce').fillna(0).astype(int)
    # Instead of using 'fisyearathlete', use 'athleteage'
    combined_df['athleteage'] = combined_df['listyear'] - combined_df['birthyear']
    combined_df['athleteage'] = combined_df['athleteage'].clip(lower=0).astype(int)
    df_FIS_list['competitorid'] = df_FIS_list['competitorid'].astype(str)
    combined_df['competitorid'] = combined_df['competitorid'].astype(str)
    combined_df.columns = combined_df.columns.str.lower()

    # Filter combined_df for SUI athletes
    combined_df_sui = combined_df[combined_df["nationcode"] == "SUI"]
    combined_df_sui = combined_df_sui[combined_df_sui["gender"].str.upper() == Gender.upper()]

    # Prepare competitor selection: only SUI athlete selection is needed (applies to all disciplines)
    competitors_sui = combined_df_sui[['competitorid', 'competitorname']].drop_duplicates()
    competitor_mapping_sui = competitors_sui.set_index("competitorid")["competitorname"].to_dict()
    default_index = list(competitor_mapping_sui.values()).index("ODERMATT Marco") if "ODERMATT Marco" in competitor_mapping_sui.values() else 0
    selected_competitor_sui = st.selectbox(
        "Select SUI Athlete",
        list(competitor_mapping_sui.keys()),
        index=default_index,
        format_func=lambda cid: competitor_mapping_sui[cid]
    )
    default_index = list(competitor_mapping_sui.values()).index("VON ALLMEN Franjo") if "VON ALLMEN Franjo" in competitor_mapping_sui.values() else 0
    selected_competitor_sui2 = st.selectbox(
        "Select another SUI Athlete",
        list(competitor_mapping_sui.keys()),
        format_func=lambda cid: competitor_mapping_sui[cid],
        index=default_index,
        key="second_competitor"
    )

    # Define disciplines and create a 2x2 grid for graphs
    disciplines = ['DH', 'SG', 'SL', 'GS']
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)
    grid = [row1_col1, row1_col2, row2_col1, row2_col2]

    # Define a color mapping for disciplines
    color_map = {
        'DH': {'line': 'rgb(255, 204, 0)', 'fill': 'rgba(255, 204, 0, 0.2)'},
        'SG': {'line': 'green', 'fill': 'rgba(0,128,0,0.2)'},
        'SL': {'line': 'blue', 'fill': 'rgba(0,0,255,0.2)'},
        'GS': {'line': 'rgb(235, 52, 201)', 'fill': 'rgba(235, 52, 201, 0.2)'},
    }

    # ... inside the for loop for individual discipline plots ...
    for idx, disciplin in enumerate(disciplines):
        with grid[idx]:
            st.markdown(f"### {disciplin} Position")
            col_name = f"{disciplin.lower()}pos"
            # Get the top X athletes for this discipline
            df_topX = df_FIS_list.nsmallest(top, col_name)[["competitorid", "competitorname"]]
            
            # Use athleteage (instead of fisyearathlete) for the x-axis:
            age_pos = combined_df[
                combined_df['competitorid'].isin(df_topX['competitorid'])
            ][['athleteage', 'competitorid', col_name, 'listyear']].dropna(subset=[col_name]).copy()
            # Rename athleteage to 'fisyear' so that helper functions work as expected
            age_pos.rename(columns={'athleteage':'fisyear'}, inplace=True)
            
            # Get competitor-specific data for first SUI athlete using athleteage
            comp_data_sui = combined_df_sui[
                (combined_df_sui['competitorid'] == selected_competitor_sui)
            ][['athleteage', col_name]].rename(columns={'athleteage': 'fisyear'}).sort_values(by='fisyear')
            
            # Calculate statistics for grouped data (grouping on the new 'fisyear' column which is athleteage)
            df_grouped = calculate_statistics(age_pos, col_name)
            
            # Determine the color based on discipline
            if disciplin in color_map:
                line_color = color_map[disciplin]['line']
                fill_color = color_map[disciplin]['fill']
            else:
                line_color = 'blue'
                fill_color = 'rgba(0,0,255,0.2)'
            
            # Create a line plot with a normal (non-inverted) y-axis using athleteage for the x-axis
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                name='Mean',
                x=df_grouped['fisyear'],
                y=df_grouped['mean'],
                mode='lines+markers',
                line=dict(color=line_color, width=4)
            ))
            fig.add_trace(go.Scatter(
                name='Upper Bound',
                x=df_grouped['fisyear'],
                y=df_grouped['upper'],
                mode='lines',
                line=dict(width=0, color=line_color),
                showlegend=False
            ))
            fig.add_trace(go.Scatter(
                name='Lower Bound',
                x=df_grouped['fisyear'],
                y=df_grouped['lower'],
                mode='lines',
                line=dict(width=0),
                fill='tonexty',
                fillcolor=fill_color,
                showlegend=False
            ))
            # Add trace for first SUI competitor (dashed lines)
            if not comp_data_sui.empty:
                fig.add_trace(go.Scatter(
                    name=f"{competitor_mapping_sui[selected_competitor_sui]} (SUI)",
                    x=comp_data_sui['fisyear'],
                    y=comp_data_sui[col_name],
                    mode='lines+markers',
                    marker=dict(color='gray', size=10),
                    line=dict(color='gray', dash='dash')
                ))
            # Get competitor-specific data for second SUI athlete using athleteage
            comp_data_sui2 = combined_df_sui[
                (combined_df_sui['competitorid'] == selected_competitor_sui2)
            ][['athleteage', col_name]].rename(columns={'athleteage': 'fisyear'}).sort_values(by='fisyear')
            # Add trace for second SUI competitor (dotted lines)
            if not comp_data_sui2.empty:
                fig.add_trace(go.Scatter(
                    name=f"{competitor_mapping_sui[selected_competitor_sui2]} (SUI 2)",
                    x=comp_data_sui2['fisyear'],
                    y=comp_data_sui2[col_name],
                    mode='lines+markers',
                    marker=dict(color='rgb(40,40,40)', size=10, symbol='square'),
                    line=dict(color='rgb(40,40,40)', dash='dot')
                ))
            
            fig.update_layout(
                title=f"{disciplin} Position vs Athlete Age",
                xaxis_title='Athlete Age',
                yaxis_title=f"{disciplin} Position",
                yaxis_type="linear"
            )
            st.plotly_chart(fig)

    # --- Combined Plot (All Disciplines Mean Only) ---
    fig_combined = go.Figure()
    for disciplin in ['DH', 'SG', 'SL', 'GS']:
        col_name = f"{disciplin.lower()}pos"
        # Get the top X athletes for this discipline
        df_topX = df_FIS_list.nsmallest(top, col_name)[["competitorid", "competitorname"]]
        age_pos = combined_df[
            combined_df['competitorid'].isin(df_topX['competitorid'])
        ][['athleteage', 'competitorid', col_name, 'listyear']].dropna(subset=[col_name]).copy()
        age_pos.rename(columns={'athleteage': 'fisyear'}, inplace=True)
        
        # Calculate grouped statistics (mean only)
        df_grouped = calculate_statistics(age_pos, col_name)
        
        # Determine the color based on discipline
        if disciplin in color_map:
            line_color = color_map[disciplin]['line']
        else:
            line_color = 'blue'
        
        # Add trace for the discipline mean using athlete age for the x-axis
        fig_combined.add_trace(go.Scatter(
            name=f"{disciplin} Mean",
            x=df_grouped['fisyear'],
            y=df_grouped['mean'],
            mode='lines+markers',
            line=dict(color=line_color, width=2)
        ))
        
        # Get competitor-specific data for SUI for the current discipline, using athleteage
        comp_data_sui = combined_df_sui[
            combined_df_sui['competitorid'] == selected_competitor_sui
        ][['athleteage', col_name]].rename(columns={'athleteage': 'fisyear'}).sort_values(by='fisyear')
        
        # Add trace for SUI competitor if data exists, with dashed line
        if not comp_data_sui.empty:
            fig_combined.add_trace(go.Scatter(
                name=f"{disciplin} {competitor_mapping_sui[selected_competitor_sui]} (SUI)",
                x=comp_data_sui['fisyear'],
                y=comp_data_sui[col_name],
                mode='lines+markers',
                marker=dict(size=10),
                line=dict(color=line_color, dash='dash')
            ))

        # Get competitor-specific data for second SUI athlete, using athleteage
        comp_data_sui2 = combined_df_sui[
            combined_df_sui['competitorid'] == selected_competitor_sui2
        ][['athleteage', col_name]].rename(columns={'athleteage': 'fisyear'}).sort_values(by='fisyear')

        # Add trace for second SUI competitor with dotted line
        if not comp_data_sui2.empty:
            fig_combined.add_trace(go.Scatter(
                name=f"{disciplin} {competitor_mapping_sui[selected_competitor_sui2]} (SUI 2)",
                x=comp_data_sui2['fisyear'],
                y=comp_data_sui2[col_name],
                mode='lines+markers',
                marker=dict(size=10, symbol='square'),
                line=dict(dash='dot')
            ))

    fig_combined.update_layout(
        title="Combined Mean Position vs Athlete Age (All Disciplines)",
        xaxis_title="Athlete Age",
        yaxis_title="Position",
        yaxis_type="linear"
    )

    st.plotly_chart(fig_combined)

