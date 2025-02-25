from sqlalchemy import create_engine, Column, Integer, Text, ForeignKey, Boolean, text
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
import re
from lxml import html, etree

# Create the SQLAlchemy engine
engine = create_engine('sqlite:///ROLL20_DB.db', echo=True)  # Change the database URL as needed

# Create a base class for declarative class definitions
Base = declarative_base()

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
    REASON = Column(Text)
    HTML = Column(Text)

# Create the tables in the database
Base.metadata.create_all(engine)

# Create a session maker
Session = sessionmaker(bind=engine)
session = Session()


# Function to check if a player with a given name exists
def player_exists(name):
    return session.query(Player).filter(Player.PLAYER_NAME == name).first()


def read_file_into_string(file_path):
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
        return file_content
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None


def extract_value_between_parentheses(input_string):
    # Use regular expression to match the value between the first pair of parentheses
    match = re.search(r'\((.*?)\)', input_string)

    if match:
        nat_roll_values = match.group(1)
        
        # if multiple dice rolls
        if len(nat_roll_values.split(' + ')) > 1:
            all_nat_roll_values = ''
            for roll in nat_roll_values:
                all_nat_roll_values += roll + ' '
            return all_nat_roll_values
        else:
            return nat_roll_values
    else:
        print("No value between parentheses found in the string")
        
def extract_dice_type_value(input_string):
    # Use regular expression to match the value between the first pair of parentheses
    match = re.search(r'\dd\d\d?', input_string)

    if match:
        return match.group(0)
    else:
        print("No dice_type value found in the string")


def sqlalchemy_add_char_get_id(char_name):
    # Create a new Player instance
    new_player = Player(
        PLAYER_NAME=char_name,
        PLAYER_CLASS=''
    )

    # Add the new_player to the session and commit the changes to the database
    session.add(new_player)
    session.commit()


# Example usage:
#file_path = 'dndlog.html'
#file_path = 'dndlog_test.html'
file_path = 'dndlog_avr2024.html'
file_content = read_file_into_string(file_path)

if file_content:
    print(file_content)
else:
    print("Failed to read file content.")
    
html_content = file_content
    
# Parse the HTML content
tree = html.fromstring(html_content)

# Try evaluating each part of the expression separately
general_messages = tree.xpath('//div[contains(@class, "message") and contains(@class, "general")]')  # Check if these exist
# print(len(general_messages))  # Check the number of messages

def delete_db_rows():
    # Define the SQL truncate queries for each table
    truncate_dice_rolls_query = text('DELETE FROM DICE_ROLLS')
    truncate_player_query = text('DELETE FROM PLAYER')
    truncate_rejected_query = text('DELETE FROM REJECTED')

    # Execute the truncate queries using the session
    session.execute(truncate_dice_rolls_query)
    session.execute(truncate_player_query)
    session.execute(truncate_rejected_query)

