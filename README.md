# homeautomation

```main``` execution outputs all the build objects as JSON.

1. JSON format changed a little to make validation actually work.
2. Three kinds of validation implemented that cover different things.
  2.1. Schema i.e. names and types and structure.
  2.2. Semantic i.e. uniqueness of names and calculated Control ids e.g. "S1_1", "R2_11"
  2.3. The build script will throw exceptions if connections are missing which the actions rely upon.

## Tests
```python -m unittest json_test.py```

### Note
- Human readable actions script output for bonus points.\
  Refer to ```configure.build(data, human_readable=False)```

## Pending
Web UI build output pending.
