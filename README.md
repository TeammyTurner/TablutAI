<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/TeammyTurner/TablutAI">
    <img src="res/tree.png" alt="Logo" width="130" height="130">
  </a>
  <h1 align="center">TablutAI</h1>

  <p align="center">
    Done the TeammyTurner's way.
  </p>
</p>

<!-- TABLE OF CONTENTS -->

## Table of Contents

- [Table of Contents](#table-of-contents)
- [About The Project](#about-the-project)
  - [How it works](#how-it-works)
- [Getting Started](#getting-started)
  - [Updates](#updates)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

<!-- ABOUT THE PROJECT -->

## About The Project

![Product Name Screen Shot][screenshot]

This is our entry for the **Tablut Competition**, hosted by the Artificial Intelligence MSc at the University of Bologna. We first started to fiddle around with RL and Gym, but it clearly wasn't the right path. Then, our research led us to try and reimplement something similar to [AlphaZero](https://it.wikipedia.org/wiki/AlphaZero), which is based on a Monte Carlo Tree Search aided by a Neural Network. Sadly, **our time management is awful**. In the end, we simply implemented a **Monte Carlo Tree Search** with no neural network, which should still perform kind of good.

### How it works

The project is actually composed of 3 repos:

- [tablutpy](https://github.com/TeammyTurner/tablutpy), our re-implementation of the Tablut game (Ashton rules) in python. This contains the `Board` object, which is the core of it all.
- [tablut-mcts](https://github.com/TeammyTurner/tablut-mcts), the module in charge of handling the Monte Carlo Tree Search, mainly through the `MCTS` class
- [tablutAI](#), this repo, which handles the interaction between our code and the [TablutCompetition server](https://github.com/AGalassi/TablutCompetition/)

<!-- GETTING STARTED -->

## Getting Started

You can just clone this repository, then install the requirements:

```
$ git clone https://github.com/TeammyTurner/TablutAI.git
```

```
$ cd TablutAI
```

```
$ pip3 install -r requirements.txt
```

This will install the two other modules too.

## Usage

To start the player, first start the server, then run

```
 $ python3 src/client.py -p white
```

The `-p` argument can either be `white` or `black`, and it contains the player that we'll impersonate.
There's other args you can change. The most important is `-t`: this states the timeout for a move. It defaults to 50 seconds, but if you decide to shorten the time this should be changed accordingly.
Then, `-d` states the tree's maximum depth, and `-C` changes the C factor for the MCTS. These should be left as default.

## License

Distributed under the GPL License. See `LICENSE` for more information.

<!-- CONTACT -->

## About us

This project was proudly made with ❤️ by TeammyTurner.

Project Link: [https://github.com/TeammyTurner/TablutAI](https://github.com/TeammyTurner/TablutAI)

[screenshot]: res/terminal.gif "Screenshot"
