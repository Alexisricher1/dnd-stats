import re
from lxml import html, etree

def read_file_into_string(file_path):
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
        return file_content
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None

# Example usage:
file_path = 'dndlog_feb2025.html'
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


def extract_values():
    # If general messages exist, proceed
    if general_messages:
        try:
            for message in general_messages:
                print('-------------------')
                # character name
                character_name = message.xpath('.//div[contains(@class, "sheet-charname")]/span/text()')
                if character_name and len(character_name) > 0:
                    
                    print('character_name: ' + character_name[0])
                else:
                    #print('Character not found!')
                    continue
                    
                    
                
                # natural roll value
                nat_roll_values_unparsed = message.xpath('.//span[contains(@class, "inlinerollresult")]/@title')
                if nat_roll_values_unparsed:
                    if len(nat_roll_values_unparsed) > 1:
                        # TODO: need work to  
                        # two types of damage like one handed or two handed.
                        # for nat_roll_value in nat_roll_values_unparsed:
                        #     damage_type = nat_roll_values_unparsed.xpath('.//span[contains(@class, "sheet-sublabel")]/text()')[0]
                        #     print('damage_type : ' + damage_type)
                        #     extract_value_between_parentheses(damage_type)
                        a = 1
                    else:
                        nat_rolls = extract_value_between_parentheses(nat_roll_values_unparsed[0])
                        
                        if nat_rolls:
                            print("nat_rolls: " + nat_rolls)
                        else:
                            continue
                else:
                    continue
                # dice type and modifier value
                dice_title_unparsed = message.xpath('.//span[contains(@class, "inlinerollresult")]/@title')[0]
                if dice_title_unparsed:
                    
                    if "[" in dice_title_unparsed and dice_title_unparsed.split("[")[1].split("]")[0] != 'INIT':
                        dice_type = dice_title_unparsed.split("[")[1].split("]")[0]
                    elif extract_dice_type_value(dice_title_unparsed) != None:
                        dice_type = extract_dice_type_value(dice_title_unparsed)
                        
                    print("dice type: " + dice_type)
                    
                    # if has modifier
                    if ' + ' in dice_type:
                        dice_type = dice_title_unparsed.split("[")[1].split("]")[0].split(" + ")[0]
                        modifier = dice_title_unparsed.split("[")[1].split("]")[0].split(" + ")[1]
                        print('modifier: ' + modifier)
                    print('dice_type: ' + dice_type)
                    
                
                # total roll value
                total_roll_value = message.xpath('.//span[contains(@class, "inlinerollresult")]/text()')[0]
                if total_roll_value:
                    print('total_roll_value: ' + total_roll_value)
                    
                # Weapon
                weapon = message.xpath('.//div[@class="sheet-label"]/span/a/text()')
                if len(weapon) > 0:
                    print('Weapon: ' + weapon[0])
                    
                # action_type
                action_type = message.xpath('.//div[@class="sheet-label"]/span/text()')
                if len(action_type) > 0:
                    if action_type[0].strip() != '':
                        print('action_type: ' + action_type[0].strip())
                    


        except etree.XPathEvalError as e:
            print("XPath Error:", e)  # Print the error message for debugging
        
        
extract_values()