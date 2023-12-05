"""Kelly Waller's Advent of Code solutions."""
import re  # noqa: F401
import sys
import math  # noqa: F401
import time  # noqa: F401
import copy  # noqa: F401
import pickle
import socket
import requests
# import itertools
import datetime  # noqa: F401
# import numpy
from os import path
import svtools.logging.toolbox as slt
from collections import OrderedDict

# Never did spend the time to work out how to get OAuth to work so this code expects you to
# manually copy over your session cookie value.
# Using a web browser inspect the cookies when logged into the Advent of Code website.
# Copy the value from the "session" cookie into a text file called "session.txt"

# Constants
_CODE_PATH = r"c:\AoC"
_OFFLINE = False
_YEAR = 2023
_NAME = "aoc%d" % _YEAR

_LOG = slt.getLogger(_NAME)
_LOG.setAutosplit(autosplit=True)
_LOG.setConsoleLevel("DEBUG")
_LOG.colorLevels(enable=True)
_LOG.setColor(levelname="ERROR", color=slt.FG.ired)
_LOG.setColor(levelname="WARNING", color=slt.FG.iyellow)
_LOG.setColor(levelname="DEBUG", color=slt.FG.iwhite)
# cur_date = datetime.datetime.now()
# _LOG.setFile(filename=_NAME + "_" + cur_date.strftime("%b%d_%H_%M_%S") + ".log", dynamic=True)
# _LOG.setFileLevel("INFO")


def _check_internet(host="8.8.8.8", port=53, timeout=2):
    """Attempt to check for the firewall by connecting to Google's DNS."""
    ret_code = True
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
    except socket.error as ex:  # noqa: UP024, F841
        # print(ex)
        ret_code = False
    return ret_code


def _pull_puzzle_input(day, seperator, cast, log=_LOG):
    """
    Pull the puzzle data from the AOC website.

    :param day: (int,str) the AoC day puzzle input to fetch or an example puzzle string
    :param seperator: (str,None) A string separator to pass into str.split when consuming the puzzle data.
        If None or "" don't try and split the puzzle input.
    :param cast: (None,type) A Python function often a type cast (int, str, lambda) to be run against each data element.
    :param log:  logger object
    :return: tuple of the data.
    """
    if _OFFLINE:
        with open(_CODE_PATH + rf"\{_YEAR}\day{day}.txt") as file_handler:  # noqa: FURB101, PTH123
            data_list = file_handler.read().split(seperator)
    elif type(day) is str:  # An example string
        data_list = day.split(seperator)
    else:
        log.result(slt.FG.icyan("Pulling Data Set"))
        if not path.exists(_CODE_PATH + "/session.txt"):  # noqa: PTH110
            err_str = "Using the web browser get the session cookie value\nand put it as a string in {}".format(_CODE_PATH + "\\session.txt")
            raise RuntimeError(err_str)
        with open(_CODE_PATH + "/session.txt", "r") as session_file:  # noqa: UP015, PTH123, FURB101
            session = session_file.read()
        # Check to see if behind the firewall.
        if _check_internet():  # noqa: SIM108
            proxy_dict = {}
        else:
            proxy_dict = {"http": "proxy-dmz.intel.com:911",
                          "https": "proxy-dmz.intel.com:912"}
        header = {"Cookie": "session={:s}".format(session.rstrip("\n"))}
        with requests.Session() as session:
            resp = session.get(f"https://adventofcode.com/{_YEAR}/day/{day}/input", headers = header, proxies = proxy_dict)  # noqa: E251
            _text = resp.text.strip("\n")
            if resp.ok:
                if seperator in {None, ""}:  # noqa: SIM108
                    data_list = [resp.text]
                else:
                    data_list = resp.text.split(seperator)
            else:
                log.warning("Warning website error")
                return ()

    if data_list[-1] == "":  # noqa: PLC1901
        data_list.pop(-1)
    if cast is not None:
        data_list = [cast(x) for x in data_list]
    return tuple(data_list)


def get_input(day, seperator, cast, override=False):  # noqa: FBT002
    """
    Helper function for the daily puzzle information.

    If the puzzle data does not exist (or is an empty tuple) it attempts to pull it from the website.
    Caches the puzzle data into a pickle file so that re-runs don't have the performance
    penalty of fetching from the Advent Of Code website.

    :param day: (int, str) the AoC day puzzle input to fetch or a string of the puzzle example.
    :param seperator: (str) A string separator to pass into str.split when consuming the puzzle data.
    :param cast: (None,type) A Python function often a type cast (int, str, lambda) to be run against each data element.
                             None - do not apply a function/cast to the data.
    :param override: (bool) True = Fetch the data again instead of using the cached copy.

    :return: tuple containing the puzzle data
    """
    if path.exists(_CODE_PATH + rf"\{_YEAR}\input.p"):  # noqa: SIM108, PTH110
        puzzle_dict = pickle.load(open(_CODE_PATH + rf"\{_YEAR}\input.p", "rb"))  # noqa: S301, SIM115, PTH123
    else:  # No pickle file, will need to make a new one.
        puzzle_dict = {}

    puzzle_input = puzzle_dict.get(day, None)

    if not puzzle_input or override is True:
        puzzle_input = _pull_puzzle_input(day, seperator, cast)
        if type(day) is int:  # only save the full puzzle data to the pickle file.
            puzzle_dict[day] = puzzle_input
            pickle.dump(puzzle_dict, open(_CODE_PATH + rf"\{_YEAR}\input.p", "wb"))  # noqa: PTH123, SIM115
    return puzzle_input


