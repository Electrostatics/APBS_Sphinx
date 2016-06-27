# A Few Notes
Running `make` will generate both the standalone geoflow program (called `osm` for some reason that I never understood) as well as a `test` program.

## A Possible Hint
I just finished reviewing the changes that were made to some of the code.  I ran across this in `pbsolvercz.cpp` and it sparked a memory:

```C
	// phi_flat = solver.solveWithGuess(bgf.baseInterface(), phi_flat);
	phi_flat = solver.solve(bgf.baseInterface());
```

I think that the solver that Andrew used here is different from what they were using in the Fortran implementation.  I believe that I was in the middle of trying to use something more similar to what I found in the Fortran code.

I've also added a comment to the source file itself.

## Unit Tests
You'll need to have installed [Google Mock](https://code.google.com/p/googlemock/) for this to work.

It's been a while since I worked on this, and as you can see below, some of the tests are failing.  I suspect it's more of an error in the tests, than something wrong with the geoflow code.

Below are the results when I committed these changes.

```
[==========] Running 6 tests from 2 test cases.
[----------] Global test environment set-up.
[----------] 3 tests from ChargeDist
[ RUN      ] ChargeDist.Test_charget_WhateverThatIs
[       OK ] ChargeDist.Test_charget_WhateverThatIs (0 ms)
[ RUN      ] ChargeDist.Test_corlocqt_WhateverThatIs
[       OK ] ChargeDist.Test_corlocqt_WhateverThatIs (0 ms)
[ RUN      ] ChargeDist.Test_loc_qt_WhateverThatIs
[       OK ] ChargeDist.Test_loc_qt_WhateverThatIs (0 ms)
[----------] 3 tests from ChargeDist (0 ms total)

[----------] 3 tests from DomainIni
[ RUN      ] DomainIni.TestDimensions
surfconcz_test.cpp:89: Failure
Value of: comdata.nx
  Actual: 7
Expected: 55
surfconcz_test.cpp:90: Failure
Value of: comdata.ny
  Actual: 7
Expected: 53
surfconcz_test.cpp:91: Failure
Value of: comdata.nz
  Actual: 6
Expected: 48
[  FAILED  ] DomainIni.TestDimensions (0 ms)
[ RUN      ] DomainIni.TestLeftandRight
surfconcz_test.cpp:95: Failure
Value of: comdata.xleft
  Actual: -6.9
Expected: -5.9
surfconcz_test.cpp:96: Failure
Value of: comdata.xright
  Actual: 8.1
Expected: 7.6
surfconcz_test.cpp:98: Failure
Value of: comdata.yleft
  Actual: -6.9
Expected: -5.9
surfconcz_test.cpp:99: Failure
Value of: comdata.yright
  Actual: 8.1
Expected: 7.1
surfconcz_test.cpp:101: Failure
Value of: comdata.zleft
  Actual: -6.9
Expected: -5.9
surfconcz_test.cpp:102: Failure
Value of: comdata.zright
  Actual: 5.6
Expected: 5.85
[  FAILED  ] DomainIni.TestLeftandRight (0 ms)
[ RUN      ] DomainIni.TestDcel
surfconcz_test.cpp:106: Failure
Value of: comdata.dcel
  Actual: 0
Expected: 0.25
[  FAILED  ] DomainIni.TestDcel (0 ms)
[----------] 3 tests from DomainIni (0 ms total)

[----------] Global test environment tear-down
[==========] 6 tests from 2 test cases ran. (1 ms total)
[  PASSED  ] 3 tests.
[  FAILED  ] 3 tests, listed below:
[  FAILED  ] DomainIni.TestDimensions
[  FAILED  ] DomainIni.TestLeftandRight
[  FAILED  ] DomainIni.TestDcel

 3 FAILED TESTS
```
