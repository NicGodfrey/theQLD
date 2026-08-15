\\ WAVE-2 LEGION 03 — BSD breakthrough verification script (Pari/GP 2.15.4)
\\ Run as:  gp -q -s 2000000000 breakthrough.gp
\\ Requires pari-elldata (Cremona database) for Part 4.
\\
\\ Companion to BREAKTHROUGH.md. Verifies, at scale, the two theorems proved there
\\ for the family  E_p : y^2 = x^3 - p^2 x,  p prime, p = 3 (mod 8):
\\   Theorem A:  Sel_2(E_p) = (Z/2)^2, hence rank E_p(Q) = 0 and Sha(E_p)[2] = 0.
\\   Theorem B:  the Tunnell number a_p = 2 (mod 4); hence L(E_p,1) >= beta/sqrt(p) > 0.
\\ and extends the Wave-1 BSD leading-term verification to every Cremona curve
\\ of conductor <= 500.

default(realprecision, 28);
totaltime = 0;

beta = intnum(x=1, [oo,-3/2], 1/sqrt(x^3-x));
print("beta = Int_1^oo dx/sqrt(x^3-x) = ", beta);
print("");

\\ =====================================================================
\\ PART 1 — Tunnell-number scan: a_p = 2 (mod 4) for ALL p = 3 (mod 8) up to 10^6.
\\ a_n := #{n=2x^2+y^2+32z^2} - (1/2)#{n=2x^2+y^2+8z^2}; qfrep counts up to sign.
\\ Also verifies the representation lemma  #{(x,y): 2x^2+y^2 = p} = 4.
\\ =====================================================================
X = 10^6;
gettime();
vB  = qfrep([2,0,0; 0,1,0; 0,0,8],  X);
vA  = qfrep([2,0,0; 0,1,0; 0,0,32], X);
vb2 = qfrep([2,0; 0,1], X);
t1 = gettime(); totaltime += t1;
print("PART 1: Tunnell scan to X = ", X, "   (qfrep: ", t1, " ms)");
{
  my(bad=0, badB0=0, cnt=0, dist=Map(), firsts=Map());
  forprime(p = 3, X,
    if(p % 8 == 3,
      cnt++;
      my(a = 2*vA[p] - vB[p]);
      if(a % 4 != 2, bad++; print("  VIOLATION p=", p, " a_p=", a));
      if(2*vb2[p] != 4, badB0++; print("  B0 VIOLATION p=", p));
      my(s = (a/2)^2);
      if(!mapisdefined(dist, s), mapput(dist, s, 0); mapput(firsts, s, p));
      mapput(dist, s, mapget(dist, s) + 1)));
  my(t = gettime()); totaltime += t;
  print("  primes p = 3 (mod 8), p <= 10^6 : ", cnt);
  print("  violations of  a_p = 2 (mod 4)  : ", bad);
  print("  violations of  #{2x^2+y^2=p}=4  : ", badB0);
  print("  BSD-predicted #Sha = (a_p/2)^2, first occurrences:");
  my(ks = vecsort(Vec(Mat(dist)[,1])));
  for(i = 1, min(#ks, 8),
    print("    #Sha = ", ks[i], "  count ", mapget(dist, ks[i]),
          "  first p = ", mapget(firsts, ks[i])));
  print("  (scan: ", t, " ms)");
}
print("");

\\ =====================================================================
\\ PART 2 — Machine 2-descent certificates (cross-check of Theorem A):
\\ ellrank = 2-descent + Cassels pairing; [0,0,0,[]] certifies rank exactly 0.
\\ =====================================================================
{
  my(cnt=0, bad=0);
  gettime();
  forprime(p = 3, 10^4,
    if(p % 8 == 3,
      cnt++;
      my(v = ellrank(ellinit([0,0,0,-p^2,0])));
      if(v != [0,0,0,[]], bad++; print("  UNEXPECTED ellrank at p=", p, ": ", v))));
  my(t = gettime()); totaltime += t;
  print("PART 2: ellrank(E_p) = [0,0,0,[]] (rank exactly 0) for all ", cnt,
        " primes p = 3 (mod 8), p <= 10^4;  failures: ", bad, "   (", t, " ms)");
}
print("");

\\ =====================================================================
\\ PART 3 — Full leading-term verification for the family, including the
\\ exact Tunnell identity  L(E_p,1) = beta*a_p^2/(4*sqrt(p))  and
\\ implied #Sha = (a_p/2)^2.  Local data: c_2 = 2 (III), c_p = 4 (I0*),
\\ Omega = 2*beta/sqrt(p), torsion (Z/2)^2  ==>  L/Omega = a_p^2/8 exactly.
\\ =====================================================================
{
  my(plist = [3,11,19,43,59,67,83,107,131,139,163,179,211,227,251,283,307,467,907]);
  my(worstL = 0., worstSha = 0., worstOm = 0.);
  gettime();
  print("PART 3: family table (E_p : y^2 = x^3 - p^2 x)");
  print("    p    a_p   L(E_p,1)        beta*a_p^2/(4 sqrt p)   implied #Sha   (a_p/2)^2  c_2  c_p  kod_2 kod_p");
  for(i = 1, #plist,
    my(p = plist[i]);
    my(a = 2*vA[p] - vB[p]);
    my(E = ellinit([0,0,0,-p^2,0]));
    my(L = lfun(lfuncreate(E), 1));
    my(T = beta*a^2/(4*sqrt(p)));
    my(sha = L/ellbsd(E));
    my(l2 = elllocalred(E,2), lp = elllocalred(E,p));
    \\ omega[1] = least real period = beta/sqrt(p); BSD period = 2*omega[1] = 2*beta/sqrt(p)
    \\ (E_p(R) has two components).  Check omega[1]*sqrt(p)/beta = 1:
    my(om = E.omega[1]*sqrt(p)/beta);
    worstL   = max(worstL,   abs(L - T));
    worstSha = max(worstSha, abs(sha - (a/2)^2));
    worstOm  = max(worstOm,  abs(om - 1));
    printf("  %5d  %4d   %.12g   %.12g    %.12g   %4d      %d    %d    %d    %d\n",
           p, a, L, T, sha, (a/2)^2, l2[4], lp[4], l2[2], lp[2]));
  my(t = gettime()); totaltime += t;
  print("  max |L - Tunnell|             = ", worstL);
  print("  max |impliedSha - (a_p/2)^2|  = ", worstSha);
  print("  max |omega1*sqrt(p)/beta - 1| = ", worstOm);
  print("  (kod codes: 3 = III at 2;  -1 = I0* at p)      (", t, " ms)");
}
print("");

\\ =====================================================================
\\ PART 4 — Extended Cremona sweep: strong-BSD leading term for EVERY curve
\\ of conductor <= 500 in the Cremona database (Wave 1 did 6 curves).
\\ implied #Sha := (L^(r)(1)/r!) / (Omega*prod(c)/tors^2 * Reg), saturated basis.
\\ =====================================================================
{
  my(n=0, worst=0., nonsq=0, obstructed=List(), rankmismatch=0, shabig=List());
  gettime();
  forell(ell, 11, 500,
    my(E = ellinit(ell[1]));
    my(ar = ellanalyticrank(E));
    my(r = ar[1], lead = ar[2]/r!);
    my(rk = ellrank(E));
    my(reg = 1.0);
    if(r > 0,
      my(sat = ellsaturation(E, rk[4], 100));
      reg = matdet(ellheightmatrix(E, sat[1..r])));
    my(sha = lead/(ellbsd(E)*reg));
    my(shaZ = round(sha));
    worst = max(worst, abs(sha - shaZ));
    if(!issquare(shaZ), nonsq++; print("  NON-SQUARE Sha at ", ell[1], ": ", sha));
    if(rk[1] != rk[2], listput(obstructed, ell[1]));  \\ 2-descent+Cassels cannot close (Sha[4] != 0)
    if(!(rk[1] <= r && r <= rk[2]), rankmismatch++;
       print("  RANK MISMATCH at ", ell[1], ": an=", r, " alg in ", [rk[1],rk[2]]));
    if(shaZ > 1, listput(shabig, [ell[1], r, shaZ]));
    n++);
  my(t = gettime()); totaltime += t;
  print("PART 4: Cremona sweep, all curves 11 <= N <= 500      (", t, " ms)");
  print("  curves checked                    : ", n);
  print("  worst |impliedSha - integer|      : ", worst);
  print("  non-square rounded Sha            : ", nonsq);
  print("  analytic rank outside descent box : ", rankmismatch);
  print("  curves where 2-descent + Cassels pairing cannot close the rank: ", #obstructed, "  ", Vec(obstructed));
  print("  curves with implied #Sha > 1      : ", #shabig);
  for(i = 1, #shabig, print("    ", shabig[i][1], "  rank_an=", shabig[i][2], "  #Sha_an=", shabig[i][3]));
}
print("");
print("TOTAL computation time: ", totaltime, " ms");
quit;
