import sc2
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.buff_id import BuffId

from sc2.position import Point2
from sc2.player import Bot, Computer

from sc2.bot_ai import BotAI
from sc2.data import Race
import random

from bot_api import BotApi


class StalkerColossus(BotApi):
    warp = False
    attack_troop = []
    defend_troop = []
    dead_troop = []
    army_length = 0

    async def stalker_colossus(self):
        await self.economy()
        await self.troop()
        await self.tech()

    async def economy(self):
        await self.CONTROL_PANIC()

        await self.build_nexus()

        await self.build_pylon()
        await self.build_gateway()
        await self.build_assimilator()
        await self.build_cyberneticscore()

        await self.operation_nexus()

    async def tech(self):
        await self.operation_cyberneticscore()

        await self.build_twilightcouncil()
        await self.operation_twilightcouncil()

        await self.build_roboticsfacility()
        await self.build_roboticsbay()
        await self.build_templararchive()

        await self.operation_roboticsbay()

        await self.build_forge()
        await self.operation_forge()

    async def troop(self):
        await self.train_stalker()
        await self.train_zealot()
        await self.train_colossus()
        await self.train_observer()

        await self.train_sentry()
        await self.train_immortal()

        await self.train_hightemplar()

        await self.operation_sentry()
        await self.operation_stalker()
        await self.operation_general_troop(UnitTypeId.ZEALOT, distance=0)
        await self.operation_general_troop(UnitTypeId.IMMORTAL)
        await self.operation_general_troop(UnitTypeId.COLOSSUS)
        await self.operation_hightemplar()
        await self.operation_general_troop(UnitTypeId.ARCHON)
        await self.operation_observer()

        await self.CONTROL_ATTACK()
        await self.random_scout()

    async def train_probe(self):
        if self.supply_workers < min(self.townhalls.ready.amount * 22, 66):
            await self.train_(UnitTypeId.NEXUS, UnitTypeId.PROBE)

    async def build_pylon(self):
        if not self.townhalls.ready.exists:
            return
        position = self.townhalls.first.position.towards(self.game_info.map_center, 9.2)
        potential_supply = self.already_pending(UnitTypeId.PYLON) * 8

        supply_consume = self.structures(UnitTypeId.GATEWAY).amount * 2 + \
                         self.structures(UnitTypeId.WARPGATE).amount * 2 + \
                         self.structures(UnitTypeId.ROBOTICSBAY).amount * 6 + \
                         self.townhalls.amount
        if self.supply_left + potential_supply <= min(supply_consume, 200 - self.supply_used):
            await self.build_(UnitTypeId.PYLON, position)

    async def build_gateway(self):
        if not self.structures(UnitTypeId.PYLON).ready.exists:
            return
        time_constant = self.time / 180
        gateway_num = (await self.count_building(UnitTypeId.NEXUS) - 1) * min(time_constant, 4) + 1
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if await self.count_building(UnitTypeId.GATEWAY) + await self.count_building(UnitTypeId.WARPGATE) < gateway_num:
            await self.build_(UnitTypeId.GATEWAY, pylon)

    async def build_nexus(self):
        if self.townhalls.amount == 1 and not self.structures(UnitTypeId.ASSIMILATOR).ready.exists:
            return
        if self.townhalls.amount == 2 and not self.structures(UnitTypeId.ROBOTICSFACILITY).exists:
            return
        if self.townhalls.amount == 3 and self.supply_army < 60:
            return
        if self.can_afford(UnitTypeId.NEXUS) and not self.already_pending(UnitTypeId.NEXUS):
            await self.expand_now()

    async def build_assimilator(self):
        if not self.structures(UnitTypeId.GATEWAY).exists:
            return
        time_constant = min(2.0, max(1.0, self.time / 180))
        if await self.count_building(UnitTypeId.ASSIMILATOR) < \
                int(await self.count_building(UnitTypeId.NEXUS) * time_constant):
            await self.build_assimilator_()

    async def build_cyberneticscore(self):
        if not self.structures(UnitTypeId.PYLON).ready.exists:
            return
        if not self.structures(UnitTypeId.GATEWAY).exists:
            return
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if not self.structures(UnitTypeId.CYBERNETICSCORE).exists:
            await self.build_(UnitTypeId.CYBERNETICSCORE, pylon)

    async def build_roboticsfacility(self):  # For Stalker & Colossus
        if not self.structures(UnitTypeId.PYLON).ready.exists:
            return
        if not self.structures(UnitTypeId.CYBERNETICSCORE).ready.exists:
            return
        time_constant = min(self.time // 200, 1)
        roboticsfacility_num = int(await self.count_building(UnitTypeId.NEXUS, count_pending=False) - 1) * time_constant
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if await self.count_building(UnitTypeId.ROBOTICSFACILITY) < roboticsfacility_num:
            await self.build_(UnitTypeId.ROBOTICSFACILITY, pylon)

    async def build_roboticsbay(self):  # For Stalker & Colossus
        if not self.structures(UnitTypeId.PYLON).ready.exists:
            return
        if not self.structures(UnitTypeId.ROBOTICSFACILITY).ready.exists:
            return
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if await self.count_building(UnitTypeId.ROBOTICSBAY) < 1:
            await self.build_(UnitTypeId.ROBOTICSBAY, pylon)

    async def build_twilightcouncil(self):
        if not self.structures(UnitTypeId.PYLON).ready.exists:
            return
        if not self.structures(UnitTypeId.CYBERNETICSCORE).ready.exists:
            return
        if not self.units(UnitTypeId.STALKER).ready.exists:
            return
        time_constant = min(self.time // 150, 1)
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if await self.count_building(UnitTypeId.TWILIGHTCOUNCIL) < time_constant:
            await self.build_(UnitTypeId.TWILIGHTCOUNCIL, pylon)

    async def build_templararchive(self):
        if not self.structures(UnitTypeId.PYLON).ready.exists:
            return
        if not self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready.exists:
            return
        if self.vespene > 250:
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            if await self.count_building(UnitTypeId.TEMPLARARCHIVE) < 1:
                await self.build_(UnitTypeId.TEMPLARARCHIVE, pylon)

    async def train_sentry(self):
        if not self.warp:
            if await self.count_unit(UnitTypeId.STALKER) >= 2:
                await self.train_(UnitTypeId.GATEWAY, UnitTypeId.SENTRY)
        else:
            sentry_amount = self.supply_army * 0.03 / 2 + 1
            if await self.count_unit(UnitTypeId.SENTRY) < sentry_amount:
                await self.warp_in(UnitTypeId.SENTRY)

    async def train_stalker(self):
        if not self.warp:
            if await self.count_unit(UnitTypeId.STALKER) < 2:
                await self.train_(UnitTypeId.GATEWAY, UnitTypeId.STALKER)
        else:
            stalker_amount = self.supply_army * 0.33 / 2 + 1
            if await self.count_unit(UnitTypeId.STALKER) < stalker_amount:
                await self.warp_in(UnitTypeId.STALKER)

    async def train_zealot(self):
        if self.warp:
            zealot_amount = self.supply_army * 0.2 / 2 + 1
            if await self.count_unit(UnitTypeId.ZEALOT) < zealot_amount:
                await self.warp_in(UnitTypeId.ZEALOT)

    async def train_colossus(self):
        if self.structures(UnitTypeId.ROBOTICSBAY).ready.exists:
            colossus_amount = self.supply_army * 0.25 / 6 + 1
            if await self.count_unit(UnitTypeId.COLOSSUS) < colossus_amount:
                await self.train_(UnitTypeId.ROBOTICSFACILITY, UnitTypeId.COLOSSUS)

    async def train_immortal(self):
        immortal_amount = self.supply_army * 0.19 / 4 + 1
        if await self.count_unit(UnitTypeId.IMMORTAL) < immortal_amount:
            await self.train_(UnitTypeId.ROBOTICSFACILITY, UnitTypeId.IMMORTAL)

    async def train_hightemplar(self):
        if self.vespene > 300:
            await self.warp_in(UnitTypeId.HIGHTEMPLAR)

    async def train_observer(self):
        if await self.count_unit(UnitTypeId.OBSERVER) < 1:
            await self.train_(UnitTypeId.ROBOTICSFACILITY, UnitTypeId.OBSERVER)
        elif await self.count_unit(UnitTypeId.OBSERVER) < 2 and await self.count_unit(UnitTypeId.IMMORTAL) > 0:
            await self.train_(UnitTypeId.ROBOTICSFACILITY, UnitTypeId.OBSERVER)

    async def train_warpprism(self):
        if await self.count_unit(UnitTypeId.WARPPRISM) < 2:
            await self.train_(UnitTypeId.ROBOTICSFACILITY, UnitTypeId.WARPPRISM)

    async def operation_cyberneticscore(self):  # For Ground Units
        for cyberneticscore in self.structures(UnitTypeId.CYBERNETICSCORE).ready.idle:
            if not await self.has_ability(AbilityId.RESEARCH_WARPGATE, cyberneticscore):
                self.warp = True
            elif self.can_afford(AbilityId.RESEARCH_WARPGATE):
                cyberneticscore(AbilityId.RESEARCH_WARPGATE)

    async def operation_twilightcouncil(self):
        for twilightcouncil in self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready.idle:
            if await self.has_ability(AbilityId.RESEARCH_BLINK, twilightcouncil):
                if self.can_afford(AbilityId.RESEARCH_BLINK):
                    twilightcouncil(AbilityId.RESEARCH_BLINK)
            else:
                if self.can_afford(AbilityId.RESEARCH_CHARGE):
                    twilightcouncil(AbilityId.RESEARCH_CHARGE)

    async def operation_roboticsbay(self):
        for roboticsbay in self.structures(UnitTypeId.ROBOTICSBAY).ready.idle:
            if await self.has_ability(AbilityId.RESEARCH_EXTENDEDTHERMALLANCE, roboticsbay):
                if self.can_afford(AbilityId.RESEARCH_EXTENDEDTHERMALLANCE):
                    roboticsbay(AbilityId.RESEARCH_EXTENDEDTHERMALLANCE)

    async def build_forge(self):  # Stalker & Colossus
        if not self.structures(UnitTypeId.PYLON).ready.exists:
            return
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if self.structures(UnitTypeId.ROBOTICSBAY).exists:
            if await self.count_building(UnitTypeId.FORGE) < 2:
                await self.build_(UnitTypeId.FORGE, pylon.position)

    async def operation_nexus(self):
        structures = \
            self.structures(UnitTypeId.GATEWAY) + \
            self.structures(UnitTypeId.ROBOTICSFACILITY) + \
            self.structures(UnitTypeId.WARPGATE) + \
            self.structures(UnitTypeId.CYBERNETICSCORE)
        idle_structures = \
            self.structures(UnitTypeId.GATEWAY).idle + \
            self.structures(UnitTypeId.ROBOTICSFACILITY).idle + \
            self.structures(UnitTypeId.WARPGATE).idle + \
            self.structures(UnitTypeId.CYBERNETICSCORE).idle
        working_structures = structures - idle_structures
        if len(working_structures) == 0:
            return
        for nexus in self.structures(UnitTypeId.NEXUS).ready:
            if await self.has_ability(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus):
                for structure in working_structures:
                    if not structure.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                        nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, structure)

    async def operation_forge(self):
        for forge in self.structures(UnitTypeId.FORGE).ready.idle:
            if await self.has_ability(AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1, forge):
                if self.can_afford(AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1):
                    forge(AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1)
                    return
            if await self.has_ability(AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1, forge):
                if self.can_afford(AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1):
                    forge(AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1)
                    return
            if await self.has_ability(AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL2, forge):
                if self.can_afford(AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL2):
                    forge(AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL2)
                    return
            if await self.has_ability(AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL2, forge):
                if self.can_afford(AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL2):
                    forge(AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL2)
                    return
            if await self.has_ability(AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL3, forge):
                if self.can_afford(AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL3):
                    forge(AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL3)
                    return
            if await self.has_ability(AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL3, forge):
                if self.can_afford(AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL3):
                    forge(AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL3)
                    return

    async def operation_stalker(self):
        for stalker in self.units(UnitTypeId.STALKER):
            if stalker in self.defend_troop:
                await self.defend(stalker)
            elif stalker in self.attack_troop:
                await self.attack(stalker)

            if not await self.has_ability(AbilityId.EFFECT_BLINK_STALKER, stalker):
                return
            if stalker.shield_percentage <= 0.4 and self.enemy_units.in_attack_range_of(stalker):
                stalker(AbilityId.EFFECT_BLINK_STALKER,
                        self.enemy_units.closest_to(stalker.position).position.towards(stalker.position, 14))

    async def operation_sentry(self):
        for sentry in self.units(UnitTypeId.SENTRY):
            if sentry in self.defend_troop:
                await self.defend(sentry)
            elif sentry in self.attack_troop:
                await self.attack(sentry)

            if self.enemy_units.closer_than(8, sentry.position):
                if not sentry.has_buff(BuffId.GUARDIANSHIELD):
                    if await self.can_cast(sentry, AbilityId.GUARDIANSHIELD_GUARDIANSHIELD):
                        sentry(AbilityId.GUARDIANSHIELD_GUARDIANSHIELD)
                        return

    async def operation_general_troop(self, unit: UnitTypeId, distance: int = 1):
        for unit in self.units(unit):
            if unit in self.defend_troop:
                await self.defend(unit)
            elif unit in self.attack_troop:
                await self.attack(unit)

    async def operation_observer(self):
        if not self.units(UnitTypeId.STALKER).ready.exists:
            return
        cloaked = self.enemy_units.filter(lambda unit: unit.is_cloaked)
        for observer in self.units(UnitTypeId.OBSERVER).ready.idle:
            if cloaked.amount > 0:
                observer.move(cloaked.closest_to(self.start_location).position.towards(
                    self.townhalls.first, 3))
            else:
                observer.move(self.units(UnitTypeId.STALKER).closest_to(self.enemy_start_locations[0]).position.towards(
                    self.townhalls.first, 2))

    async def operation_hightemplar(self):
        for hightemplar in self.units(UnitTypeId.HIGHTEMPLAR):
            await self.defend(hightemplar)
        if not self.structures(UnitTypeId.PYLON).ready.exists:
            return
        rally_position = self.structures(UnitTypeId.PYLON).ready.closest_to(self.enemy_start_locations[0]). \
            position.towards(self.game_info.map_center, 10)
        for i in range(1, self.units(UnitTypeId.HIGHTEMPLAR).ready.amount, 2):
            templar_a = self.units(UnitTypeId.HIGHTEMPLAR)[i]
            templar_b = self.units(UnitTypeId.HIGHTEMPLAR)[i - 1]
            if templar_a.distance_to(rally_position) < 10 and templar_b.distance_to(rally_position) < 10 :
                templar_a(AbilityId.MORPH_ARCHON)
                templar_b(AbilityId.MORPH_ARCHON)

    async def CONTROL_ATTACK(self):
        army = self.units(UnitTypeId.STALKER).ready + \
               self.units(UnitTypeId.IMMORTAL).ready + \
               self.units(UnitTypeId.SENTRY).ready + \
               self.units(UnitTypeId.ZEALOT).ready + \
               self.units(UnitTypeId.COLOSSUS).ready + \
               self.units(UnitTypeId.ARCHON).ready

        attack_troop = []
        defend_troop = []
        for unit in army:
            # For new unit that has been produced.
            if not unit in self.attack_troop and not unit in self.defend_troop:
                defend_troop.append(unit)

            # update the information of the list
            elif unit in self.attack_troop:
                attack_troop.append(unit)
            elif unit in self.defend_troop:
                defend_troop.append(unit)
            # If a unit is in combat and is injured
            elif unit in self.attack_troop and (unit.shield_percentage == 0 and unit.health_percentage < 0.25):
                defend_troop.append(unit)

        self.attack_troop = attack_troop
        self.defend_troop = defend_troop

        cloaked = self.enemy_units.filter(lambda unit: unit.is_cloaked)

        if len(self.defend_troop) >= 35 or self.supply_used >= 194:
            self.attack_troop += self.defend_troop
            self.defend_troop = []
        if len(self.attack_troop) <= 10 or \
                (self.units(UnitTypeId.OBSERVER).ready.amount < 2 and cloaked.amount != 0 and
                 self.supply_used != 200):
            self.defend_troop += self.attack_troop
            self.attack_troop = []

        print(len(self.attack_troop), len(self.defend_troop), army.amount)

    async def CONTROL_PANIC(self):
        half_map = self.start_location.position.distance_to(self.enemy_start_locations[0].position)
        enemy_unit = self.enemy_units.filter(lambda enemy: enemy.distance_to(self.start_location) < 0.25 * half_map)
        time_constant = 4 - self.time // 50
        if len(enemy_unit) < 4 or len(self.defend_troop) - time_constant > len(enemy_unit):
            for probe in self.units(UnitTypeId.PROBE):
                if probe.is_attacking:
                    probe.stop()
            await self.distribute_workers(resource_ratio=1.6)
            await self.train_probe()
        else:
            for probe in self.units(UnitTypeId.PROBE):
                await self.attack(probe)

    async def random_scout(self):
        units_to_ignore = [UnitTypeId.DRONE, UnitTypeId.SCV, UnitTypeId.PROBE, UnitTypeId.EGG, UnitTypeId.LARVA,
                           UnitTypeId.OVERLORD, UnitTypeId.OVERSEER, UnitTypeId.OBSERVER]
        detect_units = [UnitTypeId.OBSERVER, UnitTypeId.PHOTONCANNON, UnitTypeId.OVERSEER, UnitTypeId.RAVEN,
                        UnitTypeId.MISSILETURRET, UnitTypeId.SPORECRAWLER, UnitTypeId.SPORECANNON]
        if self.units(UnitTypeId.PROBE).ready.amount > 22:
            scout_worker = None
            for worker in self.workers:
                if self.has_order([AbilityId.PATROL], worker):
                    scout_worker = worker
            if not scout_worker:
                random_exp_location = random.choice(self.expansion_locations_list)
                scout_worker = self.workers.closest_to(self.start_location)
                if not scout_worker:
                    return
                await self.order(scout_worker, AbilityId.PATROL, random_exp_location)
                return
            nearby_enemy_units = self.enemy_units.filter(lambda unit: unit.type_id not in units_to_ignore).closer_than(
                10, scout_worker)
            if nearby_enemy_units.exists:
                await self.order(scout_worker, AbilityId.PATROL, self.game_info.map_center)
                return
            target = Point2((scout_worker.orders[0].target.x, scout_worker.orders[0].target.y))
            if scout_worker.distance_to(target) < 10:
                random_exp_location = random.choice(self.expansion_locations_list)
                await self.order(scout_worker, AbilityId.PATROL, random_exp_location)
                return

        if self.units(UnitTypeId.OBSERVER).ready.amount > 1:
            scout = None
            for observer in self.units(UnitTypeId.OBSERVER):
                if self.has_order([AbilityId.PATROL], observer):
                    scout = observer
            if not scout:
                random_exp_location = random.choice(self.expansion_locations_list)
                scout = self.units(UnitTypeId.OBSERVER).closest_to(self.start_location)
                if not scout:
                    return
                await self.order(scout, AbilityId.PATROL, random_exp_location)
                return
            if self.enemy_units.filter(lambda unit: unit.type_id in detect_units).closer_than(10, scout):
                await self.order(scout, AbilityId.PATROL, self.game_info.map_center)
                return
            target = Point2((scout.orders[0].target.x, scout.orders[0].target.y))
            if scout.distance_to(target) < 10:
                random_exp_location = random.choice(self.expansion_locations_list)
                await self.order(scout, AbilityId.PATROL, random_exp_location)
                return
