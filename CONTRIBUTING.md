# Contributing

Start with `docs/methods.md` and the tests. Add a regression test before changing
numerical behavior. Run the full suite and a small experiment; avoid copying
assessment code, private datasets or credentials into changes.

Changes to algorithm/evidence source require new experiment directories and new
measurements. Do not edit saved metrics or replace plots by hand. Regenerate from
verified records, retain weak outcomes, and distinguish reference agreement from
real-world quality. For comparative claims use identical inputs and controlled
initialization/work limits, record all seeds and disclose timing scope.

The verifier detects inconsistent records; it is not an authenticity signature or
a safe parser for untrusted arbitrary huge JSON. Use known project-generated records.
Publication requires exact-commit Linux checks, a source/privacy review and a
reviewed release. No privileged runners, secrets, paid services or GPU quota are
required. Do not add a badge asserting checks that have not run.
