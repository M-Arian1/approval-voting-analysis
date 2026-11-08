import itertools, fractions
from itertools import combinations

def H(r):
    return sum(fractions.Fraction(1,i) for i in range(1,r+1))

def all_committees(m,k):
    return [frozenset(c) for c in combinations(range(m),k)]

def score_AV_winner(profile, m, k):
    score=[0]*m
    for A in profile:
        for c in A: score[c]+=1
    order = sorted(range(m), key=lambda c:(-score[c], c))
    return frozenset(order[:k])

def winner_by_score(profile, m, k, scorefunc):
    best=None; bestscore=None
    for W in all_committees(m,k):
        sc = scorefunc(W, profile)
        Wt = tuple(sorted(W))
        if bestscore is None or sc>bestscore or (sc==bestscore and Wt<best[1]):
            bestscore=sc; best=(W,Wt)
    return best[0], bestscore

def score_PAV(W,profile): return sum(H(len(A&W)) for A in profile)
def score_CC(W,profile): return sum(1 if (A&W) else 0 for A in profile)

def check_JR(profile, W, n, k):
    # check all subsets S with |S|>=n/k and common approved candidate
    thresh = fractions.Fraction(n,k)
    N = list(range(n))
    for s in range(1, n+1):
        if s < thresh: continue
        for S in combinations(N, s):
            common = set(profile[S[0]])
            for i in S[1:]: common &= set(profile[i])
            if not common: continue
            if not any(profile[i] & W for i in S):
                return False, S, common
    return True, None, None

def check_PJR(profile, W, n, k):
    thresh_l = lambda l: fractions.Fraction(l*n,k)
    N=list(range(n))
    for l in range(1,k+1):
        for s in range(1,n+1):
            if s < thresh_l(l): continue
            for S in combinations(N,s):
                common=set(profile[S[0]])
                for i in S[1:]: common &= set(profile[i])
                if len(common) < l: continue
                union = set()
                for i in S: union |= set(profile[i])
                if len(union & W) < l:
                    return False,S,l
    return True,None,None

def check_EJR(profile, W, n, k):
    thresh_l = lambda l: fractions.Fraction(l*n,k)
    N=list(range(n))
    for l in range(1,k+1):
        for s in range(1,n+1):
            if s < thresh_l(l): continue
            for S in combinations(N,s):
                common=set(profile[S[0]])
                for i in S[1:]: common &= set(profile[i])
                if len(common) < l: continue
                if not any(len(profile[i]&W)>=l for i in S):
                    return False,S,l
    return True,None,None

if __name__=="__main__":
    # Example from doc's own intro: F_k^AV JR violation
    # n=10, k=3, majority(6) approves {0,1,2}, minority(4) approves {3,4,5}
    n=10;k=3;m=6
    profile = [frozenset({0,1,2})]*6 + [frozenset({3,4,5})]*4
    W = score_AV_winner(profile,m,k)
    print("F_k^AV winner:", sorted(W))
    ok,S,common = check_JR(profile,W,n,k)
    print("JR satisfied?", ok, "violating group size" , len(S) if S else None, "common cand" , common)

print("\n--- Searching for CC violating JR (small instances) ---")
import random
random.seed(0)
found=None
for m in range(3,6):
    for n in range(2,7):
        for k in range(1,m):
            # try some structured + random profiles
            trials = []
            # structured: try all profiles built from random small approval sets, a bunch of random trials
            for _ in range(4000):
                profile = [frozenset(random.sample(range(m), random.randint(1,m))) for _ in range(n)]
                trials.append(tuple(profile))
            for profile in set(trials):
                W,_ = winner_by_score(profile,m,k,score_CC)
                ok,S,common = check_JR(profile,W,n,k)
                if not ok:
                    found=(n,m,k,profile,W,S,common)
                    break
            if found: break
        if found: break
    if found: break
if found:
    n,m,k,profile,W,S,common = found
    print("CC JR-violation FOUND: n=%d m=%d k=%d"%(n,m,k))
    print("profile:", [sorted(a) for a in profile])
    print("winner W:", sorted(W))
    print("violating group S:", S, "common approved:", common)
else:
    print("No CC JR violation found in random search")

print("\n--- Searching for CC violating PJR (=> also violates EJR) ---")
random.seed(1)
found=None
for m in range(3,7):
    for n in range(2,9):
        for k in range(2,m):
            trials=set()
            for _ in range(3000):
                profile = tuple(frozenset(random.sample(range(m), random.randint(1,m))) for _ in range(n))
                trials.add(profile)
            for profile in trials:
                W,_ = winner_by_score(profile,m,k,score_CC)
                ok,S,l = check_PJR(profile,W,n,k)
                if not ok:
                    found=(n,m,k,profile,W,S,l)
                    break
            if found: break
        if found: break
    if found: break
if found:
    n,m,k,profile,W,S,l = found
    print("CC PJR-violation FOUND: n=%d m=%d k=%d, l=%d"%(n,m,k,l))
    print("profile:", [sorted(a) for a in profile])
    print("winner W:", sorted(W))
    print("violating group S:", S)
    ok,S2,l2 = check_EJR(profile,W,n,k)
    print("Also check EJR directly on same instance:", ok, S2, l2)
else:
    print("No CC PJR violation found in random search")

