import sys
from __init__ import run_ladder_game
from sc2.data import Race, Difficulty, AIBuild
from sc2.player import Bot, Computer, Human
import random

from sc2 import maps
from sc2.main import run_game
import time
from run_data import DataName

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
                "AcropolisLE",
                "DiscoBloodbathLE",
                "ThunderbirdLE",
                "TritonLE",
                "WintersGateLE",
                "WorldofSleepersLE",
                "2000AtmospheresAIE",
                "BerlingradAIE",
                "JagannathaLE",
                "KairosJunctionLE",
            ]
        )
        opponent_race = Race.Protoss
        difficulty = Difficulty.CheatMoney
        replay_name = "./replay/" + map_name + time.strftime("%m%d%H%M") + \
                      DataName.difficulty[difficulty] + ".SC2Replay"
        # map_name = "(2)16-BitLE"
        run_game(
            maps.get(map_name),
            [
                # Human(Race.Protoss),
                bot,
                Computer(opponent_race, difficulty),  # CheatInsane VeryHard
            ],
            realtime=False,
            save_replay_as=replay_name
        )
