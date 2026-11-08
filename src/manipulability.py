import itertools, fractions

def H(r):
    return sum(fractions.Fraction(1,i) for i in range(1,r+1))

def winners_AV(profile, m, k):
    # F_k^AV: score = approval count, pick top-k, tie-break by lower index
    score = [0]*m
    for A in profile:
        for c in A:
            score[c]+=1
    order = sorted(range(m), key=lambda c: (-score[c], c))
    return frozenset(order[:k])

def score_PAV(W, profile):
    s = fractions.Fraction(0)
    for A in profile:
        s += H(len(A & W))
    return s

def score_CC(W, profile):
    s = 0
    for A in profile:
        s += 1 if (A & W) else 0
    return s

def all_committees(m,k):
    return [frozenset(c) for c in itertools.combinations(range(m),k)]

def winner_by_score(profile, m, k, scorefunc):
    comms = all_committees(m,k)
    best = None
    bestscore = None
    for W in comms:
        sc = scorefunc(W, profile)
        key = (sc,)  # we want max sc, then lexicographically smallest tuple as tie-break
        Wtuple = tuple(sorted(W))
        if bestscore is None or sc > bestscore or (sc==bestscore and Wtuple < best[1]):
            bestscore = sc
            best = (W, Wtuple)
    return best[0], bestscore

def find_manipulation(n, m, k, rule):
    # rule in {'AV','PAV','CC'}
    results = []
    all_ballots = [frozenset(c) for r in range(m+1) for c in itertools.combinations(range(m), r)]
    # iterate over all profiles where each voter's true type is some non-empty subset (limit search space)
    types = [frozenset(c) for r in range(1, m) for c in itertools.combinations(range(m), r)]  # avoid empty/full to limit
    count=0
    for profile in itertools.product(types, repeat=n):
        count+=1
        if rule=='AV':
            W = winners_AV(profile, m, k)
        elif rule=='PAV':
            W,_ = winner_by_score(profile, m, k, score_PAV)
        elif rule=='CC':
            W,_ = winner_by_score(profile, m, k, score_CC)
        for i in range(n):
            Ai = profile[i]
            true_u = len(Ai & W)
            for Bi in all_ballots:
                if Bi == Ai: continue
                newprofile = list(profile)
                newprofile[i] = Bi
                newprofile = tuple(newprofile)
                if rule=='AV':
                    W2 = winners_AV(newprofile, m, k)
                elif rule=='PAV':
                    W2,_ = winner_by_score(newprofile, m, k, score_PAV)
                elif rule=='CC':
                    W2,_ = winner_by_score(newprofile, m, k, score_CC)
                new_u = len(Ai & W2)
                if new_u > true_u:
                    return dict(profile=profile, i=i, Ai=Ai, Bi=Bi, W=W, W2=W2, true_u=true_u, new_u=new_u, m=m,k=k,n=n)
    return None

# Search small instances for PAV manipulation
found=None
for m in [3,4]:
    for n in [2,3]:
        for k in range(1, m):
            res = find_manipulation(n, m, k, 'PAV')
            if res:
                found = res
                print("PAV manipulable example found: n=%d m=%d k=%d"%(n,m,k))
                print(res)
                break
        if found: break
    if found: break
if not found:
    print("no PAV example found in this range")

print("\n--- Checking AV rule for manipulability (should find NONE) ---")
found_av=None
for m in [3,4]:
    for n in [2,3]:
        for k in range(1, m):
            res = find_manipulation(n, m, k, 'AV')
            if res:
                found_av = res
                print("AV manipulable example FOUND (unexpected!):", res)
                break
        if found_av: break
    if found_av: break
if not found_av:
    print("Confirmed: no manipulable example found for AV rule in tested range (n<=3, m<=4) -> consistent with dominant strategy proof")

print("\n--- Checking CC rule for manipulability ---")
found_cc=None
for m in [3,4]:
    for n in [2,3]:
        for k in range(1, m):
            res = find_manipulation(n, m, k, 'CC')
            if res:
                found_cc = res
                print("CC manipulable example found: n=%d m=%d k=%d"%(n,m,k))
                print(res)
                break
        if found_cc: break
    if found_cc: break
if not found_cc:
    print("no CC example found in this range")

print("\n--- PAV manipulability across k, for fixed m=4 ---")
for m in [4]:
    for k in range(1, m+1):
        found = None
        for n in [2,3]:
            res = find_manipulation(n, m, k, 'PAV')
            if res:
                found = res
                break
        print(f"m={m}, k={k}: manipulable example found = {found is not None}")
