from stalker_colossus import StalkerColossus


async def log(message, iteration):
    if iteration % 22 == 0:
        print(message)


class BotStardust(StalkerColossus):
    async def on_step(self, iteration):
        await self.stalker_colossus()

