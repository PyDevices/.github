# Roadmap

Where the org's shared release automation and community files are heading.
Bugs, and things you need that don't work yet, go to
[issues](https://github.com/PyDevices/.github/issues).

- **Real dependencies for MIP packages.** The index builder here folds a
  required package's files into the one that requires it. Recording real
  dependencies instead means one install brings what it needs, with no copies.
- **Type stubs for every published package.** The libraries keep types in
  docstrings because annotations cost memory on a microcontroller. The plan is
  to ship `.pyi` stubs so editors and type checkers on a desktop see real types.
