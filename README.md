# GEDCOM linter

## Running the application locally

Running the application can be accomplished with the `run` shell script.

```bash
./run [args]
```

You must set your `PYTHON3PATH` environment variable to point to your `python3` 
instance before running this. Usually, you can get away with something like (for `zsh`):

```bash
echo "export PYTHON3PATH=$(which python3)" >> ~/.zshrc && source ~/.zshrc
```

Please note, this will modify your `.zshrc`.

## Running tests

Running the application can be accomplished with the `run-tests` shell script. It
takes no arguments. It will return `0` if successful and some other value if not.

```bash
./run-tests
```

You must set your `PYTHON3PATH` environment variable to point to your `python3` 
instance before running this. An example of how to do this is detailed above.
## Code structure

The `src/` folder contains the source code required to run the program. The command line 
`./run` will run the `__main__.py` in the top-level directory -- this is intentional, 
it will bootstrap the `src/` module.

Tests will be inside the `test/` module. More is to come on this later. The `samples/` folder contains 
sample GEDCOM files to be used by the tests.