def display_results(day, results, log=_LOG):
    """
    Show the results of a day's puzzle in a common format.

    Args:
        day (int):  Which day in December
        results (list):  A list of result solutions for the day's puzzle.
        log (slt.EasyLogger, optional): Logger object
    Returns:
        integer number of results given.
    """
    if not isinstance(day, int):
        err_str = f"day={day} invalid.  Must be int, not {type(day)}"
        raise TypeError(err_str)
    if not isinstance(results, list):
        err_str = f"results={results} invalid.  Must be a list not {type(results)}"
        raise TypeError(err_str)
    if not isinstance(log, slt.EasyLogger):
        err_str = f"log={log} invalid.  Must be an slt.EasyLogger not {type(log)}"
        raise TypeError(err_str)

    log.result("")
    if not results:
        log.warning("Day %d Unsolved", day)
    else:
        log.result("Day %d Results:", day)
        for i, result in enumerate(results, start=1):
            if isinstance(result, int):
                log.result("  Part %d:   %d", i, result)
            else:
                log.result("  Part %d:   %s", i, result)
    return len(results)


def day1(use_example=False, log=_LOG):  # noqa: FBT002
    """
    Trebuchet calibration.

    Args:
        use_example (bool): Use the example data set
        log (slt.EasyLogger, optional): Logger object
    Returns:
        integer number of results
    """
    day = di = int(log.findCaller()[2][3:])
    results = [0, 0]
    for part2 in range(2):
        if use_example:
            if part2:
                di = ("two1nine\n"
                      "eightwothree\n"
                      "abcone2threexyz\n"
                      "xtwone3four\n"
                      "4nineeightseven2\n"
                      "zoneight234\n"
                      "7pqrstsixteen")
            else:
                di = ("1abc2\n"
                      "pqr3stu8vwx\n"
                      "a1b2c3d4e5f\n"
                      "treb7uchet\n")
        data_tuple = get_input(di, "\n", str, override=False)
        for line in data_tuple:
            digit_list = []
            if part2:
                log.debug("line: %s", line)
                # Jam the actual digit into the digit name
                for digit, digit_name in enumerate(["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]):
                    index = line.find(digit_name)
                    while index != -1:  # find all occurrances
                        index += 2  # digit_names can overlap by a character
                        line = line[:index] + f"{digit}" + line[index:]  # noqa: PLW2901
                        index = line.find(digit_name)
            log.debug("line: %s", line)
            for char in line:
                if char.isdigit():
                    digit_list.append(char)  # noqa: PERF401
            if len(digit_list) < 1:
                continue
            line_num = int(digit_list[0] + digit_list[-1])
            log.debug("line_num: %d", line_num)
            results[part2] += line_num
    return display_results(day=day, results=results, log=log)


def day2(use_example=False, log=_LOG):  # noqa: FBT002
    """
    Cube Conundrum.

    Args:
        use_example (bool): Use the example data set
        log (slt.EasyLogger, optional): Logger object
    Returns:
        integer number of results
    """
    day = di = int(log.findCaller()[2][3:])
    if use_example:
        di = ("Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green\n"
              "Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue\n"
              "Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red\n"
              "Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red\n"
              "Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green\n")
    data_tuple = get_input(di, "\n", str, override=False)
    results = []

    # Parse the strings into a list of dictionaries
    game_list = []
    for line in data_tuple:
        max_count_dict = {"red": 0, "green": 0, "blue": 0}
        # Throw away the game id and split into rounds e.g. "3 blue, 4 red"
        round_list = line.split(":")[1].split(";")
        for round_str in round_list:
            # split into sets of colors e.g. "3 blue"
            color_list = round_str.split(",")
            for entry in color_list:
                color_count_list = entry.rsplit()  # e.g. ['3', 'blue']
                # Keep track of the maximum cubes seen for each color in this game
                max_count_dict[color_count_list[1]] = max(max_count_dict[color_count_list[1]], int(color_count_list[0]))
        game_list.append(max_count_dict)

    for g_id, entry in enumerate(game_list, start=1):
        log.debug("Game %d: %s", g_id, entry)
    log.debug("")

    possible_games_sum = 0
    power_sum = 0
    for g_id, game_count_dict in enumerate(game_list, start=1):
        power = game_count_dict["red"] * game_count_dict["green"] * game_count_dict["blue"]
        power_sum += power
        output_str = f"game {id} power={power}"
        if game_count_dict["red"] <= 12 and game_count_dict["green"] <= 13 and game_count_dict["blue"] <= 14:
            output_str += " and is possible"
            possible_games_sum += g_id
        log.debug(output_str)
    results.extend((possible_games_sum, power_sum))

    return display_results(day=day, results=results, log=log)


def show_diagram(diagram, cur_r=-1, cur_c=-1, hl_r=-1, hl_c=-1, log_level="debug", log=_LOG):
    """
    Show the diagram.

    Args:
        diagram (list): 2D list
        cur_r (int):  Current Row index
        cur_c (int):  Current Column index
        hl_r (int):  A Row index to highlight
        hl_c (int):  A Column index to hightlight
        log_level (str): A description of the logging level
        log (slt.EasyLogger, optional): Logger object
    Returns:
        None
    """
    log_level_value = int(slt.getLogLevel(log_level.upper()))
    for r, row in enumerate(diagram):
        output_str = ""
        for c, cell in enumerate(row):
            cell_str = f"{cell} "
            if r == cur_r and c == cur_c:
                if r == hl_r and c == hl_c:  # don't inspect yourself
                    output_str += slt.FG.ired(cell_str)
                else:
                    output_str += slt.FG.icyan(cell_str)
            elif r == hl_r and c == hl_c:
                output_str += slt.FG.igreen(cell_str)
            else:
                output_str += cell_str
        log.log(log_level_value, output_str)
    log.log(log_level_value, "")


def day3(use_example=False, log=_LOG):  # noqa: FBT002
    """
    Unsolved.

    Args:
        use_example (bool): Use the example data set
        log (slt.EasyLogger, optional): Logger object
    Returns:
        integer number of results
    """
    day = di = int(log.findCaller()[2][3:])
    if use_example:
        di = ("467..114..\n"
              "...*......\n"
              "..35..633.\n"
              "......#...\n"
              "617*......\n"
              ".....+.58.\n"
              "..592.....\n"
              "......755.\n"
              "...$.*....\n"
              ".664.598..\n")
    data_tuple = get_input(di, "\n", str, override=False)
    results = []

    # Create the diagram
    diagram = []
    first_last_row = ["."] * (len(data_tuple[0]) + 2)
    diagram.append(first_last_row)
    for line in data_tuple:
        row_list = ["."]
        row_list.extend(list(line))
        row_list.append(".")
        diagram.append(row_list)
    diagram.append(first_last_row)
    # show_diagram(diagram, log=log)

    # Walk the diagram looking for numbers
    part_number = 0
    cur_num_str = None
    valid = False
    for r, row in enumerate(diagram):
        for c, cell in enumerate(row):
            if cell.isdigit():
                if cur_num_str is None:  # first digit of number
                    cur_num_str = cell
                    valid = False
                else:
                    cur_num_str += cell
                # Search the neighbors for a symbol
                for row_mod in [-1, 0, 1]:
                    for col_mod in [-1, 0, 1]:
                        if row_mod == 0 and col_mod == 0:  # Skip yourself
                            continue
                        nr = r + row_mod
                        nc = c + col_mod
                        if diagram[nr][nc] != "." and not diagram[nr][nc].isalnum():  # symbol
                            valid = True
            elif cur_num_str is not None:  # end of the number
                if valid:
                    log.debug("Found Valid Part Number %s", cur_num_str)
                    part_number += int(cur_num_str)
                # Reset to look for the next number
                cur_num_str = None
                valid = False
    results.append(part_number)
    log.debug("*" * 79)

    # Part 2
    # Walk the diagram looking for Gears (*)
    gear_ratio_sum = 0
    for r, row in enumerate(diagram):
        for c, cell in enumerate(row):
            if cell == "*":
                # Look for neighboring numbers
                number_neighbors = []
                for row_mod in [-1, 0, 1]:
                    for col_mod in [-1, 0, 1]:
                        if row_mod == 0 and col_mod == 0:  # Skip yourself
                            continue
                        nr = r + row_mod
                        nc = c + col_mod
                        if diagram[nr][nc].isdigit():  # Found a number
                            # figure out the whole number
                            num_str = diagram[nr][nc]
                            # look left
                            tmp_col = nc - 1
                            while diagram[nr][tmp_col].isdigit():
                                num_str = diagram[nr][tmp_col] + num_str
                                tmp_col -= 1
                            # look right
                            tmp_col = nc + 1
                            while diagram[nr][tmp_col].isdigit():
                                num_str += diagram[nr][tmp_col]
                                tmp_col += 1
                            if int(num_str) not in number_neighbors:
                                number_neighbors.append(int(num_str))
                if len(number_neighbors) > 1:
                    # Calculate gear ratio
                    gear_ratio = 1
                    for entry in number_neighbors:
                        gear_ratio *= entry
                    log.debug("Found Gear Ratio %6d: %s", gear_ratio, number_neighbors)
                    gear_ratio_sum += gear_ratio
    results.append(gear_ratio_sum)
    return display_results(day=day, results=results, log=log)


def day4(use_example=False, log=_LOG):  # noqa: FBT002
    """
    Scratchcards puzzle.

    Args:
        use_example (bool): Use the example data set
        log (slt.EasyLogger, optional): Logger object
    Returns:
        integer number of results
    """
    day = di = int(log.findCaller()[2][3:])
    if use_example:
        di = ("Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53\n"
              "Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19\n"
              "Card 3:  1 21 53 59 44 | 69 82 63 72 16 21 14  1\n"
              "Card 4: 41 92 73 84 69 | 59 84 76 51 58  5 54 83\n"
              "Card 5: 87 83 26 28 32 | 88 30 70 12 93 22 82 36\n"
              "Card 6: 31 18 13 56 72 | 74 77 10 23 35 67 36 11\n")
    data_tuple = get_input(di, "\n", str, override=False)
    results = [0, 0]

    card_values = [0]  # dummy
    for line in data_tuple:
        card_str = line.split(":")[1]  # throw away the card id
        # Create 2 sets of numbers and the intersection is the number of wins
        win_num_str, num_str = card_str.split("|")
        win_num_set = {int(i) for i in win_num_str.split()}
        num_set = {int(i) for i in num_str.split()}
        win_set = win_num_set.intersection(num_set)
        log.debug("win_set: %s", win_set)
        card_values.append(len(win_set))
        # calculate points
        if win_set:
            points = 2**(len(win_set) - 1)
            log.debug("points: %d", points)
            results[0] += points

    log.debug("*" * 79)

    # Keep track of the number of cards for each card id
    card_count = [1] * len(card_values)
    card_count[0] = 0  # dummy
    for card_idx, entry in enumerate(card_count):
        log.debug("idx: %d - %d wins", card_idx, card_values[card_idx])
        # add the copies
        for card_value in range(card_values[card_idx]):
            card_count[card_idx + 1 + card_value] += entry
        log.debug("card_count: %s", card_count)

    results[1] = sum(card_count)
    return display_results(day=day, results=results, log=log)


def day5(use_example=False, log=_LOG):  # noqa: FBT002
    """
    If you give a seed a fertilizer.

    Args:
        use_example (bool): Use the example data set
        log (slt.EasyLogger, optional): Logger object
    Returns:
        integer number of results
    """
    day = di = int(log.findCaller()[2][3:])
    if use_example:
        di = """seeds: 79 14 55 13

seed-to-soil map:
50 98 2
52 50 48

soil-to-fertilizer map:
0 15 37
37 52 2
39 0 15

fertilizer-to-water map:
49 53 8
0 11 42
42 0 7
57 7 4

water-to-light map:
88 18 7
18 25 70

light-to-temperature map:
45 77 23
81 45 19
68 64 13

temperature-to-humidity map:
0 69 1
1 0 69

humidity-to-location map:
60 56 37
56 93 4
"""
    data_tuple = get_input(di, "\n", str, override=False)
    results = []

    seed_list = []
    # Each map has a list of dictionaries with format {"source_start": #, "source_end": #, "offset": #}
    maps = OrderedDict()
    maps["seed-to-soil"] = []
    maps["soil-to-fertilizer"] = []
    maps["fertilizer-to-water"] = []
    maps["water-to-light"] = []
    maps["light-to-temperature"] = []
    maps["temperature-to-humidity"] = []
    maps["humidity-to-location"] = []
    cur_key = None
    for line in data_tuple:
        # log.debug("line: %s", line)
        if line.count("seeds:"):
            seed_list = [int(i) for i in line.split(":")[1].split()]
        elif not line:
            cur_key = None
        elif line[0].isdigit():
            if cur_key not in maps:
                err_str = f"cur_key {cur_key} not in maps"
                raise RuntimeError(err_str)
            num_list = [int(i) for i in line.split()]
            destination_start = num_list[0]
            source_start = num_list[1]
            range_length = num_list[2]
            maps[cur_key].append({"source_start": source_start,
                                  "source_end": source_start + range_length - 1,
                                  "offset": destination_start - source_start})
        else:  # map name
            cur_key = line.split()[0]

    # Show the maps
    log.debug("")
    for map_key, map_list in maps.items():
        log.debug("%s", map_key)
        for entry in map_list:
            output_str = ""
            for key, value in entry.items():
                output_str += f"  {key}: {value}"
            log.debug(output_str)

    # Use the maps to determine the location of each seed
    locations = []
    for seed in seed_list:
        cur_value = next_value = seed
        log.debug("")
        log.debug("seed %d", seed)
        for mapping_key, map_dict in maps.items():
            next_value = cur_value
            for entry in map_dict:
                if entry["source_start"] <= cur_value <= entry["source_end"]:
                    next_value = cur_value + entry["offset"]
            cur_value = next_value
            log.debug("%s: %d", mapping_key, next_value)
        locations.append(next_value)
    results.append(min(locations))

    # Part 2, go backwards from walking up locations back to a seed, then see if it falls within the seed ranges
    seed_ranges = []
    for i in range(0, len(seed_list), 2):
        seed_ranges.append((seed_list[i], seed_list[i] + seed_list[i + 1]))  # noqa: PERF401
    log.debug("seed_ranges:")
    for entry in seed_ranges:
        log.debug("  %10d - %10d  (%d)", entry[0], entry[1], entry[1] - entry[0])

    start_time = time.time()
    # htl_idx = 0
    # location_offset = 0
    # location = -1
    location = -1
    while 1:
        location += 1
        # if location >= maps["humidity-to-location"][htl_idx]["source_end"]:
        #     htl_idx += 1
        #     location_offset = 0
        # location = maps["humidity-to-location"][htl_idx]["source_start"] + maps["humidity-to-location"][htl_idx]["offset"] + location_offset
        # location_offset += 1

        cur_value = humidity = location
        for entry in maps["humidity-to-location"]:
            if entry["source_start"] + entry["offset"] <= cur_value <= entry["source_end"] + entry["offset"]:
                humidity = cur_value - entry["offset"]

        cur_value = temperature = humidity
        for entry in maps["temperature-to-humidity"]:
            if entry["source_start"] + entry["offset"] <= cur_value <= entry["source_end"] + entry["offset"]:
                temperature = cur_value - entry["offset"]

        cur_value = light = temperature
        for entry in maps["light-to-temperature"]:
            if entry["source_start"] + entry["offset"] <= cur_value <= entry["source_end"] + entry["offset"]:
                light = cur_value - entry["offset"]

        cur_value = water = light
        for entry in maps["water-to-light"]:
            if entry["source_start"] + entry["offset"] <= cur_value <= entry["source_end"] + entry["offset"]:
                water = cur_value - entry["offset"]

        cur_value = fertilizer = water
        for entry in maps["fertilizer-to-water"]:
            if entry["source_start"] + entry["offset"] <= cur_value <= entry["source_end"] + entry["offset"]:
                fertilizer = cur_value - entry["offset"]

        cur_value = soil = fertilizer
        for entry in maps["soil-to-fertilizer"]:
            if entry["source_start"] + entry["offset"] <= cur_value <= entry["source_end"] + entry["offset"]:
                soil = cur_value - entry["offset"]

        cur_value = seed = soil
        for entry in maps["seed-to-soil"]:
            if entry["source_start"] + entry["offset"] <= cur_value <= entry["source_end"] + entry["offset"]:
                seed = cur_value - entry["offset"]

        # log.debug("location %d maps to seed %d", location, seed)
        seed_found = False
        for entry in seed_ranges:
            if entry[0] <= seed <= entry[1]:
                results.append(location)
                seed_found = True
                break
        if seed_found:
            break
    log.result("P2 took %d seconds", time.time() - start_time)
    return display_results(day=day, results=results, log=log)


def day6(use_example=False, log=_LOG):  # noqa: FBT002
    """
    Unsolved.

    Args:
        use_example (bool): Use the example data set
        log (slt.EasyLogger, optional): Logger object
    Returns:
        integer number of results
    """
    day = di = int(log.findCaller()[2][3:])
    if use_example:
        di = ""
    data_tuple = get_input(di, "\n", None, override=False)  # noqa: F841
    results = []

    return display_results(day=day, results=results, log=log)


def day7(use_example=False, log=_LOG):  # noqa: FBT002
    """
    Unsolved.

    Args:
        use_example (bool): Use the example data set
        log (slt.EasyLogger, optional): Logger object
    Returns:
        integer number of results
    """
    day = di = int(log.findCaller()[2][3:])
    if use_example:
        di = ""
    data_tuple = get_input(di, "\n", str, override=False)  # noqa: F841
    results = []

    return display_results(day=day, results=results, log=log)


def day8(use_example=False, log=_LOG):  # noqa: FBT002
    """
    Unsolved.

    Args:
        use_example (bool): Use the example data set
        log (slt.EasyLogger, optional): Logger object
    Returns:
        integer number of results
    """
    day = di = int(log.findCaller()[2][3:])
    if use_example:
        di = ""
    data_tuple = get_input(di, "\n", str, override=False)  # noqa: F841
    results = []

    return display_results(day=day, results=results, log=log)


def day9(use_example=False, log=_LOG):  # noqa: FBT002
    """
    Unsolved.

    Args:
        use_example (bool): Use the example data set
        log (slt.EasyLogger, optional): Logger object
    Returns:
        integer number of results
    """
    day = di = int(log.findCaller()[2][3:])
    if use_example:
        di = ""
    data_tuple = get_input(di, "\n", str, override=False)  # noqa: F841
    results = []

    return display_results(day=day, results=results, log=log)


def day10(use_example=False, log=_LOG):  # noqa: FBT002
    """
    Unsolved.

    Args:
        use_example (bool): Use the example data set
        log (slt.EasyLogger, optional): Logger object
    Returns:
        integer number of results
    """
    day = di = int(log.findCaller()[2][3:])
    if use_example:
        di = ""
    data_tuple = get_input(di, "\n", str, override=False)  # noqa: F841
    results = []

    return display_results(day=day, results=results, log=log)


def day11(use_example=False, log=_LOG):  # noqa: FBT002
    """
    Unsolved.

    Args:
        use_example (bool): Use the example data set
        log (slt.EasyLogger, optional): Logger object
    Returns:
        integer number of results
    """
    day = di = int(log.findCaller()[2][3:])
    if use_example:
        di = ""
    data_tuple = get_input(di, "\n", str, override=False)  # noqa: F841
    results = []

    return display_results(day=day, results=results, log=log)


def day12(use_example=False, log=_LOG):  # noqa: FBT002
    """
    Unsolved.

    Args:
        use_example (bool): Use the example data set
        log (slt.EasyLogger, optional): Logger object
    Returns:
        integer number of results
    """
    day = di = int(log.findCaller()[2][3:])
    if use_example:
        di = ""
    data_tuple = get_input(di, "\n", str, override=False)  # noqa: F841
    results = []

    return display_results(day=day, results=results, log=log)


def day13(use_example=False, log=_LOG):  # noqa: FBT002
    """
    Unsolved.

    Args:
        use_example (bool): Use the example data set
        log (slt.EasyLogger, optional): Logger object
    Returns:
        integer number of results
    """
    day = di = int(log.findCaller()[2][3:])
    if use_example:
        di = ""
    data_tuple = get_input(di, "\n", str, override=False)  # noqa: F841
    results = []

    return display_results(day=day, results=results, log=log)


def day14(use_example=False, log=_LOG):  # noqa: FBT002
    """
    Unsolved.

    Args:
        use_example (bool): Use the example data set
        log (slt.EasyLogger, optional): Logger object
    Returns:
        integer number of results
    """
    day = di = int(log.findCaller()[2][3:])
    if use_example:
        di = ""
    data_tuple = get_input(di, "\n", str, override=False)  # noqa: F841
    results = []

    return display_results(day=day, results=results, log=log)


def day15(use_example=False, log=_LOG):  # noqa: FBT002
    """
    Unsolved.

    Args:
        use_example (bool): Use the example data set
        log (slt.EasyLogger, optional): Logger object
    Returns:
        integer number of results
    """
    day = di = int(log.findCaller()[2][3:])
    if use_example:
        di = ""
    data_tuple = get_input(di, "\n", str, override=False)  # noqa: F841
    results = []

    return display_results(day=day, results=results, log=log)


def day16(use_example=False, log=_LOG):  # noqa: FBT002
    """
    Unsolved.

    Args:
        use_example (bool): Use the example data set
        log (slt.EasyLogger, optional): Logger object
    Returns:
        integer number of results
    """
    day = di = int(log.findCaller()[2][3:])
    if use_example:
        di = ""
    data_tuple = get_input(di, "\n", str, override=False)  # noqa: F841
    results = []

    return display_results(day=day, results=results, log=log)


def day17(use_example=False, log=_LOG):  # noqa: FBT002
    """
    Unsolved.

    Args:
        use_example (bool): Use the example data set
        log (slt.EasyLogger, optional): Logger object
    Returns:
        integer number of results
    """
    day = di = int(log.findCaller()[2][3:])
    if use_example:
        di = ""
    data_tuple = get_input(di, "\n", str, override=False)  # noqa: F841
    results = []

    return display_results(day=day, results=results, log=log)


def day18(use_example=False, log=_LOG):  # noqa: FBT002
    """
    Unsolved.

    Args:
        use_example (bool): Use the example data set
        log (slt.EasyLogger, optional): Logger object
    Returns:
        integer number of results
    """
    day = di = int(log.findCaller()[2][3:])
    if use_example:
        di = ""
    data_tuple = get_input(di, "\n", str, override=False)  # noqa: F841
    results = []

    return display_results(day=day, results=results, log=log)


def day19(use_example=False, log=_LOG):  # noqa: FBT002
    """
    Unsolved.

    Args:
        use_example (bool): Use the example data set
        log (slt.EasyLogger, optional): Logger object
    Returns:
        integer number of results
    """
    day = di = int(log.findCaller()[2][3:])
    if use_example:
        di = ""
    data_tuple = get_input(di, "\n", str, override=False)  # noqa: F841
    results = []

    return display_results(day=day, results=results, log=log)


def day20(use_example=False, log=_LOG):  # noqa: FBT002
    """
    Unsolved.

    Args:
        use_example (bool): Use the example data set
        log (slt.EasyLogger, optional): Logger object
    Returns:
        integer number of results
    """
    day = di = int(log.findCaller()[2][3:])
    if use_example:
        di = ""
    data_tuple = get_input(di, "\n", str, override=False)  # noqa: F841
    results = []

    return display_results(day=day, results=results, log=log)


def day21(use_example=False, log=_LOG):  # noqa: FBT002
    """
    Unsolved.

    Args:
        use_example (bool): Use the example data set
        log (slt.EasyLogger, optional): Logger object
    Returns:
        integer number of results
    """
    day = di = int(log.findCaller()[2][3:])
    if use_example:
        di = ""
    data_tuple = get_input(di, "\n", str, override=False)  # noqa: F841
    results = []

    return display_results(day=day, results=results, log=log)


def day22(use_example=False, log=_LOG):  # noqa: FBT002
    """
    Unsolved.

    Args:
        use_example (bool): Use the example data set
        log (slt.EasyLogger, optional): Logger object
    Returns:
        integer number of results
    """
    day = di = int(log.findCaller()[2][3:])
    if use_example:
        di = ""
    data_tuple = get_input(di, "\n", str, override=False)  # noqa: F841
    results = []

    return display_results(day=day, results=results, log=log)


def day23(use_example=False, log=_LOG):  # noqa: FBT002
    """
    Unsolved.

    Args:
        use_example (bool): Use the example data set
        log (slt.EasyLogger, optional): Logger object
    Returns:
        integer number of results
    """
    day = di = int(log.findCaller()[2][3:])
    if use_example:
        di = ""
    data_tuple = get_input(di, "\n", str, override=False)  # noqa: F841
    results = []

    return display_results(day=day, results=results, log=log)


def day24(use_example=False, log=_LOG):  # noqa: FBT002
    """
    Unsolved.

    Args:
        use_example (bool): Use the example data set
        log (slt.EasyLogger, optional): Logger object
    Returns:
        integer number of results
    """
    day = di = int(log.findCaller()[2][3:])
    if use_example:
        di = ""
    data_tuple = get_input(di, "\n", str, override=False)  # noqa: F841
    results = []

    return display_results(day=day, results=results, log=log)


def day25(use_example=False, log=_LOG):  # noqa: FBT002
    """
    Unsolved.

    Args:
        use_example (bool): Use the example data set
        log (slt.EasyLogger, optional): Logger object
    Returns:
        integer number of results
    """
    day = di = int(log.findCaller()[2][3:])
    if use_example:
        di = ""
    data_tuple = get_input(di, "\n", str, override=False)  # noqa: F841
    results = []

    return display_results(day=day, results=results, log=log)


def go(day, use_example=False, log=_LOG):  # noqa: FBT002
    """Runs the given day's solution to the puzzle.

    Args:
        day (int): The day of December
        use_example (bool, optional): Use example data instead of the web data. Defaults to False.
        log (slt.EasyLogger, optional): Logger object. Defaults to _LOG.

    Returns:
        _type_: _description_
    """
    if not isinstance(log, slt.EasyLogger):
        err_str = f"log={log} invalid.  Must be an slt.EasyLogger not {type(log)}"
        raise TypeError(err_str)
    if not isinstance(use_example, bool):
        err_str = f"use_example={use_example} invalid.  Must be a bool not {type(use_example)}"
        raise TypeError(err_str)
    min_day = 1
    max_day = 25
    if not isinstance(day, int) and not min_day <= day <= max_day:
        err_str = f"day={day} invalid.  Must be {min_day}-{max_day}"
        raise ValueError(err_str)
    return getattr(sys.modules.get(__name__), f"day{day}")(use_example=use_example, log=log)


def run_all(use_example=False, log=_LOG):  # noqa: FBT002
    """Run the solution for each day's puzzle."""
    if not isinstance(log, slt.EasyLogger):
        err_str = f"log={log} invalid.  Must be an slt.EasyLogger not {type(log)}"
        raise TypeError(err_str)
    if not isinstance(use_example, bool):
        log.error("use_example=%s invalid.  Must be a bool", use_example)
        return
    day_dict = {"Completed": [], "Unfinished": [], "Broken": []}
    for day in range(1, 26, 1):
        try:
            log.result(slt.FG.icyan("Day%d Start" % day))
            ret_code = getattr(sys.modules.get(__name__), f"day{day}")(use_example=use_example, log=log)
            if ret_code == 2:
                day_dict["Completed"].append(day)
            else:
                day_dict["Unfinished"].append(day)
        except Exception:
            log.exception("Day%d threw Exception", day)
            day_dict["Broken"].append(day)
        log.result("*" * 79)

    for day_key, day_list in day_dict.items():
        output_str = "{0:{fill}{align}{width}}".format(day_key + " Days:", width=16, align="<", fill=" ")
        for entry in day_list:
            output_str += "{0:{width}}, ".format(entry, width=2)
        if day_list:
            output_str = output_str[:-2]
        log.result(output_str)

# **********************************************************************************************
# ******************************* A Collection of example classes ******************************
# **********************************************************************************************
class BinTree:
    """Binary Tree Node."""
    def __init__(self, value):
        """Instantiates an instance of the class."""
        self.left = None
        self.right = None
        self.value = value

    def show_tree(self, log_level="RESULT", log=_LOG):
        """Display the Tree and all the leaves with the given logger."""
        if self.left:
            self.left.show_tree()
        log_level_value = int(slt.getLogLevel(log_level.upper()))
        log.log(log_level_value, "%s, ", self.value)
        if self.right:
            self.right.show_tree()

    def insert(self, value):
        """Insert data into tree in ascending order."""
        if value < self.value:
            if self.left is None:
                self.left = value
            else:
                self.left.insert(value)
        elif value > self.value:
            if self.right is None:
                self.right = value
            else:
                self.right.insert(value)
        else:
            raise RuntimeError("insert value=%s matches self.value" % value)


class LineSeg:
    """Line Segment class with start and end x and y coordinates."""
    def __init__(self, x1, y1, x2, y2):
        """Instantiates an instance of the class."""
        assert isinstance(x1, int), f"x1={x1} invalid.  Must be int, not {type(x1)}"  # noqa: S101
        assert isinstance(y1, int), f"y1={y1} invalid.  Must be int, not {type(y1)}"  # noqa: S101
        assert isinstance(x2, int), f"x2={x2} invalid.  Must be int, not {type(x2)}"  # noqa: S101
        assert isinstance(y2, int), f"y2={y2} invalid.  Must be int, not {type(y2)}"  # noqa: S101
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def __str__(self):
        """Return a string representation for the class instance."""
        return "%3d, %3d -> %3d, %3d" % (self.x1, self.y1, self.x2, self.y2)


class Knot:
    """A knob location in a rope."""
    def __init__(self, name, row, col, prv):
        """Instantiates an instance of the class."""
        assert isinstance(row, int), f"row={row} invalid.  Must be int, not {type(row)}"  # noqa: S101
        assert isinstance(col, int), f"col={col} invalid.  Must be int, not {type(col)}"  # noqa: S101
        self.name = name
        self.row = row
        self.col = col
        self.prev = prv
        self.next = None

    def __str__(self):
        """Return a string representation for the class instance."""
        return "%s: %3d, %3d" % (self.name, self.row, self.col)


class DirNode:
    """A file system Directory class used to build a file system."""
    def __init__(self, parent, name):
        """Instantiates an instance of the class."""
        self.name = name
        # Is it better to store the path or dynamically build the path?
        if parent is None:
            self.parent = self
            self.path = self.name
        else:
            self.parent = parent
            self.path = parent.path + "." + self.name
        self.sub_dirs = []
        self.file_dict = {}
        self.current = False

    def __str__(self, prefix=""):
        """Return a string representation for the class instance."""
        ret_str = f"{prefix}{self.name} (dir)  "
        if self.current:
            ret_str += slt.FG.iyellow("<----------------------------------------")
        ret_str += "\n"
        for filename, size in self.file_dict.items():
            ret_str += "  %s%s (file, size=%d\n" % (prefix, filename, size)
        if self.sub_dirs:
            for sub_dir in self.sub_dirs:
                ret_str += sub_dir.__str__(prefix + "    ")
        return ret_str

    def get_size(self):
        """Return the size."""
        total_size = 0
        for size in self.file_dict.values():
            total_size += size
        for sub_dir in self.sub_dirs:
            total_size += sub_dir.get_size()
        return total_size

    def get_path(self):
        """Return the path as a string."""
        # Alternate to storing the path.  Not sure which is better
        the_path = self.name
        cur_dir = self
        while cur_dir.parent.name != "/":
            the_path = cur_dir.parent.name + "." + the_path
            cur_dir = cur_dir.parent
        return "/." + the_path


class Graph:
    """A class that creates a Graph Data structure."""
    def __init__(self, nodes, init_graph):
        """Instantiates an instance of the class."""
        self.nodes = nodes
        self.graph = self.construct_graph(nodes, init_graph)

    def construct_graph(self, nodes, init_graph):  # noqa: PLR6301
        """
        This method makes sure that the graph is symmetrical.

        In other words, if there's a path from node A to B with a value V, there needs to be a path from node B to node A with a value V.
        """
        graph = {}
        for node in nodes:
            graph[node] = {}

        graph.update(init_graph)

        for node, edges in graph.items():
            for adjacent_node, value in edges.items():
                if graph[adjacent_node].get(node, False) is False:
                    graph[adjacent_node][node] = value

        return graph

    def get_nodes(self):
        """Returns the nodes of the graph."""
        return self.nodes

    def get_outgoing_edges(self, node):
        """Returns the neighbors of a node."""
        connections = []
        for out_node in self.nodes:
            if self.graph[node].get(out_node, False) is not False:
                connections.append(out_node)  # noqa: PERF401
        return connections

    def value(self, node1, node2):
        """Returns the value of an edge between two nodes."""
        return self.graph[node1][node2]


def dfw(visited, cur_dir, big_dict, small_dict, min_size, log=_LOG):
    """Recursive Depth-First Walk of tree."""
    if cur_dir not in visited:
        visited.add(cur_dir)
        # Collect the sizes
        cur_size = cur_dir.get_size()
        # log.debug("cur_dir %s %d" % (cur_dir.name, cur_size))
        if cur_size < 100000:
            big_dict[cur_dir.path] = cur_size
            # big_dict[cur_dir.get_path()] = cur_size  # Alternate
        if cur_size > min_size:
            small_dict[cur_dir.path] = cur_size
            # small_dict[cur_dir.get_path()] = cur_size  # Alternate
        for sub_dir in cur_dir.sub_dirs:
            dfw(visited, sub_dir, big_dict, small_dict, min_size, log)
# **********************************************************************************************
# **********************************************************************************************
