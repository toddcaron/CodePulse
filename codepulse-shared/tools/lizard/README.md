# Bundled Lizard Runtime

Run the pinned analyzer from this directory with an available Python 3.8 or later interpreter:

```text
python lizard.py --version
python lizard.py --csv -C 999 <source-root>
```

CodePulse consumes the CSV output for Cyclomatic Complexity only. It must exclude generated, minified, vendored, migration, build, cache, and separately reported test code before invoking the analyzer. It must ignore Lizard `*global*` pseudo-functions and retain the command, version, source scope, exclusions, and coverage gaps in the resulting assessment metrics.

Use the shared complexity model for the authoritative invocation and fallback rules.