import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, Text, ForeignKey, text
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import altair as alt
import numpy as np
import re


# Create an engine
#sqlite:///C:/Users/Alexis/Documents/DND/ROLL20_DB.db
engine = create_engine('sqlite:///./ROLL20_DB.db', echo=True)  # Change the database URL as needed

# Create a base class for declarative class definitions
Base = declarative_base()

# Create the tables in the database
Base.metadata.create_all(engine)

# Create a session maker
Session = sessionmaker(bind=engine)
session = Session()

# Define the list of characters to include in the analysis
FILTERED_CHARACTERS = ["Gleditschia", "Oskar", "Kirgi", "Miron", "Netari", "Kukaccar"]
CHARACTERS_FILTER_SQL = "p.player_name IN ('{}')".format("', '".join(FILTERED_CHARACTERS))

# Define the DiceRolls class representing the DICE_ROLLS table
class DiceRolls(Base):
    __tablename__ = 'DICE_ROLLS'

    DICE_ROLL_ID = Column(Integer, primary_key=True, autoincrement=True)
    NAT_ROLL_VALUE = Column(Integer)
    TOTAL_ROLL_VALUE = Column(Integer)
    ACTION_TYPE = Column(Text)
    ACTION_NAME = Column(Text)
    DICE_TYPE = Column(Text)
    MODIFIER = Column(Integer)
    IS_CRITICAL_FAIL = Column(Integer)
    IS_CRITICAL_HIT = Column(Integer)
    FULL_MESSAGE = Column(Text)
    PLAYER_ID = Column(Integer, ForeignKey('PLAYER.PLAYER_ID'))  # Reference PLAYER_ID

    # Define a relationship with the Player class (assuming it's defined elsewhere)
    player = relationship("Player", back_populates="dice_rolls")

# Define the Player class representing the PLAYER table
class Player(Base):
    __tablename__ = 'PLAYER'

    PLAYER_ID = Column(Integer, primary_key=True, autoincrement=True)
    PLAYER_NAME = Column(Text)
    PLAYER_CLASS = Column(Text)
    # Add other columns as needed
    dice_rolls = relationship("DiceRolls", back_populates="player")

# Define the REJECTED table class
class Rejected(Base):
    __tablename__ = 'REJECTED'
    REJECT_ID = Column(Integer, primary_key=True, autoincrement=True)
    HTML = Column(Text)

# Create the tables in the database
Base.metadata.create_all(engine)

# Sidebar for selecting table and query options
st.sidebar.title('Query Options')
selected_table = st.sidebar.selectbox('Select table to query:', ['Analyse de distribution D20', 'Critical 1d20 fail', 'Critical 1d20 success', 'Critical 1d20 joueurs', 'Analyse des dégâts'])

# Display filtered characters in sidebar
st.sidebar.markdown("### Personnages filtrés")
st.sidebar.markdown(", ".join(FILTERED_CHARACTERS))

# Main content area
st.title('D&D')



def crit_1d20_fail_graph():
    st.header('Critical 1d20 fail')

    # Execute the SQL query with character filter
    execute = text(f"""
        SELECT DISTINCT p.player_id, p.player_name, d.DICE_TYPE, COUNT(p.player_name) AS count
        FROM DICE_ROLLS d
        LEFT JOIN PLAYER p ON d.PLAYER_ID = p.PLAYER_ID
        WHERE nat_roll_value = 1 AND d.DICE_TYPE = '1d20'
        AND {CHARACTERS_FILTER_SQL}
        GROUP BY p.player_id;
    """)
    result = session.execute(execute)
    
    # Convert the result to a DataFrame
    columns = ['player_id', 'player_name', 'dice_type', 'count']
    dice_rolls_df = pd.DataFrame(result.fetchall(), columns=columns).sort_values(by="count", ascending=False)

    # Display a horizontal bar chart using Streamlit with player names on the x-axis
    #st.bar_chart(dice_rolls_df.set_index('player_name')['count'], use_container_width=True, height=600)
    
    st.altair_chart(alt.Chart(dice_rolls_df).mark_bar().encode(
        x=alt.X('player_name', sort=None, title="Joueurs"),
        y=alt.Y('count', title="Nombre de crit fails"),
    ), use_container_width=True)
    
    st.text(f'Nombre total de lancés critical fail : {dice_rolls_df["count"].sum()}')
    
    st.divider()

        # Display the DataFrame if needed
        # if not dice_rolls_df.empty:
        #     st.dataframe(dice_rolls_df)
        # else:
        #     st.write('No data found in the Dice Rolls table.')
            
