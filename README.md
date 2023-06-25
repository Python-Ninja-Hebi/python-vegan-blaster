# pygame-vegan-blaster - simple blaster game with python and pygame

I made a simple game with python and pygame  
inspired by the classic Blasterman from Hudson-Soft.

Thanks Kenney https://kenney.nl for the assets

<img src="img/VeganBlaster.gif" width="320" align="left"><br><br><br><br><br><br><br><br><br><br><br><br><br><br>

## From pygame to the browser

You can convert a python pygame into an webassembly and play it in the browser.

Install pygbag https://github.com/pygame-web/pygbag


```Rust
pip install pygbag
```

You have to rename your game to main.py and make its loop async aware.


```Rust
import math
import random

from wonderzero import *

..

async def main():
    game = Game(width=WIDTH, height=HEIGHT, name='Vegan Blaster')
    game.background_color = GRAY
    await game.run_async()
    game.quit()

asyncio.run(main())
```

Compile to webassembly


```Rust
pygbag ./folder
```

You can play it.
Chrome should work. Use keyboard.

soon on itch.io


```Rust

```
