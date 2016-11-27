import csv
import itertools
from matplotlib import pyplot
import numpy
from scipy import stats
import random

from modelutils.misc import *

from most_common_lineups import PITCHER, LINEUPS, INCOMPLETE_TEAMS, map_to_players

class Player:
    WEAK_HITTER=0
    MIDDLE_HITTER=1
    POWER_HITTER=2

    def __init__(self, id=None, first_name=None, last_name=None, at_bats=None, hits=None, doubles=None, triples=None,
                 hrs=None, obp=None, ba=None, slug=None, double_play_occurrences=None, walks=None, hbp=None):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.at_bats = at_bats
        self.hits = hits
        if some(hits) and some(doubles) and some(triples) and some(hrs):
            self.singles = hits-doubles-triples-hrs
        else:
            self.singles = None
        self.doubles = doubles
        self.triples = triples
        self.hrs = hrs
        self.on_base_percentage = obp
        self.batting_average = ba
        self.slugging_percentage = slug
        self.double_play_occurrences = double_play_occurrences
        self.walks = walks
        self.hbp = hbp
        if some(hits) and some(walks) and some(hbp) and some(at_bats):
            self.hit_average = float(self.hits)/float(self.at_bats + self.walks + self.hbp)
        else:
            print str(hits) + ' ' + str(walks) + ' ' + str(hbp) + ' ' + str(at_bats)
            print str(first_name) + str(last_name)
            self.hit_average = None

    @property
    def player_type(self):
        if self.hrs > self.doubles:
            return Player.POWER_HITTER
        elif self.doubles > 2*self.hrs or (self.doubles == 0 and self.hrs == 0):
            return Player.WEAK_HITTER
        else:
            return Player.MIDDLE_HITTER

    def hit_check(self, hit_seed, slug_seed):
        if hit_seed >= self.on_base_percentage:
            return 0
        elif hit_seed >= self.batting_average:
            return 1
        else:
            return self.bases_check(slug_seed)

    def bases_check(self, slug_seed):
        def single_prob(x):
            return .75 - (2./3)*x
        def double_prob(x):
            return .15 + x/3.
        def homer_prob(x):
            return .1 + x/3.

        x = (3./4)*(self.slugging_percentage/self.batting_average) - 1.0875
        if x > .3:
            x = .3
        elif x < 0:
            x = 0

        if slug_seed < single_prob(x):
            return 1
        elif slug_seed < (single_prob(x) + double_prob(x)):
            return 2
        else:
            return 4

# precision_hitter = Player(ba=.310, obp=.375, slug=.45)
# slugger = Player(ba=.290, obp=.350, slug=.52)
# bad_hitter = Player(ba=.250, obp=.330, slug=.4)
#
# proto_lineup = [
#     precision_hitter,
#     precision_hitter,
#     precision_hitter,
#     slugger,
#     slugger,
#     slugger,
#     bad_hitter,
#     bad_hitter,
#     bad_hitter
# ]
#
# redsox_lineup = [
#     Player(
#         ba=.318,
#         obp=.363,
#         slug=.534
#     ),
#     Player(
#         ba=.318,
#         obp=.376,
#         slug=.449
#     ),
#     Player(
#         ba=.294,
#         obp=.356,
#         slug=.446
#     ),
#     Player(
#         ba=.315,
#         obp=.401,
#         slug=.620
#     ),
#     Player(
#         ba=.286,
#         obp=.361,
#         slug=.505
#     ),
#     Player(
#         ba=.242,
#         obp=.306,
#         slug=.421
#     ),
#     Player(
#         ba=.255,
#         obp=.322,
#         slug=.383
#     ),
#     Player(
#         ba=.310,
#         obp=.369,
#         slug=.476
#     ),
#     Player(
#         ba=.267,
#         obp=.349,
#         slug=.486
#     ),
# ]