def extract_values():
    delete_db_rows()
    # If general messages exist, proceed
    if general_messages:
        try:
            for message in general_messages:
                print('-------------------')
                # character name
                character_name = message.xpath('.//div[contains(@class, "sheet-charname")]/span/text()')
                if character_name and len(character_name) > 0:
                    character_name = character_name[0]
                    player = player_exists(character_name)
                    if not player:
                        # Create a new Player instance and insert it into the database
                        player = Player(
                            PLAYER_NAME=character_name,
                            PLAYER_CLASS=''
                        )
                        # Add the new_player to the session
                        session.add(player)
                        # Commit the changes to generate the PLAYER_ID
                        session.commit()
                    print('character_name: ' + character_name)
                else:
                    rejected_entry = Rejected(HTML=etree.tostring(message, encoding='unicode', method='html'), REASON="NO_CHAR_NAME")
                    session.add(rejected_entry)
                    session.commit()
                    continue
                

                # natural roll value
                nat_roll_values_unparsed = message.xpath('.//span[contains(@class, "inlinerollresult")]/@title')
                if nat_roll_values_unparsed:
                    # if len(nat_roll_values_unparsed) > 1 and re.search('basicdiceroll', nat_roll_values_unparsed[0]):
                    #     # TODO: need work to  
                    #     # two types of damage like one handed or two handed.
                    #     # for nat_roll_value in nat_roll_values_unparsed:
                    #     #     damage_type = nat_roll_values_unparsed.xpath('.//span[contains(@class, "sheet-sublabel")]/text()')[0]
                    #     #     print('damage_type : ' + damage_type)
                    #     #     extract_value_between_parentheses(damage_type)
                    #     match = re.search('basicdiceroll', nat_roll_values_unparsed[0])
                    #     if match:
                    #         values = re.findall('(?<=>)\d\d?(?=</span)', nat_roll_values_unparsed[0])
                    #         if values:
                    #             # Convert the first value to an integer (assuming there's only one value)
                    #             nat_rolls = values[0]
                    # else:
                    #     nat_rolls = extract_value_between_parentheses(nat_roll_values_unparsed[0])
                        
                    #     if nat_rolls:
                    #         print("nat_rolls: " + nat_rolls)
                    #     else:
                    #         continue
                    
                    nat_rolls = extract_value_between_parentheses(nat_roll_values_unparsed[0])
                    
                    if nat_rolls:
                        print("nat_rolls: " + nat_rolls)
                        if re.search('basicdiceroll', nat_rolls):
                            match = re.search('basicdiceroll', nat_roll_values_unparsed[0])
                            if match:
                                values = re.findall('(?<=>)\d\d?(?=</span)', nat_roll_values_unparsed[0])
                                if values:
                                    # Convert the first value to an integer (assuming there's only one value)
                                    nat_rolls = values[0]
                    else:
                        rejected_entry = Rejected(HTML=etree.tostring(message, encoding='unicode', method='html'), REASON='.//span[contains(@class, "inlinerollresult")]/@title not found > basicdiceroll')
                        session.add(rejected_entry)
                        session.commit()
                        continue
                    
                else:
                    rejected_entry = Rejected(HTML=etree.tostring(message, encoding='unicode', method='html'), REASON='.//span[contains(@class, "inlinerollresult")]/@title not found')
                    session.add(rejected_entry)
                    session.commit()
                    continue
                
                # dice type and modifier value
                dice_title_unparsed = message.xpath('.//span[contains(@class, "inlinerollresult")]/@title')[0]
                if dice_title_unparsed:
                    
                    if "[" in dice_title_unparsed and re.search('\dd\d\d?', dice_title_unparsed.split("[")[1].split("]")[0]) :
                         dice_type = dice_title_unparsed.split("[")[1].split("]")[0]
                    elif "[" in dice_title_unparsed:
                        dice_type = dice_title_unparsed.split("Rolling ")[1].split("[")[0]
                    elif "+" in dice_title_unparsed:
                        dice_type = dice_title_unparsed.split("Rolling ")[1].split("=")[0].rstrip()
                    elif extract_dice_type_value(dice_title_unparsed) != None:
                        dice_type = extract_dice_type_value(dice_title_unparsed)
                        
                    print("dice type: " + dice_type)
                    
                    # if has modifier
                    modifier = ''
                    if '+' in dice_type:
                        dice_type_u = dice_type.split("+")[0].rstrip()
                        modifier = dice_type.split("+")[1].rstrip()
                        dice_type = dice_type_u
                    # elif "</span>+<span" in dice_title_unparsed:
                    #     modifier = dice_title_unparsed.split('+<span class="basicdiceroll">')[1].split("</span>")[0].rstrip()
                        
                    print('modifier: ' + modifier)
                    print('dice_type: ' + dice_type)
                    
                
                # total roll value
                total_roll_value = message.xpath('.//span[contains(@class, "inlinerollresult")]/text()')[0]
                if total_roll_value:
                    print('total_roll_value: ' + total_roll_value)
                    
                # action_name
                action_name = message.xpath('.//div[@class="sheet-label"]/span/a/text()')
                if len(action_name) > 0:
                    action_name = re.sub(r'\s{2,}', ' ', action_name[0].rstrip())
                    print('Weapon: ' + action_name)
                else:
                    action_name = ''
                    
                # TODO: REWORK
                if action_name == '':
                    # action_type
                    action_type = message.xpath('.//div[@class="sheet-label"]/span/text()')
                    if len(action_type) > 0 and action_type[0].strip() != '':
                        action_type = action_type[0].strip()
                        print('action_type: ' + action_type)
                    else:
                        action_type = ''
                        
                    action_name = action_type
                    

                # Now you can access the generated PLAYER_ID
                new_player_id = player.PLAYER_ID
                
                
                html = etree.tostring(message, encoding='unicode', method='html')
                # Create a new DiceRolls instance and insert it into the database
                new_dice_roll = DiceRolls(
                    NAT_ROLL_VALUE=nat_rolls,
                    TOTAL_ROLL_VALUE=total_roll_value,
                    ACTION_TYPE=None,
                    ACTION_NAME=action_name,
                    DICE_TYPE=dice_type,
                    MODIFIER=modifier,
                    IS_CRITICAL_FAIL=nat_rolls == '1',
                    IS_CRITICAL_HIT=nat_rolls == '20',
                    FULL_MESSAGE=html,
                    PLAYER_ID=new_player_id # Use the player's ID as the foreign key
                )

                # Add the new_dice_roll to the session and commit the changes to the database
                session.add(new_dice_roll)
                session.commit()
                    


        except etree.XPathEvalError as e:
            print("XPath Error:", e)  # Print the error message for debugging
        
        
extract_values()





















# Close the session
session.close()
