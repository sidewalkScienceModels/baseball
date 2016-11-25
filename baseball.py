import csv
import itertools
from matplotlib import pyplot
import numpy
from scipy import stats
import random

from misc_utils import *


class Player:
    def __init__(self, id=None, first_name=None, last_name=None, at_bats=None, hits=None, doubles=None, triples=None,
                 hrs=None, obp=None, ba=None, slug=None):
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

precision_hitter = Player(ba=.310, obp=.375, slug=.45)
slugger = Player(ba=.290, obp=.350, slug=.52)
bad_hitter = Player(ba=.250, obp=.330, slug=.4)

proto_lineup = [
    precision_hitter,
    precision_hitter,
    precision_hitter,
    slugger,
    slugger,
    slugger,
    bad_hitter,
    bad_hitter,
    bad_hitter
]

redsox_lineup = [
    Player(
        ba=.318,
        obp=.363,
        slug=.534
    ),
    Player(
        ba=.318,
        obp=.376,
        slug=.449
    ),
    Player(
        ba=.294,
        obp=.356,
        slug=.446
    ),
    Player(
        ba=.315,
        obp=.401,
        slug=.620
    ),
    Player(
        ba=.286,
        obp=.361,
        slug=.505
    ),
    Player(
        ba=.242,
        obp=.306,
        slug=.421
    ),
    Player(
        ba=.255,
        obp=.322,
        slug=.383
    ),
    Player(
        ba=.310,
        obp=.369,
        slug=.476
    ),
    Player(
        ba=.267,
        obp=.349,
        slug=.486
    ),
]


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
    player_data_reader = csv.reader(open('data/mlb2012.csv', 'rb'))
    # Keys
    PLAYER_ID=0
    FIRST_NAME=1
    LAST_NAME=2
    AB=12
    HITS=14
    DOUBLES=15
    TRIPLES=16
    HR=17
    AVG=28
    OBP=29
    SLG=30
    players = []
    for player in player_data_reader:
        # Skip the first line
        if 'playerID' in player:
            continue
        # Dismiss players who didn't play enough
        elif fucking_cast(int, player[AB]) < 300:
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
                slug=fucking_cast(float, player[SLG])
            ))
    return players



def create_player_graphs(players):
    x_attr = 'singles'
    y_attr = 'doubles'
    x_axis = map_to_attr_op(x_attr, 'hits', players)
    y_axis = map_to_attr_op(y_attr, 'hits', players)
    pyplot.scatter(x_axis, y_axis)
    pyplot.xlabel(x_attr)
    pyplot.ylabel(y_attr)
    print numpy.mean(x_axis)
    print numpy.std(x_axis)
    pyplot.show()


def compute_regression(players):
    best = 0
    best_slope = None
    best_inter = None
    x_attr = 'singles'
    y_attr = 'doubles'
    x_axis = map_to_attr_op(x_attr, 'hits', players)
    y_axis = map_to_attr_op(y_attr, 'hits', players)

    return stats.linregress(x_axis, y_axis)

if __name__ == '__main__':
    import sys
    print_num = sys.argv[1] if len(sys.argv) > 1 else 10

    players = collect_players()
    print compute_regression(players)
    create_player_graphs(players)
    asdasd

    my_order = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    results = {}
    counter = 1
    for new_order in itertools.permutations(my_order):
        if counter % 1000 == 0:
            print counter
        scores = run_simulation([proto_lineup[x] for x in new_order])
        results[(sum(scores) / float(len(scores)), numpy.std(scores))] = list(new_order)
        counter += 1

    def compare_results(result_tuple_a, result_tuple_b):
        ave_a, std_a = result_tuple_a[0]
        ave_b, std_b = result_tuple_b[0]
        if ave_a == ave_b:
            if std_b > std_a:
                return -1
            else:
                return 1
        elif ave_a > ave_b:
            return -1
        else:
            return 1

    result_items = results.items()
    result_items.sort(compare_results)

    for ave_and_std, order in result_items:
        if print_num > 0 or order == sorted(order):
            print "Lineup Order: {}".format(order)
            print 'Average score: {}'.format(ave_and_std[0])
            print 'Score stdev: {}'.format(ave_and_std[1])
            print_num -= 1