import csv
import json

def create_wmata_json(red, blue, green, yellow, orange, silver):
    # Hardcoded paths
    stops_path = r'c:\Users\Chen\Downloads\rail-gtfs-static\stops.txt'
    output_path = r'c:\Users\Chen\Documents\VSCode\Python\wmata_rail\wmata_subway_stations.json'

    # Hardcoded boilerplate
    data = {
        "Lines": {
            "RED": {},
            "BLUE": {},
            "GREEN": {},
            "YELLOW": {},
            "ORANGE": {},
            "SILVER": {}
        },
        "references": {}
    }

    # Set branch info based on WMATA system map
    data['Lines']['RED']['branch'] = False
    data['Lines']['BLUE']['branch'] = False
    data['Lines']['GREEN']['branch'] = False
    data['Lines']['YELLOW']['branch'] = False
    data['Lines']['ORANGE']['branch'] = False
    data['Lines']['SILVER']['branch'] = True

    # Set line station name to index mapping based on WMATA GTFS data
    data['Lines']['RED']['stop_id_to_index'] = red
    data['Lines']['BLUE']['stop_id_to_index'] = blue
    data['Lines']['GREEN']['stop_id_to_index'] = green
    data['Lines']['YELLOW']['stop_id_to_index'] = yellow
    data['Lines']['ORANGE']['stop_id_to_index'] = orange
    data['Lines']['SILVER']['stop_id_to_index'] = silver

    # Read stops.txt and populate references
    try:
        with open(stops_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                stop_id = row['stop_id']
                # Filter for stop_ids starting with "PF_"
                if stop_id.startswith('PF_'):
                    data['references'][stop_id] = row['parent_station']
    except FileNotFoundError:
        print(f"Error: Could not find file at {stops_path}")
        return
    except KeyError as e:
        print(f"Error: Missing expected column in CSV: {e}")
        return

    # Dump to JSON file with indentation
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f)

    print(f"Successfully created {output_path} with {len(data['references'])} references.")