def crit_1d20_success_graph():
    st.header('Critical 1d20 hit')
    # Execute the SQL query with character filter
    execute = text(f"""
        SELECT DISTINCT p.player_id, p.player_name, d.DICE_TYPE, COUNT(p.player_name) AS count
        FROM DICE_ROLLS d
        LEFT JOIN PLAYER p ON d.PLAYER_ID = p.PLAYER_ID
        WHERE nat_roll_value = 20 AND d.DICE_TYPE = '1d20'
        AND {CHARACTERS_FILTER_SQL}
        GROUP BY p.player_id;
    """)
    result = session.execute(execute)

    # Convert the result to a DataFrame
    columns = ['player_id', 'player_name', 'dice_type', 'count']
    dice_rolls_df = pd.DataFrame(result.fetchall(), columns=columns).sort_values(by="count", ascending=False)

    # Display a horizontal bar chart using Streamlit with player names on the x-axis
    #st.bar_chart(dice_rolls_df.set_index('player_name')['count'], use_container_width=True, height=600)
    
    st.altair_chart(alt.Chart(dice_rolls_df).mark_bar().encode(
        x=alt.X('player_name', sort=None, title="Joueurs"),
        y=alt.Y('count', title="Nombre de crit success"),
    ), use_container_width=True)
    
    st.text(f'Nombre total de lancés critical success : {dice_rolls_df["count"].sum()}')
    
    st.divider()

        # Display the DataFrame if needed
        # if not dice_rolls_df.empty:
        #     st.dataframe(dice_rolls_df)
        # else:
        #     st.write('No data found in the Dice Rolls table.')
        
        
def crit_1d20_players_graph():
    st.header('Statistiques pour 1d20')
    # Execute the SQL query with character filter
    execute = text(f"""
SELECT p.player_id, p.player_name, d.nat_roll_value, COUNT(d.dice_type) as DICE_ROLL_COUNT
FROM DICE_ROLLS d
LEFT JOIN player p ON d.PLAYER_ID = p.PLAYER_ID
WHERE d.DICE_TYPE = '1d20'
AND {CHARACTERS_FILTER_SQL}
GROUP BY p.player_id, p.player_name, d.nat_roll_value
    """)
    result = session.execute(execute)

    # Convert the result to a DataFrame
    columns = ['player_id', 'player_name', 'nat_roll_value', 'dice_roll_count']
    dice_rolls_df = pd.DataFrame(result.fetchall(), columns=columns)
    #st.bar_chart(dice_rolls_df.set_index('dice_roll_count'), use_container_width=True, height=600)

    # Create individual bar charts for each player
    for player in dice_rolls_df['player_name'].unique():
        player_data = dice_rolls_df[dice_rolls_df['player_name'] == player]
        st.subheader(f'{player}')
        
        chart_data = pd.DataFrame(
            {
                "Dice_Roll_Count": player_data["dice_roll_count"],
                "Dice_Roll_Value": player_data["nat_roll_value"],
            }
        )
        
        # Custom color gradient function
        def get_color(value, cmap_name='viridis'):
            cmap = plt.get_cmap(cmap_name)
            norm = mcolors.Normalize(vmin=1, vmax=20)  # Adjust the range based on your data
            return mcolors.to_hex(cmap(norm(value)))

        # Get colors for each bar based on Dice_Roll_Value
        colors = [get_color(value) for value in chart_data['Dice_Roll_Count']]

        # Plot the bar chart with a color gradient for each bar
        st.bar_chart(chart_data, x="Dice_Roll_Value", y="Dice_Roll_Count")
        st.text(f'Nombre total de lancés : {player_data["dice_roll_count"].sum()}')
        
        st.divider()
            
            
            #st.bar_chart(player_data.set_index('nat_roll_value'), use_container_width=True)
            #st.dataframe(player_data)

        # Display a horizontal bar chart using Streamlit with player names on the x-axis
        

        # Display the DataFrame if needed
        # if not dice_rolls_df.empty:
        #     st.dataframe(dice_rolls_df)
        # else:
        #     st.write('No data found in the Dice Rolls table.')

