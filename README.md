# DFIR Cheatsheet

Data for the app [https://harder.vercel.app/](https://harder.vercel.app/).

## Overview

- There are two categories current: Red, blue
- Keep entries slim, this is not a wiki!
- You can link between entries with the `slug` key.

## How to add an entry

- Copy `template-blue.yaml` or `template-red.yaml` into the `blue` respectively `red` folder.
- Rename the newly created file, the filename is also the `slug` value.
- Fill out information.
- Run `python gen.py`
- Check if there are any errors
- Create a pull request
