import xml.etree.ElementTree as ET
from datetime import datetime

'''

Script to parse sales data and match itemIDs to string name & descriptions.

'''
# Global variables
CASH_XML = './strings/cash.xml'
EQUIPS_XML = './strings/equips.xml'
PET_XML = './strings/pet.xml'
COMMODITY_XML = './strings/commodity.xml'
PACKAGE_NAMES_XML = './strings/package_names.xml'
PACKAGE_CONTENTS_XML = './strings/package_contents.xml'
QUALIFYING_DIRS_OUTPUT = 'qualifying_dirs.xml'

def parse_xml_files():
    """
    Parse the XML files and return the root elements.
    Returns:
    #1 - commodity.xml
    #2 - cash.xml
    #3 - eqp.xml
    #4 - pet.xml
    #5 - package_names.xml
    #6 - package_contents.xml
    """
    tree_commodity = ET.parse(COMMODITY_XML)
    tree_cash = ET.parse(CASH_XML)
    tree_eqp = ET.parse(EQUIPS_XML)
    tree_pet = ET.parse(PET_XML)
    tree_package_names = ET.parse(PACKAGE_NAMES_XML)
    tree_package_contents = ET.parse(PACKAGE_CONTENTS_XML)

    return (
        tree_commodity.getroot(),
        tree_cash.getroot(),
        tree_eqp.getroot(),
        tree_pet.getroot(),
        tree_package_names.getroot(),
        tree_package_contents.getroot()
    )

def upcoming_sales(root_commodity):
    # This script parses a dumped Commodity.img to XML 
    # For every dir in the XML, find ones that are upcoming
    # Use current month to find any Dirs with term_start values of that month

    # Load the XML file
    # unused XML files get assigned to dummy variables

    # Create a new XML tree for qualifying dirs
    qualifying_root = ET.Element("root")

    now = datetime.now()
    curr_day = now.strftime("%Y%m%d")

    # Iterate over all dir elements
    for dir_elem in root_commodity.findall('.//dir'):
        # Check if the dir element has a child element with name "termStart"
        term_end_elem = dir_elem.find("./int32[@name='termEnd']")
        # Check if termEnd value is in the past or not
        if term_end_elem is not None and term_end_elem.get('value') >= curr_day:
            # Append the qualifying dir element to the new XML tree
            qualifying_root.append(dir_elem)

    
    qualifying_tree = ET.ElementTree(qualifying_root)


    return qualifying_tree

def sort_xml(tree, sort_by):
    '''
    Sort an XML tree by passed element
    '''
    root = tree.getroot()

    sorted_elements = sorted(root, key=lambda x: int(x.find(f"int32[@name='{sort_by}']").get("value")))

    root.clear()

    # Append the sorted elements back to the root
    for element in sorted_elements:
        root.append(element)
        
    return tree

def search_nested_xml_for_dir_by_name(root, item_id):
    """
    Search nested XML root for a directory element by name.
    
    Parameters:
        root (Element): XML root element to start the search from.
        item_id (str): ID of the item to search for.
    
    Returns:
        Element or None: XML element with the matching name, or None if not found.
    """
    return root.find(f".//dir[@name='{item_id}']")

def package_dict_creator(qualified_tree, root_package_names, root_package_contents):
    root = qualified_tree.getroot()

    # make package dir for storing data
    # contents will be an array of SN IDs
    package_dict = {}

    # get package names
    for dir_element in root.findall('dir'):
        item_id = dir_element.find("int32[@name='ItemId']").get('value')
        if item_id.startswith("910"):
            # for dir_element_2 in root_package_names:
            package = root_package_names.find(f"dir[@name='{item_id}']")
            package_id = package.attrib['name']
            package_dict[package_id] = {}
            package_dict[package_id]["name"] = package.find("string[@name='name']").get('value')
            package_dict[package_id]["description"] = package.find("string[@name='desc']").get('value').replace("#c","").replace("\\n","\n").replace("#","") if package.find("string[@name='desc']") is not None else ""

            for dir_element in root_package_contents.findall('dir'):
                if package_id == dir_element.attrib['name']:
                    package_dict[package_id]["contents"] = [int32_element.get('value') for int32_element in dir_element.findall('.//int32')]

    
    # return nested dictionaries
    return package_dict

