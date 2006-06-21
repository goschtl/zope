"""Single-transferable voting implementation

As decribed at: http://en.wikipedia.org/wiki/Single_Transferable_Vote
(On June 21, 2006)

To run the example on the page, use:

    python stv.py treats 3

"""

import os, random, sys

def read(d):
    data = []
    for name in os.listdir(d):
        data.append((1.0, open(os.path.join(d, name)).read().strip().split()))

    random.shuffle(data)
    print 'votes'
    for w, vote in data:
        print vote
    print
    return data
    
def count(data, seats):
    quota = len(data)/(seats+1) + 1
    print 'quota', quota
    
    candidates = {}
    winners = {}
    losers = {}
    round = 1
    while data:

        # count votes
        for weight, vote in data:
            #print weight, vote
            while vote:
                candidate = vote.pop(0)
                if candidate in winners:
                    continue
                if candidate in losers:
                    continue

                score, votes = candidates.get(candidate, (0.0, []))
                score += weight
                votes.append((weight, vote))
                candidates[candidate] = score, votes
                break

        # find winners and harvest their alternate votes
        data = []
        for (candidate, (score, votes)) in candidates.items():
            if score >= quota:
                winners[candidate] = score
                candidates.pop(candidate)
                data.extend(
                    [((score-quota)/score * weight, vote)
                     for (weight, vote) in votes
                     if vote
                     ])

        print
        print 'round', round
        round += 1
        print '  winners', winners
        print '  losers', losers
        print '  candidates'
        for i in candidates.items():
            print '   ', i

        if len(winners) >= seats:
            print winners, [(c, s) for (c, (s, v)) in candidates.items()]
            return


        # If we don't have any votes to process from winners,
        # then take the votes from the losingest loser
        if not data and candidates:
            # No winners in last round, so pick losingest loser
            # and use their other votes.
            score, candidate, data = sorted(
                [(score, candidate, votes)
                 for (candidate, (score, votes)) in candidates.items()]
                )[0]
            losers[candidate] = score
            candidates.pop(candidate)

    print "Couldn't get enough winners.  Here's what we have so far:"
    print winners, [(c, s) for (c, (s, v)) in candidates.items()]


def main(args=None):
    if args == None:
        args = sys.argv[1:]

    d, seats = args
    if d == 'treats':
        data = [
            (1.0, ['orange', 'tangerine']),
            (1.0, ['orange', 'tangerine']),
            (1.0, ['orange', 'tangerine']),
            (1.0, ['orange', 'tangerine']),
            (1.0, ['tangerine', 'orange']),
            (1.0, ['tangerine', 'orange']),
            (1.0, ['chocolate', 'strawberry']),
            (1.0, ['chocolate', 'strawberry']),
            (1.0, ['chocolate', 'strawberry']),
            (1.0, ['chocolate', 'strawberry']),
            (1.0, ['chocolate', 'strawberry']),
            (1.0, ['chocolate', 'strawberry']),
            (1.0, ['chocolate', 'strawberry']),
            (1.0, ['chocolate', 'strawberry']),
            (1.0, ['chocolate', 'candy']),
            (1.0, ['chocolate', 'candy']),
            (1.0, ['chocolate', 'candy']),
            (1.0, ['chocolate', 'candy']),
            (1.0, ['strawberry']),
            (1.0, ['candy']),
            ]
    else:
        data = read(d)
    count(data, int(seats))

if __name__ == '__main__':
    main()