def d20_distribution_analysis():
    st.header('Analyse de distribution des lancés de d20')

    # Get total rolls per value for filtered players
    execute = text(f"""
        SELECT d.nat_roll_value, COUNT(*) as roll_count
        FROM DICE_ROLLS d
        JOIN PLAYER p ON d.PLAYER_ID = p.PLAYER_ID
        WHERE d.DICE_TYPE = '1d20'
        AND {CHARACTERS_FILTER_SQL}
        GROUP BY d.nat_roll_value
        ORDER BY d.nat_roll_value
    """)
    result = session.execute(execute)
    
    # Convert to DataFrame
    columns = ['nat_roll_value', 'roll_count']
    roll_dist_df = pd.DataFrame(result.fetchall(), columns=columns)
    
    # Calculate total rolls and expected counts
    total_rolls = roll_dist_df['roll_count'].sum()
    expected_per_value = total_rolls / 20  # For a fair d20, each value should appear 5% of the time
    
    # Add expected count and ratio columns
    roll_dist_df['expected_count'] = expected_per_value
    roll_dist_df['ratio_to_expected'] = roll_dist_df['roll_count'] / roll_dist_df['expected_count']
    
    # Create a combined chart showing actual vs expected distribution
    st.subheader(f'Distribution des valeurs de d20 (Joueurs filtrés: {", ".join(FILTERED_CHARACTERS)})')
    
    # Bar chart of actual counts
    chart = alt.Chart(roll_dist_df).mark_bar().encode(
        x=alt.X('nat_roll_value:O', title='Valeur du dé'),
        y=alt.Y('roll_count:Q', title='Nombre de lancés'),
        tooltip=['nat_roll_value', 'roll_count', 'ratio_to_expected']
    ).properties(
        width=600,
        height=400
    )
    
    # Line for expected counts
    expected_line = alt.Chart(roll_dist_df).mark_line(color='red').encode(
        x='nat_roll_value:O',
        y='expected_count:Q'
    )
    
    # Display the combined chart
    st.altair_chart(chart + expected_line, use_container_width=True)
    
    # Display ratio chart
    ratio_chart = alt.Chart(roll_dist_df).mark_bar().encode(
        x=alt.X('nat_roll_value:O', title='Valeur du dé'),
        y=alt.Y('ratio_to_expected:Q', title='Ratio (Observé/Attendu)'),
        color=alt.condition(
            alt.datum.ratio_to_expected > 1,
            alt.value('green'),  # The positive color
            alt.value('red')     # The negative color
        ),
        tooltip=['nat_roll_value', 'roll_count', 'ratio_to_expected']
    ).properties(
        width=600,
        height=400
    )
    
    # Add a horizontal line at ratio = 1 (perfect distribution)
    baseline = alt.Chart(pd.DataFrame({'y': [1]})).mark_rule(color='black', strokeDash=[3, 3]).encode(y='y')
    
    st.subheader('Ratio des valeurs observées par rapport aux valeurs attendues')
    st.altair_chart(ratio_chart + baseline, use_container_width=True)
    
    # Calculate chi-square statistic to test for fairness
    chi_square = np.sum(((roll_dist_df['roll_count'] - roll_dist_df['expected_count']) ** 2) / roll_dist_df['expected_count'])
    degrees_of_freedom = 19  # 20 possible outcomes - 1
    
    # Display statistics
    st.subheader('Statistiques de distribution')
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total des lancés", f"{total_rolls}")
    with col2:
        st.metric("Valeur attendue par face", f"{expected_per_value:.1f}")
    with col3:
        st.metric("Chi-square", f"{chi_square:.2f}")
        
    # Interpretation of chi-square
    st.write("""
    **Interprétation du Chi-square:**
    - Une valeur proche de 0 indique une distribution très proche de l'attendu (dé équilibré)
    - Une valeur élevée (>30 pour un d20) suggère une distribution non aléatoire
    """)
    
    # Per-player analysis
    st.subheader('Analyse par joueur')
    
    # Get player-specific distributions with character filter
    execute = text(f"""
        SELECT p.player_name, d.nat_roll_value, COUNT(*) as roll_count
        FROM DICE_ROLLS d
        JOIN PLAYER p ON d.PLAYER_ID = p.PLAYER_ID
        WHERE d.DICE_TYPE = '1d20'
        AND {CHARACTERS_FILTER_SQL}
        GROUP BY p.player_name, d.nat_roll_value
        ORDER BY p.player_name, d.nat_roll_value
    """)
    result = session.execute(execute)
    
    # Convert to DataFrame
    columns = ['player_name', 'nat_roll_value', 'roll_count']
    player_dist_df = pd.DataFrame(result.fetchall(), columns=columns)
    
    # Calculate player totals
    player_totals = player_dist_df.groupby('player_name')['roll_count'].sum().reset_index()
    player_totals.columns = ['player_name', 'total_rolls']
    
    # Merge back to get player totals
    player_dist_df = pd.merge(player_dist_df, player_totals, on='player_name')
    
    # Calculate expected counts and ratios
    player_dist_df['expected_count'] = player_dist_df['total_rolls'] / 20
    player_dist_df['ratio_to_expected'] = player_dist_df['roll_count'] / player_dist_df['expected_count']
    
    # Display player-specific ratio charts
    for player in player_dist_df['player_name'].unique():
        player_data = player_dist_df[player_dist_df['player_name'] == player]
        
        # Ensure we have all values 1-20 (fill missing with 0)
        all_values = pd.DataFrame({'nat_roll_value': range(1, 21)})
        player_data = pd.merge(all_values, player_data, on='nat_roll_value', how='left').fillna({
            'player_name': player,
            'roll_count': 0,
            'total_rolls': player_data['total_rolls'].iloc[0] if not player_data.empty else 0,
            'expected_count': player_data['expected_count'].iloc[0] if not player_data.empty else 0,
            'ratio_to_expected': 0
        })
        
        st.write(f"**{player}** (Total: {int(player_data['total_rolls'].iloc[0])} lancés)")
        
        # Create ratio chart for this player
        player_ratio_chart = alt.Chart(player_data).mark_bar().encode(
            x=alt.X('nat_roll_value:O', title='Valeur du dé'),
            y=alt.Y('ratio_to_expected:Q', title='Ratio (Observé/Attendu)'),
            color=alt.condition(
                alt.datum.ratio_to_expected > 1,
                alt.value('green'),
                alt.value('red')
            ),
            tooltip=['nat_roll_value', 'roll_count', 'ratio_to_expected']
        ).properties(
            width=600,
            height=300
        )
        
        # Calculate chi-square for this player
        chi_square = np.sum(((player_data['roll_count'] - player_data['expected_count']) ** 2) / 
                            player_data['expected_count'].replace(0, 1))  # Avoid division by zero
        
        # Display the chart with baseline
        st.altair_chart(player_ratio_chart + baseline, use_container_width=True)
        st.metric("Chi-square", f"{chi_square:.2f}")
        st.divider()


if selected_table == 'Analyse de distribution D20':
    d20_distribution_analysis()
elif selected_table == 'Critical 1d20 fail':
    crit_1d20_fail_graph()
elif selected_table == 'Critical 1d20 success':
    crit_1d20_success_graph()
elif selected_table == 'Critical 1d20 joueurs':
    crit_1d20_players_graph()
    

    # elif query_type == 'Custom Query':
    #     # User input for custom SQL query
    #     custom_query = st.text_area('Enter custom SQL query:')
    #     if st.button('Run Query'):
    #         try:
    #             result = session.execute(text(custom_query))
    #             st.dataframe(result.fetchall())
    #         except Exception as e:
    #             st.error(f'Error executing query: {e}')