def package_contents_parser(package_dict, item_id, root_commodity):
    # something = an entry from our dictionary
    # or maybe pass in dictionary and item_id?

    item_ids = {}
    item_ids[item_id] = {}
    array = package_dict[item_id].get("contents")
    for idx, sn in enumerate(array):
        for dir_element in root_commodity.findall('.//dir'):
            sn_elem = dir_element.find('int32[@name="SN"]')
            if sn_elem is not None and sn_elem.get('value') == sn:
                item_id_element = dir_element.find('int32[@name="ItemId"]')
                item_count_element = dir_element.find('int32[@name="Count"]')
                if item_id_element is not None:
                    item_ids[item_id][idx] = {
                        'itemID': item_id_element.get('value'),
                        'count': item_count_element.get('value')
                    }
                break
    return item_ids



def process_qualifying_dirs(qualified_tree, package_dict, root_commodity, root_cash, root_eqp, root_pet):
    root_qualified = qualified_tree.getroot()
    item_info = {}
    package_contents = {}

    for dir_element in root_qualified.findall('dir'):
        # get the value of the 'ItemId' attribute from commodity data
        # sn_id is needed to differentiate items with the same ID being sold at different values such as amount, price, period
        # sn_id is only used to differentiate non-package items for now, may need to change in the future but unsure
        # will very likely need to modify the dictionary to put the item ID somewhere in there;
        # because it used to be the key value of each dict entry, but now it is nowhere in the dict
        # i will do this later because it won't be needed until I figure out how to pull images from Wz files

        sn_id = dir_element.find("int32[@name='SN']").get('value')
        item_id = dir_element.find("int32[@name='ItemId']").get('value')
        price = dir_element.find("int32[@name='Price']").get('value')
        count = dir_element.find("int32[@name='Count']").get('value')
        discount = dir_element.find("int32[@name='discount']").get('value') if dir_element.find("int32[@name='discount']") is not None else "0"
        original_price = dir_element.find("int32[@name='originalPrice']").get('value') if dir_element.find("int32[@name='originalPrice']") is not None else "0"
        game_world = dir_element.find("string[@name='gameWorld']").get('value')
        period = dir_element.find("int32[@name='Period']").get('value')

        term_start_element = dir_element.find("int32[@name='termStart']")
        term_start = term_start_element.get('value')
        term_start_f = datetime.strptime(term_start, '%Y%m%d%H').strftime('%m-%d-%Y %H:00 UTC')

        term_end_element = dir_element.find("int32[@name='termEnd']")
        term_end = term_end_element.get('value')
        term_end_f = datetime.strptime(term_end, '%Y%m%d%H').strftime('%m-%d-%Y %H:00 UTC')

        # search through all XML files for the corresponding Item ID
        corresponding_dir = None
        if item_id.startswith("910"):
            # stuff
            contents = package_contents_parser(package_dict, item_id, root_commodity)
            for odx, items in contents.items():
                package_contents[odx] = {}
                for idx, item_data in items.items():
                    sub_item_id = item_data['itemID']
                    count = item_data['count']

                    for root in [root_cash, root_eqp, root_pet]:
                        corresponding_dir = search_nested_xml_for_dir_by_name(root, sub_item_id)
                        if corresponding_dir is not None:
                            break
                    if corresponding_dir is not None:

                        name_element = corresponding_dir.find("string[@name='name']")
                        name = name_element.get('value') if name_element is not None else "Name not found"
                        
                        # Get the description string
                        desc_element = corresponding_dir.find("string[@name='desc']")
                        description = desc_element.get('value') if desc_element is not None else None
                        description = description.replace("#c","").replace("\\n","\n").replace("#","") if description is not None else None

                        package_contents[odx][idx] = {'name': name, 'description': description, 'count': count}

                    
                    
            item_info[item_id] = {'name': package_dict[item_id].get('name'), 'description': package_dict[item_id].get('description'),
                                  'count': count, 'price': price, 'discount': discount, 'originalPrice': original_price,
                                  'termStart': term_start_f, 'termEnd': term_end_f, 'gameWorld': game_world, 'period': period,
                                  'packageContents': package_contents
                                  }
        for root in [root_cash, root_eqp, root_pet]:
            corresponding_dir = search_nested_xml_for_dir_by_name(root, item_id)
            if corresponding_dir is not None:
                break
        

        if corresponding_dir is not None:
            # Get the name string
            name_element = corresponding_dir.find("string[@name='name']")
            name = name_element.get('value') if name_element is not None else "Name not found"
            
            # Get the description string
            desc_element = corresponding_dir.find("string[@name='desc']")
            description = desc_element.get('value') if desc_element is not None else None
            description = description.replace("#c","").replace("\\n","\n").replace("#","") if description is not None else None
            
            # pets are listed as permanent because the item itself is permanent
            # but the magic duration is not permanent
            # this is a hack job to list them as 90-day until i figure out where magic duration is stored
            if item_id.startswith("500") and price == "4900":
                period = "90"

            
            item_info[sn_id] = {'name': name, 'count': count, 'description': description, 'price': price, 'discount': discount, 'originalPrice': original_price, 'termStart': term_start_f, 'termEnd': term_end_f, 'gameWorld': game_world, 'period': period}

    return item_info

