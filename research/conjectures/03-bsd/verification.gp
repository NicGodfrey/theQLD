\\ LEGION 03 — BSD numerical verification script (Pari/GP 2.15.4)
\\ Executed 2026-08-15 in this session. Outputs recorded in REPORT.md §3.9 and §5.
\\ Requires: pari-gp, pari-elldata (for Cremona labels in shacheck).

default(realprecision, 28);

\\ Leading-term BSD check: analytic rank, L^(r)(E,1)/r!, Omega*prod(c_p)/|tors|^2,
\\ regulator from a saturated Mordell-Weil basis, and the implied #Sha.
check(label, v) = {
  my(E = ellinit(v));
  my(gr = ellglobalred(E));
  my(ar = ellanalyticrank(E));
  my(r = ar[1], lead = ar[2]/r!);
  my(rk = ellrank(E));
  my(pts = rk[4], reg = 1.0);
  if(r > 0,
     my(sat = ellsaturation(E, pts, 100));   \\ saturation is essential: raw ellrank
     reg = matdet(ellheightmatrix(E, sat[1..r])));  \\ points can be non-saturated
  my(sha = lead / (ellbsd(E) * reg));
  printf("%s  N=%d  rank_an=%d  rank_alg in [%d,%d]\n", label, gr[1], r, rk[1], rk[2]);
  printf("   lead coeff L^(r)(1)/r! = %.12g\n", lead);
  printf("   Omega*prodc/tors^2     = %.12g   (tors=%d, prod c_p=%d)\n", ellbsd(E), elltors(E)[1], gr[3]);
  printf("   regulator              = %.12g\n", reg);
  printf("   implied #Sha           = %.12g\n\n", sha);
}

check("32a1  (y^2=x^3-x, congruent-number curve N=1)", [0,0,0,-1,0]);
check("37a1  (y^2+y=x^3-x, first rank-1 curve)",       [0,0,1,-1,0]);
check("389a1 (y^2+y=x^3+x^2-2x, first rank-2 curve)",  [0,1,1,-2,0]);
check("5077a1 (y^2+y=x^3-7x+6, first rank-3 curve)",   [0,0,1,-7,6]);

\\ Nontrivial Sha (rank 0, regulator = 1):
shacheck(label) = {
  my(E = ellinit(label));
  my(ar = ellanalyticrank(E));
  my(sha = (ar[2]/ar[1]!) / ellbsd(E));
  printf("%s: rank_an=%d, implied #Sha=%.12g\n", label, ar[1], sha);
}
shacheck("571a1");   \\ expect 4
shacheck("681b1");   \\ expect 9

\\ Live Heegner-point construction on the rank-1 curve 37a1:
E = ellinit([0,0,1,-1,0]);
P = ellheegner(E);
printf("Heegner point on 37a1: P = %s, canonical height = %.12g\n", Str(P), ellheight(E,P));
printf("L'(37a1,1) = %.12g\n", lfun(lfuncreate(E), 1, 1));

\\ Congruent-number family y^2 = x^3 - N^2 x:
cn(N) = {
  my(E = ellinit([0,0,0,-N^2,0]));
  my(ar = ellanalyticrank(E));
  my(r = ar[1], lead = ar[2]/r!);
  my(rk = ellrank(E), reg = 1.0);
  if(r > 0, my(sat = ellsaturation(E, rk[4], 100)); reg = matdet(ellheightmatrix(E, sat[1..r])));
  printf("y^2=x^3-%d^2x: rank_an=%d rank_alg in [%d,%d], sign=%d, implied #Sha=%.10g\n",
         N, r, rk[1], rk[2], ellrootno(E), lead/(ellbsd(E)*reg));
}
cn(1); cn(2); cn(3); cn(5); cn(6); cn(7); cn(34);

quit;
