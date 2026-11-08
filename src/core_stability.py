import itertools, fractions
from itertools import combinations, combinations_with_replacement

def H(r):
    return sum(fractions.Fraction(1,i) for i in range(1,r+1))

def all_committees(m,k):
    return [frozenset(c) for c in combinations(range(m),k)]

def score_PAV(W,profile): return sum(H(len(A&W)) for A in profile)

def core_stable(profile, W, n, k, m):
    """profile: tuple of frozensets. Returns True if W is core-stable."""
    N=list(range(n)); C=list(range(m))
    for s in range(1,n+1):
        limit = fractions.Fraction(s*k, n)
        maxT = int(limit)  # floor
        if maxT==0: continue
        for S in combinations(N,s):
            for tsize in range(1, maxT+1):
                for T in combinations(C, tsize):
                    Tset=frozenset(T)
                    if all(len(profile[i]&Tset) > len(profile[i]&W) for i in S):
                        return False
    return True

def exists_core_committee(profile,n,m,k):
    for W in all_committees(m,k):
        if core_stable(profile,W,n,k,m):
            return True, W
    return False, None

print("=== PART A: verifying the published PAV k=8 counterexample (Example 4.3) ===")
# c1..c10 -> indices 0..9
# v1: {0,1,2}, v2:{0,1,3}, v3=v4:{4,5,6,7,8,9}
profile = (frozenset({0,1,2}), frozenset({0,1,3}), frozenset({4,5,6,7,8,9}), frozenset({4,5,6,7,8,9}))
n,m,k = 4,10,8
W_claimed = frozenset({0,1,4,5,6,7,8,9})  # {c1,c2,c5,...,c10}
# check PAV-optimality among all size-8 committees
best=None; bestscore=None
for W in all_committees(m,k):
    sc = score_PAV(W,profile)
    if bestscore is None or sc>bestscore:
        bestscore=sc; best=[W]
    elif sc==bestscore:
        best.append(W)
print("Max PAV score:", bestscore, " number of tied global-PAV committees:", len(best))
print("Is claimed W among global PAV committees?", W_claimed in best)
print("PAV score of claimed W:", score_PAV(W_claimed,profile))

# check core-stability of claimed W
print("Is claimed W core-stable?", core_stable(profile, W_claimed, n,k,m))
T = frozenset({0,1,2,3})
S = (0,1)
print(f"Check blocking: S={S}, T={sorted(T)}")
print("  |T| <= (|S|/n)k ?", len(T), "<=", fractions.Fraction(len(S)*k,n))
for i in S:
    print(f"  voter{i}: |Ai∩T|={len(profile[i]&T)}  |Ai∩W|={len(profile[i]&W_claimed)}")

print("\n=== PART B: our own exhaustive small-scale search for core existence ===")
import time
def all_ballots(m):
    return [frozenset(c) for r in range(0,m+1) for c in combinations(range(m),r)]

def exhaustive_check(n,m,k,verbose=True):
    ballots = all_ballots(m)
    t0=time.time()
    count_profiles=0
    worst=None
    # iterate over multisets of ballots of size n (voters are symmetric, so multiset suffices)
    for combo in combinations_with_replacement(ballots, n):
        count_profiles+=1
        ok, W = exists_core_committee(combo, n, m, k)
        if not ok:
            worst = combo
            break
    dt = time.time()-t0
    if verbose:
        status = "NO core-stable committee found!! <-- COUNTEREXAMPLE" if worst else "core-stable committee exists for ALL profiles"
        print(f"n={n} m={m} k={k}: checked {count_profiles} distinct profiles in {dt:.1f}s -> {status}")
    return worst

for m in [2,3,4]:
    for n in [2,3,4]:
        for k in range(1,m):
            w = exhaustive_check(n,m,k)
            if w:
                print("COUNTEREXAMPLE PROFILE:", [sorted(a) for a in w])

print("\n=== extending a bit further: m=5 ===")
for n in [2,3,4]:
    for k in range(1,5):
        w = exhaustive_check(n,5,k)
        if w:
            print("COUNTEREXAMPLE PROFILE:", [sorted(a) for a in w])
