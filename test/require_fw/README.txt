Spexygen test: 'require-fw' rules (Spexygen 4.1.0)

Files:
  t.dox            test document; each UID brief states the expected outcome
  spex.json        two rules (rule 1: code operations need a test,
                   rule 2: requirements need code, depth 1)
  spex_bad.json    malformed rule (unknown key 'levels'): must stop with an error
  expected.log     reviewed output of: python ../../spexygen.py spex.json
  expected_bad.log reviewed output of: python ../../spexygen.py spex_bad.json
  expected/t.dox   reviewed generated document (spex/t.dox written by the run
                   with spex.json): forward and backward traces with briefs

Run in this directory and compare the console output with the expected logs,
and the generated spex\t.dox with expected\t.dox (ignore line endings):
  python ..\..\spexygen.py spex.json      (> compare with expected.log;
                                          spex\t.dox with expected\t.dox)
  python ..\..\spexygen.py spex_bad.json  (> compare with expected_bad.log, exit code 255)

Expected: rule 1: 15 UIDs checked, 9 reported; rule 2: 3 UIDs checked, 2 reported.
Cases covered: direct test; no forward trace; non-test child only; NOTEST
disposition; non-operation UIDs (no ')' / full match); doc UID (kind);
base operation tested through an override (level 2); override without a test;
test beyond the default depth 2; cycle without a test (terminates); test trace
in an inactive section; UID in an inactive section; no forward-trace
placeholder; inactive placeholder; test listed in a reference list only.
