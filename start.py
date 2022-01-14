import sc2
from sc2 import *
from sc2.constants import UnitTypeId,AbilityId,BuffId

from bot_api import bot_api

class start(bot_api):
    async def two_base(self):
        if self.structures(UnitTypeId.NEXUS).exists:

            pylon_position = self.structures(UnitTypeId.NEXUS).first.position.towards(self.game_info.map_center,9.2)

            if self.supply_workers < 14:
                await self.train_(UnitTypeId.PROBE,UnitTypeId.NEXUS)
            elif self.supply_workers == 14 and await self.count(UnitTypeId.PYLON) < 1:
                await self.build_(UnitTypeId.PYLON,pylon_position)
            elif self.supply_workers < 16:
                await self.train_(UnitTypeId.PROBE,UnitTypeId.NEXUS)
            if self.structures(UnitTypeId.PYLON).ready.exists:
                nexus = self.structures(UnitTypeId.NEXUS).ready.first
                if not nexus.is_idle:
                    self.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus))
            if self.structures(UnitTypeId.GATEWAY).exists:
                if self.supply_workers < 19:
                    await self.train_(UnitTypeId.PROBE, UnitTypeId.NEXUS)
                elif self.supply_workers == 19:
                    if self.can_afford(UnitTypeId.NEXUS):
                        await self.expand_now()
                    if self.structures(UnitTypeId.PYLON).ready.exists and self.structures(UnitTypeId.NEXUS).amount > 1:
                        if not self.structures(UnitTypeId.CYBERNETICSCORE) and not self.already_pending(UnitTypeId.CYBERNETICSCORE):
                            pylon = self.structures(UnitTypeId.PYLON).ready.random
                            await self.build_(UnitTypeId.CYBERNETICSCORE, pylon)
            if self.structures(UnitTypeId.CYBERNETICSCORE).exists:
                if self.supply_workers < 20:
                    await self.train_(UnitTypeId.PROBE, UnitTypeId.NEXUS)
                elif self.supply_workers == 20 and await self.count(UnitTypeId.ASSIMILATOR) < 2:
                    await self.build_assimilator_()
                elif self.supply_workers < 21:
                    await self.train_(UnitTypeId.PROBE, UnitTypeId.NEXUS)
                elif self.supply_workers == 21 and await self.count(UnitTypeId.PYLON) < 2:
                    await self.build_(UnitTypeId.PYLON, pylon_position)
                elif await self.count(UnitTypeId.PYLON) == 2:
                    await self.train_(UnitTypeId.PROBE, UnitTypeId.NEXUS)

            if self.structures(UnitTypeId.PYLON).ready.exists:
                if not self.structures(UnitTypeId.GATEWAY).exists and not self.already_pending(UnitTypeId.GATEWAY):
                    pylon = self.structures(UnitTypeId.PYLON).ready.random
                    await self.build_(UnitTypeId.GATEWAY, pylon)
            if self.structures(UnitTypeId.GATEWAY).exists and await self.count(UnitTypeId.ASSIMILATOR) < 1:
                await self.build_assimilator_()

    async def one_base_four_gateway_start(self):

        pylon_position = self.structures(UnitTypeId.NEXUS).first.position.towards(self.game_info.map_center, 9.2)

        if self.supply_workers < 14:
            await self.train_(UnitTypeId.PROBE, UnitTypeId.NEXUS)
        elif self.supply_workers == 14 and await self.count(UnitTypeId.PYLON) < 1:
            await self.build_(UnitTypeId.PYLON, pylon_position)
        elif self.supply_workers < 23:
            await self.train_(UnitTypeId.PROBE,UnitTypeId.NEXUS)
        if self.supply_workers > 20 and await self.count(UnitTypeId.PYLON) < 2:
            await self.build_(UnitTypeId.PYLON, pylon_position)

        if self.structures(UnitTypeId.PYLON).ready.exists:
            pylon = self.structures(UnitTypeId.PYLON).ready.filter \
                (lambda pylon: pylon.distance_to(self.start_location) < 0.5 * map_length).random
            if await self.count(UnitTypeId.GATEWAY) < 2:
                await self.build_(UnitTypeId.GATEWAY, pylon)
        if self.structures(UnitTypeId.GATEWAY).exists and await self.count(UnitTypeId.ASSIMILATOR) < 2:
            await self.build_assimilator_()
        if self.structures(UnitTypeId.GATEWAY).ready.exists and await self.count(UnitTypeId.CYBERNETICSCORE) < 1:
            await self.build_(UnitTypeId.CYBERNETICSCORE,pylon)

    async def one_base_four_gateway_mid(self):  # After having a cyberneticscore
        # Require invisible detecting

        global map_length
        global warp
        map_length = self.start_location.position.distance_to(self.enemy_start_locations[0].position)
        warp = False

        if await self.count_(UnitTypeId.PROBE) < 23:
            await self.one_base_four_gateway_start()
        await self.distribute_workers()
        await self.CONTROLL_ATTACK_4bg()
        await self.scout_4bg()
        await self.operation_cyberneticscore_4bg()
        await self.train_stalker_4bg()
        # await self.train_zealot_4bg()

        await self.operation_stalker_4bg()
        # await self.operation_zealot_4bg()
        await self.build_pylon_4bg()

    async def scout_4bg(self):
        # initiating
        global arrived
        global scout
        if self.time < 1:
            scout = None
        if scout == None:
            arrived = False

        pylon_position_out = self.game_info.map_center.towards(self.enemy_start_locations[0], 0.15 * map_length)

        if await self.count(UnitTypeId.GATEWAY) > 1:  # Assign a scout worker
            scout = self.units(UnitTypeId.PROBE).ready.closest_to(self.enemy_start_locations[0])
            if arrived == False or scout.is_idle:
                self.do(scout.move(pylon_position_out))
            if await self.count_(UnitTypeId.STALKER) > 3 and await self.count(UnitTypeId.PYLON) < 4:
                if self.can_afford(UnitTypeId.PYLON):
                    await self.build(UnitTypeId.PYLON,near=pylon_position_out,build_worker=scout)
            elif await self.count_(UnitTypeId.STALKER) > 3 and self.structures(UnitTypeId.PYLON).ready.amount > 3 and await self.count(UnitTypeId.GATEWAY) < 4:
                if self.can_afford(UnitTypeId.GATEWAY):
                    await self.build(UnitTypeId.GATEWAY,near=pylon_position_out,build_worker=scout)

        if self.units(UnitTypeId.PROBE).ready.closer_than(2, pylon_position_out).exists:
            arrived = True

    async def operation_stalker_4bg(self):

        for stalker in self.units(UnitTypeId.STALKER):
            enemy_in_range = await self.enemy_in_range(self.enemy_units, stalker)
            await self.attack_control_a(stalker, attack)
            if await self.has_ability(AbilityId.EFFECT_BLINK_STALKER, stalker):
                if stalker.shield_percentage <= 0.4 and len(enemy_in_range) != 0:
                    self.do(stalker(AbilityId.EFFECT_BLINK_STALKER, self.enemy_units.closest_to(stalker.position).position.towards(
                    stalker.position,14
                )))

    async def operation_zealot_4bg(self):
        for zealot in self.units(UnitTypeId.ZEALOT):
            await self.attack_control_a(zealot, attack)

    async def operation_cyberneticscore_4bg(self):
        global warp
        for cyberneticscore in self.structures(UnitTypeId.CYBERNETICSCORE).ready.idle:
            if self.can_afford(AbilityId.RESEARCH_WARPGATE) and \
                    await self.has_ability(AbilityId.RESEARCH_WARPGATE, cyberneticscore):
                self.do(cyberneticscore(AbilityId.RESEARCH_WARPGATE))
            elif not await self.has_ability(AbilityId.RESEARCH_WARPGATE, cyberneticscore):
                warp = True

        if self.structures(UnitTypeId.CYBERNETICSCORE).ready.exists:
            for cyberneticscore in self.structures(UnitTypeId.CYBERNETICSCORE).ready.idle:
                if self.can_afford(AbilityId.RESEARCH_WARPGATE) and \
                        await self.has_ability(AbilityId.RESEARCH_WARPGATE,cyberneticscore):
                    self.do(cyberneticscore(AbilityId.RESEARCH_WARPGATE))

    async def train_stalker_4bg(self):  # 4 BG Stalker

        pylon_position_out = self.game_info.map_center.towards(self.enemy_start_locations[0], 0.15 * map_length)

        if self.structures(UnitTypeId.CYBERNETICSCORE).ready.exists:
            if warp == False:
                if await self.count_(UnitTypeId.STALKER) < 4:
                    await self.train_(UnitTypeId.STALKER,UnitTypeId.GATEWAY)
                elif await self.count_(UnitTypeId.STALKER) < 6 and await self.count(UnitTypeId.GATEWAY) > 3:
                    await self.train_(UnitTypeId.STALKER,UnitTypeId.GATEWAY)
            else:
                    await self.warp_in(UnitTypeId.STALKER, pylon_position_out)

    async def train_zealot_4bg(self):  # 4 BG Stalker

        pylon_position_out = self.game_info.map_center.towards(self.enemy_start_locations[0], 0.15 * map_length)

        if self.structures(UnitTypeId.CYBERNETICSCORE).ready.exists:
            if warp:
                if await self.count_(UnitTypeId.ZEALOT) < int(await self.count_(UnitTypeId.STALKER) * 0.2):
                    await self.warp_in(UnitTypeId.ZEALOT, pylon_position_out)

    async def build_pylon_4bg(self):
        pylon_position = self.structures(UnitTypeId.NEXUS).first.position.towards(self.game_info.map_center, 9.2)
        potential_supply = self.already_pending(UnitTypeId.PYLON)*8

        if self.supply_used > 28 and await self.count(UnitTypeId.PYLON) < 3:
            await self.build_(UnitTypeId.PYLON, pylon_position)
        elif await self.count(UnitTypeId.PYLON) > 3:
            supply_consume = (self.structures(UnitTypeId.GATEWAY).amount+self.structures(UnitTypeId.WARPGATE).amount)*2 +\
                             self.structures(UnitTypeId.ROBOTICSBAY).amount*6
            if self.supply_left+potential_supply < supply_consume:
                await self.build_(UnitTypeId.PYLON, pylon_position)

    async def CONTROLL_ATTACK_4bg(self):  # 4 BG
        global attack
        global attack_history
        if self.supply_workers < 24:
            attack_history = True
            attack = False
        if attack_history == True:
            if await self.count_(UnitTypeId.STALKER) > 10:
                attack = True
















