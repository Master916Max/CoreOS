# Tutorial on how to begin Debugging the OS

## Starting

Start the Boot as Normal but with the Debug Flag Set.
```sh
uv run boot.py (Other Set Flags) --debug
```

After the Kernel Has started you can simply start the Debugger Client in another Terminal Window

```sh
uv run debuger.py
```

Now Once Connected it should look somthing like this:
```python
|-DB-Kernel>
```

