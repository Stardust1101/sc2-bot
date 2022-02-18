from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId

from protoss import Protoss


class StalkerColossus(Protoss):

    async def stalker_colossus(self):
        await self.economy()
        await self.troop()
        await self.tech()
        await self.cancel_building()

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

        if len(self.defend_troop) >= 45 or self.supply_used >= 194:
            self.attack_troop += self.defend_troop
            self.defend_troop = []
        if len(self.attack_troop) <= 10:
            self.defend_troop += self.attack_troop
            self.attack_troop = []

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