def run_inning(lineup, current_place=0):
    outs = 0
    current_bases = {k: False for k in (1, 2, 3)}
    runs = 0
    while outs < 3:
        hit_seed = random.random()
        slug_seed = random.random()
        at_bat_result = lineup[current_place].hit_check(slug_seed=slug_seed, hit_seed=hit_seed)
        if at_bat_result == 0:
            outs += 1
        else:
            for runner in (3, 2, 1):
                if current_bases[runner]:
                    current_bases[runner] = False
                    if runner + at_bat_result <= 3:
                        current_bases[runner + at_bat_result] = True
                    else:
                        runs += 1
            if at_bat_result == 4:
                runs += 1
            else:
                current_bases[at_bat_result] = True
        current_place = (current_place + 1) % 9
    return runs, current_place


def run_game(lineup):
    current_place = 0
    score = 0
    for i in (1, 2, 3, 4, 5, 6, 7, 8, 9):
        runs, current_place = run_inning(lineup, current_place)
        score += runs
    return score


def run_simulation(lineup):
    all_scores = []
    for i in xrange(1000):
        all_scores.append(run_game(lineup))
    return all_scores


def collect_players():
    player_data_reader = csv.reader(open('data/mlb2014.csv', 'rb'))
    # Keys
    PLAYER_ID=0
    FIRST_NAME=1
    LAST_NAME=2
    AB=12
    HITS=14
    DOUBLES=15
    TRIPLES=16
    HR=17
    BB=21
    HBP=24
    AVG=28
    OBP=29
    SLG=30
    GIDP=27
    players = []
    for player in player_data_reader:
        # Skip the first line
        if 'playerID' in player:
            continue
        # Dismiss players who didn't play enough
        elif fucking_cast(int, player[AB]) < 200:
            continue
        else:
            players.append(Player(
                id=player[PLAYER_ID],
                first_name=player[FIRST_NAME],
                last_name=player[LAST_NAME],
                at_bats=fucking_cast(int, player[AB]),
                hits=fucking_cast(int, player[HITS]),
                doubles=fucking_cast(int, player[DOUBLES]),
                triples=fucking_cast(int, player[TRIPLES]),
                hrs=fucking_cast(int, player[HR]),
                ba=fucking_cast(float, player[AVG]),
                obp=fucking_cast(float, player[OBP]),
                slug=fucking_cast(float, player[SLG]),
                double_play_occurrences=fucking_cast(int, player[GIDP]),
                walks=fucking_cast(int, player[BB]),
                hbp=fucking_cast(int, player[HBP])
            ))
    # Generic pitcher rarely gets a hit, but when they do it's a single.
    generic_pitcher = Player(
        last_name=PITCHER,
        ba=.175,
        obp=.200,
        slug=.175,
        doubles=0,
        triples=0,
        hrs=0,
        hits=10,
        walks=0,
        hbp=0,
        at_bats=57
    )
    players.append(generic_pitcher)
    return players



def create_player_graphs(players):
    x_attr = 'singles'
    x_axis = map_to_attr_op(x_attr, 'hits', players)
    pyplot.hist(x_axis, bins=20)
    pyplot.xlabel(x_attr)
    print numpy.mean(x_axis)
    print numpy.std(x_axis)
    pyplot.show()

    x_attr = 'hit_average'
    x_axis = map_to_attr(x_attr, players)
    pyplot.hist(x_axis, bins=20)
    pyplot.xlabel(x_attr)
    print numpy.mean(x_axis)
    print numpy.std(x_axis)
    pyplot.show()

    x_axis = map_to_attr_op('on_base_percentage', 'hit_average', players, 'diff')
    pyplot.hist(x_axis, bins=20)
    pyplot.xlabel('walkiness')
    print numpy.mean(x_axis)
    print numpy.std(x_axis)
    pyplot.show()