print("\n--- Verifying PAV always satisfies EJR (random search, should find NO violation) ---")
random.seed(2)
violation=None
for m in range(3,6):
    for n in range(2,7):
        for k in range(1,m):
            for _ in range(1500):
                profile = tuple(frozenset(random.sample(range(m), random.randint(1,m))) for _ in range(n))
                W,_ = winner_by_score(profile,m,k,score_PAV)
                ok,S,l = check_EJR(profile,W,n,k)
                if not ok:
                    violation=(n,m,k,profile,W,S,l)
                    break
            if violation: break
        if violation: break
    if violation: break
print("PAV EJR violation found?" , violation is not None, violation)

print("\n--- Finding a JR-but-not-PJR example (any rule/random committee) to show strictness ---")
random.seed(3)
found=None
for m in range(3,6):
    for n in range(2,7):
        for k in range(2,m):
            for _ in range(2000):
                profile = tuple(frozenset(random.sample(range(m), random.randint(1,m))) for _ in range(n))
                W = frozenset(random.sample(range(m),k))
                okjr,_,_ = check_JR(profile,W,n,k)
                okpjr,S,l = check_PJR(profile,W,n,k)
                if okjr and not okpjr:
                    found=(n,m,k,profile,W,S,l)
                    break
            if found: break
        if found: break
    if found: break
print("JR-not-PJR example:", found)

print("\n--- Finding a PJR-but-not-EJR example ---")
random.seed(4)
found2=None
for m in range(3,6):
    for n in range(2,8):
        for k in range(2,m):
            for _ in range(3000):
                profile = tuple(frozenset(random.sample(range(m), random.randint(1,m))) for _ in range(n))
                W = frozenset(random.sample(range(m),k))
                okpjr,_,_ = check_PJR(profile,W,n,k)
                okejr,S,l = check_EJR(profile,W,n,k)
                if okpjr and not okejr:
                    found2=(n,m,k,profile,W,S,l)
                    break
            if found2: break
        if found2: break
    if found2: break
print("PJR-not-EJR example:", found2)

def check_core(profile, W, n, k, m):
    N=list(range(n)); C=list(range(m))
    for s in range(1,n+1):
        for S in combinations(N,s):
            limit = fractions.Fraction(len(S)*k, n)
            maxT = int(limit)  # floor, since |T| integer <= limit
            for tsize in range(0, maxT+1):
                for T in combinations(C, tsize):
                    Tset=frozenset(T)
                    if all(len(profile[i]&Tset) > len(profile[i]&W) for i in S):
                        return False, S, Tset
    return True, None, None

print("\n--- Searching for an EJR-satisfying committee that is NOT in the Core ---")
random.seed(5)
found3=None
for m in range(3,5):
    for n in range(2,6):
        for k in range(2,m):
            for _ in range(600):
                profile = tuple(frozenset(random.sample(range(m), random.randint(1,m))) for _ in range(n))
                W,_ = winner_by_score(profile,m,k,score_PAV)  # PAV guarantees EJR, good candidate to test core-failure
                okejr,_,_ = check_EJR(profile,W,n,k)
                if not okejr: continue
                okcore,S,T = check_core(profile,W,n,k,m)
                if not okcore:
                    found3=(n,m,k,profile,W,S,T)
                    break
            if found3: break
        if found3: break
    if found3: break
print("EJR-but-not-core (via PAV) example:", found3)

print("\n--- Verifying the Q2-example (majority/minority) is NOT in the Core under F_k^AV ---")
n=10;k=3;m=6
profile = tuple([frozenset({0,1,2})]*6 + [frozenset({3,4,5})]*4)
W = score_AV_winner(profile,m,k)
print("W =", sorted(W))
okcore, S, T = check_core(profile, W, n, k, m)
print("In core?", okcore)
if not okcore:
    print("Blocking group S (voter indices):", S, " size=",len(S))
    print("Proposed alternative T:", sorted(T))
    limit = fractions.Fraction(len(S)*k,n)
    print("budget |S|/n * k =", limit, " |T| =", len(T))
    for i in S:
        print(f"  voter {i}: A_i={sorted(profile[i])}, |A_i∩T|={len(profile[i]&T)}, |A_i∩W|={len(profile[i]&W)}")

# also double check no single voter has a profitable unilateral deviation (Nash) at this profile, brute force
print("\nChecking Nash: any single voter has profitable deviation under F_k^AV at this profile?")
all_subsets = [frozenset(c) for r in range(m+1) for c in combinations(range(m),r)]
manip=False
for i in range(n):
    true_u = len(profile[i]&W)
    for Bi in all_subsets:
        if Bi==profile[i]: continue
        newp = list(profile); newp[i]=Bi
        W2 = score_AV_winner(tuple(newp),m,k)
        if len(profile[i]&W2) > true_u:
            manip=True
            print("  found manipulation for voter", i, Bi)
            break
    if manip: break
print("Any profitable unilateral deviation found?", manip)

print("\n--- Retrying EJR-but-not-core with arbitrary (non-rule) committees ---")
random.seed(7)
found4=None
for m in range(3,6):
    for n in range(2,7):
        for k in range(2,m):
            for _ in range(3000):
                profile = tuple(frozenset(random.sample(range(m), random.randint(1,m))) for _ in range(n))
                W = frozenset(random.sample(range(m),k))
                okejr,_,_ = check_EJR(profile,W,n,k)
                if not okejr: continue
                okcore,S,T = check_core(profile,W,n,k,m)
                if not okcore:
                    found4=(n,m,k,profile,W,S,T)
                    break
            if found4: break
        if found4: break
    if found4: break
print("EJR-but-not-core example:", found4)
