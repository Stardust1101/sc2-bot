from sc2.data import Race, Difficulty


class DataName:
    race = {
        Race.Protoss: "PROTOSS",
        Race.Zerg: "ZERG",
        Race.Terran: "TERRAN",
        Race.Random: "RANDOM"
    }

    difficulty = {
        Difficulty.VeryHard: "Elite",
        Difficulty.CheatVision: "Cheat1",
        Difficulty.CheatMoney: "Cheat2",
        Difficulty.CheatInsane: "Cheat3"
    }
