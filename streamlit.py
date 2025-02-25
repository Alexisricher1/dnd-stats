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
engine = create_engine('sqlite:///C:/Users/Alexis/Documents/DND/ROLL20_DB.db', echo=True)  # Change the database URL as needed

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

def damage_analysis():
    st.header('Analyse des dégâts')
    
    # Get damage rolls data with character filter
    execute = text(f"""
        SELECT p.player_name, p.player_class, d.dice_type, d.nat_roll_value, d.modifier, 
               d.total_roll_value, d.action_name, d.full_message
        FROM DICE_ROLLS d
        JOIN PLAYER p ON d.PLAYER_ID = p.PLAYER_ID
        WHERE d.DICE_TYPE != '1d20' 
        AND (d.ACTION_TYPE IS NULL OR d.ACTION_TYPE != 'saving throw')
        AND {CHARACTERS_FILTER_SQL}
        ORDER BY p.player_name, d.DICE_ROLL_ID
    """)
    result = session.execute(execute)
    
    # Convert to DataFrame
    columns = ['player_name', 'player_class', 'dice_type', 'nat_roll_value', 'modifier', 
               'total_roll_value', 'action_name', 'full_message']
    damage_df = pd.DataFrame(result.fetchall(), columns=columns)
    
    if damage_df.empty:
        st.warning("Aucun jet de dégâts trouvé dans la base de données.")
        return
    
    # Convert modifier to numeric, replacing non-numeric values with 0
    damage_df['modifier'] = pd.to_numeric(damage_df['modifier'], errors='coerce').fillna(0)
    
    # Try to extract damage types from full_message using regex patterns
    def extract_damage_type(message):
        if not message:
            return "Unknown"
        
        # Common damage types in D&D
        damage_types = ['acid', 'bludgeoning', 'cold', 'fire', 'force', 'lightning', 
                        'necrotic', 'piercing', 'poison', 'psychic', 'radiant', 
                        'slashing', 'thunder', 'sneak attack']
        
        # Convert to lowercase for case-insensitive matching
        message_lower = message.lower()
        
        # Check for each damage type
        for damage_type in damage_types:
            if damage_type in message_lower:
                return damage_type.capitalize()
        
        return "Unknown"
    
    # Apply the function to extract damage types
    damage_df['damage_type'] = damage_df['full_message'].apply(extract_damage_type)
    
    # Extract dice information
    def parse_dice_type(dice_type):
        if not dice_type or pd.isna(dice_type):
            return 0, 0
        
        match = re.match(r'(\d+)d(\d+)', dice_type)
        if match:
            num_dice = int(match.group(1))
            dice_sides = int(match.group(2))
            return num_dice, dice_sides
        return 0, 0
    
    # Apply the function to extract dice info
    damage_df['num_dice'], damage_df['dice_sides'] = zip(*damage_df['dice_type'].apply(parse_dice_type))
    
    # Filter out rows with invalid dice info
    damage_df = damage_df[(damage_df['num_dice'] > 0) & (damage_df['dice_sides'] > 0)]
    
    if damage_df.empty:
        st.warning("Aucun jet de dégâts valide trouvé après filtrage.")
        return
    
    # Ensure all numeric columns are actually numeric
    numeric_columns = ['nat_roll_value', 'modifier', 'total_roll_value', 'num_dice', 'dice_sides']
    for col in numeric_columns:
        damage_df[col] = pd.to_numeric(damage_df[col], errors='coerce').fillna(0)
    
    # Calculate theoretical average damage per die type
    damage_df['theoretical_avg'] = damage_df['num_dice'] * (damage_df['dice_sides'] + 1) / 2 + damage_df['modifier']
    
    # Calculate efficiency (actual vs theoretical)
    # Avoid division by zero
    damage_df['efficiency'] = np.where(
        damage_df['theoretical_avg'] > 0,
        (damage_df['total_roll_value'] / damage_df['theoretical_avg'] * 100).round(2),
        100  # Default to 100% if theoretical average is 0
    )
    
    # Overview statistics
    st.subheader(f'Statistiques générales de dégâts (Joueurs filtrés: {", ".join(FILTERED_CHARACTERS)})')
    
    # Group by player and calculate stats
    player_damage_stats = damage_df.groupby('player_name').agg({
        'total_roll_value': ['count', 'sum', 'mean', 'min', 'max'],
        'efficiency': ['mean']
    }).reset_index()
    
    # Flatten the multi-index columns
    player_damage_stats.columns = ['player_name', 'roll_count', 'total_damage', 'avg_damage', 
                                  'min_damage', 'max_damage', 'avg_efficiency']
    
    # Round numeric columns
    numeric_cols = player_damage_stats.columns.drop('player_name')
    player_damage_stats[numeric_cols] = player_damage_stats[numeric_cols].round(2)
    
    # Create a bar chart for total damage dealt
    total_damage_chart = alt.Chart(player_damage_stats).mark_bar().encode(
        x=alt.X('player_name:N', title='Joueur', sort='-y'),
        y=alt.Y('total_damage:Q', title='Dégâts totaux'),
        color=alt.Color('player_name:N', legend=None),
        tooltip=['player_name', 'roll_count', 'total_damage', 'avg_damage', 'avg_efficiency']
    ).properties(
        width=600,
        height=400,
        title='Dégâts totaux par joueur'
    )
    
    st.altair_chart(total_damage_chart, use_container_width=True)
    
    # Create a bar chart for average damage per roll
    avg_damage_chart = alt.Chart(player_damage_stats).mark_bar().encode(
        x=alt.X('player_name:N', title='Joueur', sort='-y'),
        y=alt.Y('avg_damage:Q', title='Dégâts moyens par jet'),
        color=alt.Color('player_name:N', legend=None),
        tooltip=['player_name', 'roll_count', 'avg_damage', 'min_damage', 'max_damage']
    ).properties(
        width=600,
        height=400,
        title='Dégâts moyens par joueur'
    )
    
    st.altair_chart(avg_damage_chart, use_container_width=True)
    
    # Display detailed stats table
    st.subheader('Statistiques détaillées par joueur')
    st.dataframe(player_damage_stats.set_index('player_name'), use_container_width=True)
    
    # Damage by dice type analysis
    st.subheader('Analyse par type de dé')
    
    # Group by dice type
    dice_type_stats = damage_df.groupby('dice_type').agg({
        'total_roll_value': ['count', 'mean', 'sum'],
        'efficiency': ['mean']
    }).reset_index()
    
    # Flatten the multi-index columns
    dice_type_stats.columns = ['dice_type', 'roll_count', 'avg_damage', 'total_damage', 'avg_efficiency']
    
    # Round numeric columns
    numeric_cols = dice_type_stats.columns.drop('dice_type')
    dice_type_stats[numeric_cols] = dice_type_stats[numeric_cols].round(2)
    
    # Sort by total damage
    dice_type_stats = dice_type_stats.sort_values('total_damage', ascending=False)
    
    # Create a bar chart for damage by dice type
    dice_damage_chart = alt.Chart(dice_type_stats).mark_bar().encode(
        x=alt.X('dice_type:N', title='Type de dé', sort='-y'),
        y=alt.Y('total_damage:Q', title='Dégâts totaux'),
        color=alt.Color('dice_type:N', legend=None),
        tooltip=['dice_type', 'roll_count', 'avg_damage', 'total_damage', 'avg_efficiency']
    ).properties(
        width=600,
        height=400,
        title='Dégâts totaux par type de dé'
    )
    
    st.altair_chart(dice_damage_chart, use_container_width=True)
    
    # Display dice type stats table
    st.dataframe(dice_type_stats.set_index('dice_type'), use_container_width=True)
    
    # Damage by damage type analysis
    st.subheader('Analyse par type de dégâts')
    
    # Group by damage type
    damage_type_stats = damage_df.groupby('damage_type').agg({
        'total_roll_value': ['count', 'mean', 'sum'],
    }).reset_index()
    
    # Flatten the multi-index columns
    damage_type_stats.columns = ['damage_type', 'roll_count', 'avg_damage', 'total_damage']
    
    # Round numeric columns
    numeric_cols = damage_type_stats.columns.drop('damage_type')
    damage_type_stats[numeric_cols] = damage_type_stats[numeric_cols].round(2)
    
    # Sort by total damage
    damage_type_stats = damage_type_stats.sort_values('total_damage', ascending=False)
    
    # Create a bar chart for damage by damage type
    damage_type_chart = alt.Chart(damage_type_stats).mark_bar().encode(
        x=alt.X('damage_type:N', title='Type de dégâts', sort='-y'),
        y=alt.Y('total_damage:Q', title='Dégâts totaux'),
        color=alt.Color('damage_type:N', legend=None),
        tooltip=['damage_type', 'roll_count', 'avg_damage', 'total_damage']
    ).properties(
        width=600,
        height=400,
        title='Dégâts totaux par type de dégâts'
    )
    
    st.altair_chart(damage_type_chart, use_container_width=True)
    
    # Display damage type stats table
    st.dataframe(damage_type_stats.set_index('damage_type'), use_container_width=True)
    
    # Efficiency analysis
    st.subheader('Analyse d\'efficacité des jets de dégâts')
    
    # Create a box plot for damage roll efficiency by player
    efficiency_chart = alt.Chart(damage_df).mark_boxplot().encode(
        x=alt.X('player_name:N', title='Joueur'),
        y=alt.Y('efficiency:Q', title='Efficacité (%)', scale=alt.Scale(zero=False)),
        color='player_name:N'
    ).properties(
        width=600,
        height=400,
        title='Distribution de l\'efficacité des jets de dégâts par joueur'
    )
    
    st.altair_chart(efficiency_chart, use_container_width=True)
    
    # Create a histogram of efficiency values
    efficiency_hist = alt.Chart(damage_df).mark_bar().encode(
        x=alt.X('efficiency:Q', bin=alt.Bin(step=10), title='Efficacité (%)'),
        y=alt.Y('count():Q', title='Nombre de jets'),
        color='player_name:N',
        tooltip=['player_name', 'count()']
    ).properties(
        width=600,
        height=400,
        title='Distribution de l\'efficacité des jets de dégâts'
    )
    
    st.altair_chart(efficiency_hist, use_container_width=True)
    
    # Top damage rolls
    st.subheader('Top 10 des jets de dégâts les plus élevés')
    
    # Sort by total damage and get top 10
    top_damage_rolls = damage_df.sort_values('total_roll_value', ascending=False).head(10)
    
    # Create a table with the top damage rolls
    top_damage_table = top_damage_rolls[['player_name', 'dice_type', 'nat_roll_value', 
                                        'modifier', 'total_roll_value', 'damage_type', 'action_name']]
    
    st.dataframe(top_damage_table, use_container_width=True)

if selected_table == 'Analyse de distribution D20':
    d20_distribution_analysis()
elif selected_table == 'Critical 1d20 fail':
    crit_1d20_fail_graph()
elif selected_table == 'Critical 1d20 success':
    crit_1d20_success_graph()
elif selected_table == 'Critical 1d20 joueurs':
    crit_1d20_players_graph()
elif selected_table == 'Analyse des dégâts':
    damage_analysis()
    

    # elif query_type == 'Custom Query':
    #     # User input for custom SQL query
    #     custom_query = st.text_area('Enter custom SQL query:')
    #     if st.button('Run Query'):
    #         try:
    #             result = session.execute(text(custom_query))
    #             st.dataframe(result.fetchall())
    #         except Exception as e:
    #             st.error(f'Error executing query: {e}')
