import json
import random
import collections
import sys

# external libraries
import matplotlib.pyplot as plt


def json_loader():
    json_file = open('game_config.json', encoding="utf-8")

    # this try/except excludes most errors
    try:
        json_data = json.load(json_file)
    except ValueError:
        print('JSON file is not made properly.\n'
              'Closing the app...')
        sys.exit()
    json_file.close()

    if json_data['game']['reelsNo'] != len(json_data['game']['reels']):
        print('In JSON file is discrepancy between declared quantity of reels\n'
              'and number of created reels. [reelsNo != reels]\n'
              'Closing the app...')
        sys.exit()

    if json_data['game']['visibleSymbols'] < 1:
        print('Number of visibleSymbols in JSON file is less than 1.\n'
              'Closing the app...')
        sys.exit()

    for reel in json_data['game']['reels']:
        if not reel:
            print('One or more reels are empty.\n'
                  'Closing the app...')
            sys.exit()

    for winline in json_data['game']['winlines']:
        if not winline:
            print('One or more win lines are empty.\n'
                  'Closing the app...')
            sys.exit()

    return json_data


data = json_loader()

reels_no = data['game']['reelsNo']
reels = data['game']['reels']
visible_symbols = data['game']['visibleSymbols']
win_lines = data['game']['winlines']

# this list include data if all reels from JSON file
reelsList = []
# this list includes all symbols which contributed a won
won_symbols = []


def reel_on(visible_symbols, winlines):
    # this list contains tulpes of index and values of symbols in reels
    reel_randoms = []
    # this list contains extracted indexes from reel_randoms list
    reel_index = []

    # variable for storing points
    points_won = 0

    # drawing items in row 0
    for reel in range(0, len(reelsList)):
        reel_randoms.append(random.choice(list(enumerate(reelsList[reel]))))
        index, item = reel_randoms[reel]
        reel_index.append(index)

    # list containing all visible symbols
    all_visible_symbols = []

    # loop which creates visible symbols based on items from row 0
    for x in range(0, visible_symbols):
        # temporary loop for single row
        tmp_in_loop = []
        for y in range(0, len(reelsList)):
            # protection from getting out of range index
            try:
                item = reelsList[y][reel_index[y] + x]
            except IndexError:
                item = reelsList[y][reel_index[y] + x - len(reelsList[y])]

            tmp_in_loop.append(item)

        all_visible_symbols.append(tmp_in_loop)

    print('-------------------\n'
          'Preview of the spin:\n'
          '{}\n'
          '-------------------'.format(all_visible_symbols))

    # this loop checks if symbol win conditions are met in each winline
    for x in range(0, len(winlines)):
        # this list contains all symbols included in winline
        winline_symbols = []
        # this list contains symbols with 100% winrate
        banned_from_winrate = []

        # this loop reads all symbols in winline
        for y in range(0, len(all_visible_symbols)):
            # visible symbol matching winline
            # [row[which winline][which coord]][column]
            winline_symbols.append(all_visible_symbols[winlines[x][y]][y])

        counter = collections.Counter(winline_symbols)

        # this loop checks win conditions in winline
        for key, value in counter.items():
            win_parameters_data = data['game']['symbols'][key]['win']

            for n in range(0, len(win_parameters_data)):
                no_value = win_parameters_data[n].get('no')

                if value == no_value:
                    banned_from_winrate.append(key)
                    won_symbols.append(key)
                    points_won = points_won + win_parameters_data[n].get('win')
                    print('Chance for win on line {} by {} symbol: 100%'
                          .format(winlines[n], key))

        # this loop calculates chance for win for symbols that didn't won
        for xx in range(0, len(winline_symbols)):
            if winline_symbols[xx] in banned_from_winrate:
                continue

            ignored_symbols = []
            win_rate = 0
            no_match_symbols = 0  # counter for entering if condition inside yy loop
            ignored_symbols.append(winline_symbols[xx])

            for yy in range(0, len(winline_symbols)):
                if winline_symbols[yy] in ignored_symbols:
                    continue
                if winline_symbols[yy] != winline_symbols[xx]:
                    win_rate = win_rate +\
                               (reelsList[yy].count(winline_symbols[xx])
                                / len(reelsList[yy])*100)
                    no_match_symbols = no_match_symbols + 1

            # protection from division by 0
            try:
                win_rate = win_rate / no_match_symbols
            except ZeroDivisionError:
                win_rate = 0

            print('Chance for win on line {} by {} symbol: {}%'
                  .format(winlines[x], winline_symbols[xx], int(win_rate)))
            banned_from_winrate.append(winline_symbols[xx])

    return points_won


def main():
    # this loop gets all reels with symbols it contains
    for x in range(0, reels_no):
        reelsList.append(reels[x])

    win_count = 0
    total_points = 0

    number_of_games = int(input('How many games?: '))

    if number_of_games < 1:
        print('You wrote too small number of games.\n'
              'Closing the app...')
        sys.exit()

    points_x, points_y = [], []

    for x in range(0, number_of_games):
        print('************************************\n'
              '** Sample number {}\n'
              '************************************'.format(x+1))
        points_from_one_turn = reel_on(visible_symbols, win_lines)

        # condition that checks won by points given
        if points_from_one_turn > 0:
            win_count = win_count + 1
            total_points = total_points + points_from_one_turn

        points_x.append(x)
        points_y.append(win_count)
        print('********** END OF SAMPLE {} **********\n'.format(x+1))

    print('Number of wins: {}/{}'.format(win_count, number_of_games))
    print("Frequency of wins: {}".format(win_count / number_of_games))
    print("Ratio of point_in/point_out: {}"
          .format(total_points / number_of_games))

    won_symbols_count = collections.Counter(won_symbols)
    if won_symbols:
        for key, value in won_symbols_count.items():
            symbol_winrate = value / win_count * 100
            print('Frequency of winning by {} symbol: {}%'
                  .format(key, symbol_winrate))
    else:
        print('Frequency of winning by symbol will not be calculated'
              ' - no winning symbols!')

    plt.grid(True)
    plt.title('Wins per games frequency')
    plt.xlabel('Games')
    plt.ylabel('Wins')
    plt.plot(points_x, points_y)
    plt.show()


main()
