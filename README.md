# monday-24-november-2026

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/azzilong/monday-24-november-2026/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/azzilong/monday-24-november-2026/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

Tuesday 24 November 2026 — The World in One Page. A dense newspaper front page that sums up the day's world news in a single image: 35 stories across 7 regions — Nvidia brings back Jensen Huang, allies warn of a nuclear weapon in space, and Iran defies the US blockade as tankers burn in Hormuz lead the page, with 10 pictured stories, a numbered world map, 22 more briefs, and a DATE CHECK box that says plainly what was left out and what was not yet confirmed when the image was drawn. Every illustration is original flat vector art drawn in code by `tools/render.py` (Python + Pillow); `main.ts` copies the finished `entry.png` to the output directory. See `SOURCES.md` for the full story list and the dating notes behind it.

## Run it

```sh
python3 tools/render.py entry.png
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

`main.ts` runs twice and writes the same bytes both times; `entry.png` is 1024×1024 and under 1 MiB.