def main():
    root_commodity, root_cash, root_eqp, root_pet, root_package_names, root_package_contents = parse_xml_files()

    qualifying_dirs = upcoming_sales(root_commodity)
    sort_by = 'termStart' # change this if you want to change the sort
    sort_xml(qualifying_dirs, sort_by)
    package_dict = package_dict_creator(qualifying_dirs, root_package_names, root_package_contents)
    item_info = process_qualifying_dirs(qualifying_dirs, package_dict, root_commodity, root_cash, root_eqp, root_pet)


    with open("CashShopSales.txt", "w") as file:
        for item_id, info in item_info.items():
            output_lines = []
            output_lines.append("---")
            if info.get('name') != "":
                name_line = f"Name: {info['name']}"
                if int(info.get('count', 0)) > 1:
                    name_line += f" ({info['count']})"
                output_lines.append(name_line)

            if info.get('description'):
                output_lines.append(f"Description: {info['description']}")

            if info.get('period') != "":
                duration_line = "Duration: "
                duration_line += f"{info['period']} days" if info['period'] != "0" else "Permanent"
                output_lines.append(duration_line)
                output_lines.append("")

            if info.get('price') != "":
                currency = "Mesos" if int(info['price']) > 1000001 else "NX"
                price_line = f"Price: {int(info['price']):,} {currency}"
                if info.get('discount') == "1":
                    price_line += f" (was {int(info['originalPrice']):,} {currency})"
                output_lines.append(price_line)

            if 'packageContents' in info:
                output_lines.append("\nPackage Contents:")
                curr_package = info['packageContents'].get(f'{item_id}')
                for idx, item in enumerate(curr_package):
                    content_lines = []
                    if curr_package[idx].get('name') != "":
                        content_lines.append(f"* Name: {curr_package[idx]['name']}")
                        if int(curr_package[idx].get('count', 0)) > 1:
                            content_lines[-1] += f" ({curr_package[idx]['count']})"
                    if curr_package[idx].get('description'):
                        content_lines.append(f"  * Description: {curr_package[idx]['description']}")
                    output_lines.extend(content_lines)

            if info.get('termStart') != "":
                output_lines.append(f"\nStart Date: {info['termStart']}")

            if info.get('termEnd') != "":
                output_lines.append(f"End Date: {info['termEnd']}")
                output_lines.append("")

            if info.get('gameWorld') != "":
                if info['gameWorld'] == "45/46/70":
                    output_lines.append("Heroic Servers Only")
                elif info['gameWorld'] == "0/1/17/18/30/48/49":
                    output_lines.append("Interactive Servers Only")
                else:
                    output_lines.append("Heroic & Interactive Servers")

            if output_lines:
                output = "\n".join(output_lines)
                file.write(output + "\n\n")

    print("Saved as CashShopSales.txt")
if __name__ == "__main__":
    main()