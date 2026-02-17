#!/usr/bin/env python3

import os
import argparse
import requests
from dataclasses import dataclass
from typing import List, Optional
from google.transit import gtfs_realtime_pb2
import time
import json
from collections import OrderedDict

# WMATA requires an API key for accessing the GTFS-RT feed
WMATA_API_KEY = "YOUR_API_KEY"

parser = argparse.ArgumentParser(description="WMATA Rail Tracker")
route_ids = ['RED', 'BLUE', 'GREEN', 'YELLOW', 'ORANGE', 'SILVER']
parser.add_argument('-l', '-r', '--route', type=str, choices=route_ids, default='RED', help='Line to track')
parser.add_argument('-st', '--self-test', action='store_true', help='Run self-test to display route colors and names')
args = parser.parse_args()

line_to_long_name = {
    "RED": "Red Line",
    "BLUE": "Blue Line",
    "GREEN": "Green Line",
    "YELLOW": "Yellow Line",
    "ORANGE": "Orange Line",
    "SILVER": "Silver Line"
}

# Mapping direction_id to trip_headsign for each route
headsigns = {
    "RED":    {0: "Glenmont", 1: "Shady Grove"},
    "BLUE":   {0: "Largo", 1: "Franconia-Springfield"},
    "GREEN":  {0: "Greenbelt", 1: "Branch Av"},
    "YELLOW": {0: "Greenbelt", 1: "Huntington"},
    "ORANGE": {0: "New Carrollton", 1: "Vienna"},
    "SILVER": {0: "Largo", 1: "Ashburn"},
}

# WMATA Line Colors (ANSI 24-bit) derived from official GTFS routes.txt
colors = {
    "RED":     "\033[1m\033[38;2;255;255;255m\033[48;2;200;15;34m",
    "BLUE":    "\033[1m\033[38;2;255;255;255m\033[48;2;0;156;222m",
    "GREEN":   "\033[1m\033[38;2;255;255;255m\033[48;2;0;177;64m",
    "YELLOW":  "\033[1m\033[38;2;0;0;0m\033[48;2;255;209;0m",
    "ORANGE":  "\033[1m\033[38;2;0;0;0m\033[48;2;237;139;0m",
    "SILVER":  "\033[1m\033[38;2;0;0;0m\033[48;2;145;157;157m",
    "SHUTTLE": "\033[1m\033[38;2;0;0;0m\033[48;2;184;159;130m",
}

feed_url = "https://api.wmata.com/gtfs/rail-gtfsrt-tripupdates.pb"

@dataclass
class Train:
    trip_id: str
    route_id: str
    start_date: str
    next_stop_id: str
    time_until: float
    direction: Optional[int] = None
    next_station_index: Optional[int] = -1
    direction_char: Optional[str] = None
    vehicle_stop_id: Optional[str] = None
    current_status: Optional[str] = None
    section_name: Optional[str] = None

    def __str__(self):
        eta = f"{int(self.time_until)}s" if self.time_until is not None else "n/a"
        status_info = f"{self.current_status}" if self.current_status else ""
        
        next_station_name = traingetter.station_id_to_name(self.next_stop_id) or self.next_stop_id
        direction_prefix = self.direction_char if self.direction_char else str(self.direction)

        # Longer lines need more padding for alignment
        padding = " " * (20 - len(direction_prefix)) if len(direction_prefix) < 20 else " "
        
        return f"""
{colors.get(self.route_id, "") + f" {direction_prefix} " + "\033[0m"}{padding}{"\033[1;44m" + self.trip_id + "\033[0m"} {"\033[1;33m" + status_info}\n{next_station_name} in {eta}\033[0m"""

def _secs_until(arrival_ts: int) -> float:
    try:
        now = time.time()
        remaining = float(arrival_ts) - now
        return remaining if remaining > 0 else 0.0
    except Exception:
        return 0.0