if __name__ == "__main__":
    red = {
        "STN_B11": [0, "Glenmont"],
        "STN_B10": [1, "Wheaton"],
        "STN_B09": [2, "Forest Glen"],
        "STN_B08": [3, "Silver Spring"],
        "STN_B07": [4, "Takoma"],
        "STN_B06_E06": [5, "Fort Totten"],
        "STN_B05": [6, "Brookland-CUA"],
        "STN_B04": [7, "Rhode Island Av"],
        "STN_B35": [8, "NoMa-Gallaudet U"],
        "STN_B03": [9, "Union Station"],
        "STN_B02": [10, "Judiciary Square"],
        "STN_B01_F01": [11, "Gallery Place"],
        "STN_A01_C01": [12, "Metro Center"],
        "STN_A02": [13, "Farragut North"],
        "STN_A03": [14, "Dupont Circle"],
        "STN_A04": [15, "Woodley Park"],
        "STN_A05": [16, "Cleveland Park"],
        "STN_A06": [17, "Van Ness-UDC"],
        "STN_A07": [18, "Tenleytown-AU"],
        "STN_A08": [19, "Friendship Heights"],
        "STN_A09": [20, "Bethesda"],
        "STN_A10": [21, "Medical Center"],
        "STN_A11": [22, "Grosvenor-Strathmore"],
        "STN_A12": [23, "North Bethesda"],
        "STN_A13": [24, "Twinbrook"],
        "STN_A14": [25, "Rockville"],
        "STN_A15": [26, "Shady Grove"]
    }
    blue = {
        "STN_J03": [0, "Franconia-Springfield"],
        "STN_J02": [1, "Van Dorn St"],
        "STN_C13": [2, "King St-Old Town"],
        "STN_C12": [3, "Braddock Road"],
        "STN_C11": [4, "Potomac Yard"],
        "STN_C10": [5, "Ronald Reagan Washington National Airport"],
        "STN_C09": [6, "Crystal City"],
        "STN_C08": [7, "Pentagon City"],
        "STN_C07": [8, "Pentagon"],
        "STN_C06": [9, "Arlington Cemetery"],
        "STN_C05": [10, "Rosslyn"],
        "STN_C04": [11, "Foggy Bottom-GWU"],
        "STN_C03": [12, "Farragut West"],
        "STN_C02": [13, "McPherson Sq"],
        "STN_A01_C01": [14, "Metro Center"],
        "STN_D01": [15, "Federal Triangle"],
        "STN_D02": [16, "Smithsonian"],
        "STN_D03_F03": [17, "L'Enfant Plaza"],
        "STN_D04": [18, "Federal Center SW"],
        "STN_D05": [19, "Capitol South"],
        "STN_D06": [20, "Eastern Market"],
        "STN_D07": [21, "Potomac Av"],
        "STN_D08": [22, "Stadium-Armory"],
        "STN_G01": [23, "Benning Rd"],
        "STN_G02": [24, "Capitol Heights"],
        "STN_G03": [25, "Addison Rd"],
        "STN_G04": [26, "Morgan Blvd"],
        "STN_G05": [27, "Downtown Largo"]
    }
    green = {
        "STN_F11": [0, "Branch Av"],
        "STN_F10": [1, "Suitland"],
        "STN_F09": [2, "Naylor Road"],
        "STN_F08": [3, "Southern Av"],
        "STN_F07": [4, "Congress Heights"],
        "STN_F06": [5, "Anacostia"],
        "STN_F05": [6, "Navy Yard-Ballpark"],
        "STN_F04": [7, "Waterfront"],
        "STN_D03_F03": [8, "L'Enfant Plaza"],
        "STN_F02": [9, "Archives"],
        "STN_B01_F01": [10, "Gallery Place"],
        "STN_E01": [11, "Mount Vernon Sq"],
        "STN_E02": [12, "Shaw-Howard U"],
        "STN_E03": [13, "U St"],
        "STN_E04": [14, "Columbia Heights"],
        "STN_E05": [15, "Georgia Av-Petworth"],
        "STN_B06_E06": [16, "Fort Totten"],
        "STN_E07": [17, "West Hyattsville"],
        "STN_E08": [18, "Hyattsville Crossing"],
        "STN_E09": [19, "College Park-U of Md"],
        "STN_E10": [20, "Greenbelt"]
    }
    yellow = {
        "STN_C15": [0, "Huntington"],
        "STN_C14": [1, "Eisenhower Av"],
        "STN_C13": [2, "King St-Old Town"],
        "STN_C12": [3, "Braddock Road"],
        "STN_C11": [4, "Potomac Yard"],
        "STN_C10": [5, "Ronald Reagan Washington National Airport"],
        "STN_C09": [6, "Crystal City"],
        "STN_C08": [7, "Pentagon City"],
        "STN_C07": [8, "Pentagon"],
        "STN_D03_F03": [9, "L'Enfant Plaza"],
        "STN_F02": [10, "Archives"],
        "STN_B01_F01": [11, "Gallery Place"],
        "STN_E01": [12, "Mount Vernon Sq"],
        "STN_E02": [13, "Shaw-Howard U"],
        "STN_E03": [14, "U St"],
        "STN_E04": [15, "Columbia Heights"],
        "STN_E05": [16, "Georgia Av-Petworth"],
        "STN_B06_E06": [17, "Fort Totten"],
        "STN_E07": [18, "West Hyattsville"],
        "STN_E08": [19, "Hyattsville Crossing"],
        "STN_E09": [20, "College Park-U of Md"],
        "STN_E10": [21, "Greenbelt"]
    }
    orange = {
        "STN_K08": [0, "Vienna"],
        "STN_K07": [1, "Dunn Loring"],
        "STN_K06": [2, "West Falls Church"],
        "STN_K05": [3, "East Falls Church"],
        "STN_K04": [4, "Ballston-MU"],
        "STN_K03": [5, "Virginia Sq-GMU"],
        "STN_K02": [6, "Clarendon"],
        "STN_K01": [7, "Court House"],
        "STN_C05": [8, "Rosslyn"],
        "STN_C04": [9, "Foggy Bottom-GWU"],
        "STN_C03": [10, "Farragut West"],
        "STN_C02": [11, "McPherson Sq"],
        "STN_A01_C01": [12, "Metro Center"],
        "STN_D01": [13, "Federal Triangle"],
        "STN_D02": [14, "Smithsonian"],
        "STN_D03_F03": [15, "L'Enfant Plaza"],
        "STN_D04": [16, "Federal Center SW"],
        "STN_D05": [17, "Capitol South"],
        "STN_D06": [18, "Eastern Market"],
        "STN_D07": [19, "Potomac Av"],
        "STN_D08": [20, "Stadium-Armory"],
        "STN_D09": [21, "Minnesota Av"],
        "STN_D10": [22, "Deanwood"],
        "STN_D11": [23, "Cheverly"],
        "STN_D12": [24, "Landover"],
        "STN_D13": [25, "New Carrollton"]
    }
    silver = [
        {
            "STN_G05": [0, "Downtown Largo"],
            "STN_G04": [1, "Morgan Blvd"],
            "STN_G03": [2, "Addison Rd"],
            "STN_G02": [3, "Capitol Heights"],
            "STN_G01": [4, "Benning Rd"]
        },
        {
            "STN_D13": [0, "New Carrollton"],
            "STN_D12": [1, "Landover"],
            "STN_D11": [2, "Cheverly"],
            "STN_D10": [3, "Deanwood"],
            "STN_D09": [4, "Minnesota Av"]
        },
        {
            "STN_D08": [0, "Stadium-Armory"],
            "STN_D07": [1, "Potomac Av"],
            "STN_D06": [2, "Eastern Market"],
            "STN_D05": [3, "Capitol South"],
            "STN_D04": [4, "Federal Center SW"],
            "STN_D03_F03": [5, "L'Enfant Plaza"],
            "STN_D02": [6, "Smithsonian"],
            "STN_D01": [7, "Federal Triangle"],
            "STN_A01_C01": [8, "Metro Center"],
            "STN_C02": [9, "McPherson Sq"],
            "STN_C03": [10, "Farragut West"],
            "STN_C04": [11, "Foggy Bottom-GWU"],
            "STN_C05": [12, "Rosslyn"],
            "STN_K01": [13, "Court House"],
            "STN_K02": [14, "Clarendon"],
            "STN_K03": [15, "Virginia Sq-GMU"],
            "STN_K04": [16, "Ballston-MU"],
            "STN_K05": [17, "East Falls Church"],
            "STN_N01": [18, "McLean"],
            "STN_N02": [19, "Tysons"],
            "STN_N03": [20, "Greensboro"],
            "STN_N04": [21, "Spring Hill"],
            "STN_N06": [22, "Wiehle-Reston East"],
            "STN_N07": [23, "Reston Town Center"],
            "STN_N08": [24, "Herndon"],
            "STN_N09": [25, "Innovation Center"],
            "STN_N10": [26, "Washington Dulles International Airport"],
            "STN_N11": [27, "Loudoun Gateway"],
            "STN_N12": [28, "Ashburn"]
        }
    ]
    for color, num_of_stations, stations in zip(["RED", "BLUE", "GREEN", "YELLOW", "ORANGE", "SILVER"], [27, 28, 21, 22, 26, 3], [red, blue, green, yellow, orange, silver]):
        assert len(stations) == num_of_stations, f"Expected {num_of_stations} stations for {color} line, but got {len(stations)}"
    for branch, num_of_stations, stations in zip(["SILVER_1", "SILVER_2", "SILVER_3"], [5, 5, 29], silver):
        assert len(stations) == num_of_stations, f"Expected {num_of_stations} stations for {branch} branch of SILVER line, but got {len(stations)}"
    create_wmata_json(red, blue, green, yellow, orange, silver)