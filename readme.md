## stages

- run with `python main.py`
- build with `pyinstaller main.py`
- test with `python tests.py`

## stages
- fetches list of houses
- fetches reference data in constructor of RefDics, puts everything in dictionaries (may be written to file)
- generate example data*
- prompt user for settings
- map list of house to data package

## Example data
1. data-house-all-items
This is the data that gets retrieved per house
2. data-house-all-details
This shows all the extra pieces of information that can be retrieved for a house
3. data-house-all-distilled
This will contain the detail sections that will be used to compile a house for the data package
4. data-house-all-compiled
This is the data per house that will end up in the package

## Specific Unit testing

To run a test class, run `python -m unittest my_test.py`.
Alternatively, if you define the following at the end of your test file:

```
if __name__ == '__main__':
  unittest.main()
```

You can simply run `python my_test.py` for the same result.

In order to run multiple tests at once, you can use `python -m unittest discover` and it will run all tests in files prepended with `test_`