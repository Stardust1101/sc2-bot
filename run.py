import sc2, sys
from __init__ import run_ladder_game
from sc2.bot_ai import BotAI
from sc2.data import Race, Difficulty, AIBuild
from sc2.player import Bot, Computer, Human
import random

from sc2 import maps
from sc2.main import run_game
import time

# Load bot
from bot_main import BotStardust
bot = Bot(Race.Protoss, BotStardust())

# Start game
if __name__ == "__main__":

    if "--LadderServer" in sys.argv:
        # Ladder game started by LadderManager
        print("Starting ladder game...")
        result, opponentid = run_ladder_game(bot)
        print(f"{result} against opponent {opponentid}")
    else:
        # Local game
        print("Starting local game...")
        map_name = random.choice(
            [
                'AcropolisLE',
                'DiscoBloodbathLE',
                'EphemeronLE',
                'ThunderbirdLE',
                'TritonLE',
                'WintersGateLE',
                'WorldofSleepersLE'
            ]
        )
        opponent_race = Race.Protoss
        difficulty = Difficulty.VeryHard
        # map_name = "(2)16-BitLE"
        run_game(
            maps.get(map_name),
            [
                # Human(Race.Protoss),
                bot,
                Computer(opponent_race, difficulty),  # CheatInsane VeryHard
            ],
            realtime=False,
            #save_replay_as="./replay/" + map_name + time.strftime("%m%d%H%M%S") + ".SC2Replay"
        )