class TrainGetter():
    def __init__(self) -> None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(script_dir, "wmata_subway_stations.json")
        with open(json_path, "r") as f:
            full_data = json.load(f, object_pairs_hook=OrderedDict)
        
        self.references = full_data.get("references", {})
        self.lines_data = full_data.get("Lines", {})
        self.route_info = self.lines_data.get(args.route, {})
        
        self.stop_id_to_name = OrderedDict()
        self.stop_id_to_sections = {}
        self.route_sections = OrderedDict()

        if not self.route_info:
            return

        is_branched = self.route_info.get("branch", False)
        raw_stop_data = self.route_info.get("stop_id_to_index", {})

        if not is_branched:
            section_name = f"{args.route} Line"
            self.route_sections[section_name] = raw_stop_data
            for sid, val in raw_stop_data.items():
                self.stop_id_to_name[sid] = val[1]
                if sid not in self.stop_id_to_sections:
                    self.stop_id_to_sections[sid] = []
                self.stop_id_to_sections[sid].append(section_name)
        else:
            for i, branch_dict in enumerate(raw_stop_data):
                section_name = f"{args.route} Segment {i+1}"
                self.route_sections[section_name] = branch_dict
                for sid, val in branch_dict.items():
                    self.stop_id_to_name[sid] = val[1]
                    if sid not in self.stop_id_to_sections:
                        self.stop_id_to_sections[sid] = []
                    self.stop_id_to_sections[sid].append(section_name)

    def station_id_to_name(self, stop_id: str) -> Optional[str]:
        return self.stop_id_to_name.get(stop_id)

    def get_trains(self, feed: gtfs_realtime_pb2.FeedMessage) -> List[Train]:
        trains: List[Train] = []
        for entity in feed.entity:
            if entity.HasField('trip_update'):
                tu = entity.trip_update
                if tu.trip.route_id != args.route:
                    continue
                
                arrival_ts = None
                next_stop_id_raw = None
                for stu in tu.stop_time_update:
                    at, dt = getattr(stu, "arrival", None), getattr(stu, "departure", None)
                    if at and at.time:
                        arrival_ts, next_stop_id_raw = at.time, stu.stop_id
                        break
                    if dt and dt.time:
                        arrival_ts, next_stop_id_raw = dt.time, stu.stop_id
                        break
                
                if not next_stop_id_raw:
                    continue
                
                base_stop_id = self.references.get(next_stop_id_raw, next_stop_id_raw)
                secs = _secs_until(arrival_ts) if arrival_ts else 0.0
                
                direction = tu.trip.direction_id
                # Use headsigns map if available, otherwise fallback to I/O or the ID
                route_heads = headsigns.get(args.route, {})
                direction_char = route_heads.get(direction, 'OUT' if direction == 0 else 'IN')
                
                possible_sections = self.stop_id_to_sections.get(base_stop_id, [])
                section_name = possible_sections[0] if possible_sections else None
                
                station_index = -1
                if section_name:
                    branch_data = self.route_sections.get(section_name, {})
                    val = branch_data.get(base_stop_id)
                    if val:
                        station_index = val[0]

                trains.append(Train(
                    trip_id=tu.trip.trip_id,
                    route_id=tu.trip.route_id,
                    start_date=tu.trip.start_date,
                    next_stop_id=base_stop_id,
                    time_until=secs,
                    direction=direction,
                    next_station_index=station_index,
                    direction_char=direction_char,
                    section_name=section_name
                ))
        
        def get_sort_key(train: Train):
            # Sort toward index 0 or toward endpoint
            # For Red line, direction 0 is toward index 0 (Glenmont)
            # For others, usually direction 1 is toward index 0
            if args.route == "RED":
                is_to_endpoint = (train.direction == 0)
            else:
                is_to_endpoint = (train.direction == 1)

            primary_sort = train.next_station_index - (1 if is_to_endpoint else 0)
            primary_sort *= -1
            secondary_sort = train.time_until
            secondary_sort *= (1 if is_to_endpoint else -1)
            return (primary_sort, secondary_sort)

        try:
            trains.sort(key=get_sort_key)
        except Exception:
            pass
            
        return trains

def self_test():
    print("WMATA Rail Routes:\n")
    for route in route_ids:
        color = colors.get(route, "\033[0m")
        print(f"{color} {route} \033[0m: {line_to_long_name[route]}")
    print("\n")
    print(len(route_ids), "routes total.")

if __name__ == "__main__":
    if args.self_test:
        self_test()
        exit()

    traingetter = TrainGetter()
    feed = gtfs_realtime_pb2.FeedMessage()
    
    headers = {"api_key": WMATA_API_KEY}
    
    try:
        response = requests.get(feed_url, headers=headers)
        response.raise_for_status()
        feed.ParseFromString(response.content)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        exit(1)

    trains = traingetter.get_trains(feed)

    color = colors.get(args.route, "\033[0m")
    print(color + f" {args.route}: {line_to_long_name.get(args.route, '')} " + "\033[0m")
    
    if not traingetter.route_info:
        print(f"No station data found for route {args.route} in wmata_subway_stations.json")
        exit()

    if not trains:
        print("No trip updates for this route in feed.")
    
    trains_by_section = OrderedDict((section, []) for section in traingetter.route_sections.keys())
    for t in trains:
        if t.section_name and t.section_name in trains_by_section:
            trains_by_section[t.section_name].append(t)

    for section_name, section_trains in trains_by_section.items():
        print(f"\n\033[1;4m{section_name}\033[0m")
        if section_trains:
            for t in section_trains:
                print(t)