def create_hit_correlation_graphs(players):
    x_attr = 'singles'
    y_attr = 'doubles'
    x_axis = map_to_attr_op(x_attr, 'hits', players)
    y_axis = map_to_attr_op(y_attr, 'hits', players)
    pyplot.scatter(x_axis, y_axis)
    pyplot.xlabel(x_attr)
    pyplot.ylabel(y_attr)
    print stats.linregress(x_axis, y_axis)
    pyplot.show()

    x_attr = 'singles'
    y_attr = 'hrs'
    x_axis = map_to_attr_op(x_attr, 'hits', players)
    y_axis = map_to_attr_op(y_attr, 'hits', players)
    pyplot.scatter(x_axis, y_axis)
    pyplot.xlabel(x_attr)
    pyplot.ylabel(y_attr)
    print stats.linregress(x_axis, y_axis)
    pyplot.show()

    x_attr = 'hrs'
    y_attr = 'doubles'
    x_axis = map_to_attr_op(x_attr, 'hits', players)
    y_axis = map_to_attr_op(y_attr, 'hits', players)
    pyplot.scatter(x_axis, y_axis)
    pyplot.xlabel(x_attr)
    pyplot.ylabel(y_attr)
    print stats.linregress(x_axis, y_axis)
    pyplot.show()


def create_lineup_graphs(players):
    batting_order = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    batting_averages = []
    obp_minus_ba = []
    singles_ratios = []
    batter_types = []
    valid_lineups = []
    for lineup in LINEUPS:
        if lineup in INCOMPLETE_TEAMS:
            continue
        batting_averages.append(map_to_attr('hit_average', map_to_players(LINEUPS[lineup], players)))
        singles_ratios.append(map_to_attr_op('singles', 'hits', map_to_players(LINEUPS[lineup], players)))
        obp_minus_ba.append(map_to_attr_op('on_base_percentage', 'hit_average', map_to_players(LINEUPS[lineup], players), 'diff'))
        batter_types.append(map_to_attr('player_type', map_to_players(LINEUPS[lineup], players)))
        valid_lineups.append(lineup)

    axes = pyplot.gca()
    axes.set_xlim([0, 12])

    handles = []
    for i, plot_data in enumerate(batting_averages):
        handle, = pyplot.plot(
            batting_order,
            plot_data,
            'o',
            label=valid_lineups[i]
        )
        handles.append(handle)

    pyplot.legend(handles=handles)
    pyplot.ylabel('hit_averages')
    pyplot.show()

    axes = pyplot.gca()
    axes.set_xlim([0, 12])
    handles = []
    for i, plot_data in enumerate(obp_minus_ba):
        handle, = pyplot.plot(
            batting_order,
            plot_data,
            'o',
            label=valid_lineups[i]
        )
        handles.append(handle)

    pyplot.legend(handles=handles)
    pyplot.ylabel('walkiness')
    pyplot.show()

    axes = pyplot.gca()
    axes.set_xlim([0, 12])
    handles = []
    for i, plot_data in enumerate(singles_ratios):
        handle, = pyplot.plot(
            batting_order,
            plot_data,
            'o',
            label=valid_lineups[i]
        )
        handles.append(handle)

    pyplot.legend(handles=handles)
    pyplot.ylabel('singles_ratios')
    pyplot.show()

    axes = pyplot.gca()
    axes.set_xlim([0, 12])
    handles = []
    weak_batter_counts = [0] * 9
    middle_batter_counts = [0] * 9
    power_batter_counts = [0] * 9

    for team in batter_types:
        for i, batter_type in enumerate(team):
            if batter_type == Player.WEAK_HITTER:
                weak_batter_counts[i] += 1
            elif batter_type == Player.MIDDLE_HITTER:
                middle_batter_counts[i] += 1
            else:
                power_batter_counts[i] += 1

    for i, plot_data in enumerate((weak_batter_counts, middle_batter_counts, power_batter_counts)):
        handle, = pyplot.plot(
            batting_order,
            plot_data,
            label=('weak', 'middle', 'power')[i]
        )
        handles.append(handle)

    pyplot.legend(handles=handles)
    pyplot.ylabel('player_type')
    pyplot.show()


    batting_averages_aves, batting_averages_stdvs = column_averages(batting_averages)
    obp_minus_ba_aves, obp_minus_ba_stdvs = column_averages(obp_minus_ba)
    singles_ratios_aves, singles_ratios_stdvs = column_averages(singles_ratios)

    axes = pyplot.gca()
    axes.set_xlim([0, 12])
    pyplot.errorbar(batting_order, batting_averages_aves, yerr=batting_averages_stdvs)
    pyplot.ylabel('hit_averages')
    pyplot.show()

    axes = pyplot.gca()
    axes.set_xlim([0, 12])
    pyplot.errorbar(batting_order, obp_minus_ba_aves, yerr=obp_minus_ba_stdvs)
    pyplot.ylabel('walkiness')
    pyplot.show()

    axes = pyplot.gca()
    axes.set_xlim([0, 12])
    pyplot.errorbar(batting_order, singles_ratios_aves, yerr=singles_ratios_stdvs)
    pyplot.ylabel('singles_ratios')
    pyplot.show()


