# Contributing

Thanks for helping the Fellowship. Bug reports, fixes, new art and Linux or Windows testing are all welcome.

## Reporting a bug

Open an issue with the bug template. Include your Herdr version (`herdr-app --version`), your system and a screenshot. Linux and Windows haven't been tested yet, so reports from them help the most.

## Making a change

1. Fork the repo and create a branch.
2. Make your change. Where things live:
   - `layouts/middle-earth.json`: the window layout.
   - `themes/`: the Shire (light) and Mordor (dark) colors.
   - `mods/`: the code. `fellowship` is the agents list, `fellowship-toast` the notifications, `fellowship-status` the status bar and `realms` the spaces list.
   - `tools/sprites.py`: every sprite and emblem, as grids (24x24 agents, 16x16 emblems).
3. To change art, edit the grids in `tools/sprites.py`, never the SVG or PNG files. Then regenerate:

   ```sh
   python3 tools/sprites.py
   python3 tools/banners.py   # needs Pillow
   python3 tools/header.py    # only if the base sprites changed
   ```

4. Install your copy and check it. On macOS and Linux, `./install.sh` copies it into your Herdr home and runs `herdr-app check` on each mod. Your previous files go to `backups/middle-earth-<time>/`.
5. Try it in Herdr: start an agent and watch it work, wait, finish and need you, in both light and dark mode.
6. If you changed how the layout looks or behaves, update `RECIPE.md` too. The Herdr gallery and other people's agents build from it.
7. Open a pull request and fill in the checklist.

## Style

- Match the code around your change. The mods started as clones of Herdr's own `agents`, `toast`, `workspace-status` and `spaces`.
- Name constants instead of writing magic numbers, and comment why, not what.
- Don't swallow errors: log them with `console.error`.