def compute_regression(players):
    best = 0
    best_tuple = None
    best_slope = None
    best_inter = None
    x_attr = 'singles'

    def hrs(slope, inter):
        return lambda x: slope*x + inter
    def dbls(slope, inter):
        return lambda x: (1-inter) - (slope + 1)*x
    # HR = a + bS
    # D = 1 - a - (b + 1)S

    x_axis = map_to_attr_op(x_attr, 'hits', players)
    doubles = map_to_attr_op('doubles', 'hits', players)
    homers = map_to_attr_op('hrs', 'hits', players)
    for slope in range(-100, 0, 1):
        slope = slope/100.0
        print slope
        for y_inter in range(100, 0, -1):
            y_inter = y_inter/100.0
            result_hrs = r_squared(x_axis, homers, hrs(slope, y_inter))
            result_double = r_squared(x_axis, doubles, dbls(slope, y_inter))
            if 0 < result_hrs < 1 and 0 < result_double < 1:
                if result_hrs + result_double > best:
                    best = result_hrs + result_double
                    best_tuple = (result_hrs, result_double)
                    best_slope = slope
                    best_inter = y_inter
            else:
                continue

    return best_tuple, best_slope, best_inter
    # return stats.linregress(x_axis, y_axis)

if __name__ == '__main__':
    import sys
    print_num = sys.argv[1] if len(sys.argv) > 1 else 10

    players = collect_players()
    # for player in players:
    #     if 0.79 <= player.singles/float(player.hits) <= 0.81:
    #         print player.first_name + ' ' + player.last_name
    #         print player.hrs/float(player.hits)
    #         print player.doubles/float(player.hits)
    #         print player.hits

    # players = filter(lambda x: x.hrs > x.doubles, players)
    # print compute_regression(players)
    # create_hit_correlation_graphs(players)
    # create_player_graphs(players)
    create_lineup_graphs(players)
    # import most_common_lineups
    # most_common_lineups.validate_lineups(players)

    # my_order = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    # results = {}
    # counter = 1
    # for new_order in itertools.permutations(my_order):
    #     if counter % 1000 == 0:
    #         print counter
    #     scores = run_simulation([proto_lineup[x] for x in new_order])
    #     results[(sum(scores) / float(len(scores)), numpy.std(scores))] = list(new_order)
    #     counter += 1
    #
    # def compare_results(result_tuple_a, result_tuple_b):
    #     ave_a, std_a = result_tuple_a[0]
    #     ave_b, std_b = result_tuple_b[0]
    #     if ave_a == ave_b:
    #         if std_b > std_a:
    #             return -1
    #         else:
    #             return 1
    #     elif ave_a > ave_b:
    #         return -1
    #     else:
    #         return 1
    #
    # result_items = results.items()
    # result_items.sort(compare_results)
    #
    # for ave_and_std, order in result_items:
    #     if print_num > 0 or order == sorted(order):
    #         print "Lineup Order: {}".format(order)
    #         print 'Average score: {}'.format(ave_and_std[0])
    #         print 'Score stdev: {}'.format(ave_and_std[1])
    #         print_num -= 1