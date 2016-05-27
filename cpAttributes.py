__author__ = 'Toni'


from SQLAlchemyBaseClass import dbManager, DefaultTableOperations
from sqlalchemy import Column, Integer, String, Float, Boolean
from SQLAlchemyBaseClass import Base

from AWSExportImportManager import EndpointManager


# TODO move category field here


class BluePrintsTable(Base, DefaultTableOperations):
    __tablename__ = 'blueprints_table'
    name = Column(String, primary_key=True)
    description = Column(String)
    tags = Column(String)
    type = Column(String, nullable=False)
    cost = Column(Float)

    def count(self):
        c = self.get_class()
        query = self.session.query(c).order_by(c.name)
        return len(query.all())

    def add(self, name: str, description: str, cost: float):
        """adds attribute to blueprints table
        :param name: name of the attribute
        :param description: description of the attribute
        :param cost: price to rise the attribute during character creation
        """
        c = self.get_class()
        row = c(name=name, description=description, cost=cost)
        self.add_and_commit(row)

    def search_by_name(self, name):
        c = self.get_class()
        query = self.session.query(c).filter(c.name == name)
        return query.first()

    __mapper_args__ = {'polymorphic_on': type, 'polymorphic_identity': 'blueprints_table'}


class SkillBlueprints(BluePrintsTable):
    stat = Column(String)
    short = Column(String)
    diff = Column(Integer)
    category = Column(String)
    chippable = Column(Boolean)
    chip_lvl_cost = Column(Integer)
    __mapper_args__ = {'polymorphic_identity': 'skill_blueprints'}

    def add(self, name, category, stat, chippable, chip_lvl_cost, diff, cost, short, description):
        diff = int(diff)
        chip_lvl_cost = int(chip_lvl_cost)
        cost = float(cost)
        if chippable == 'yes':
            chippable = True
        else:
            chippable = False

        skill = SkillBlueprints(name=name, short=short, diff=diff, category=category, chippable=chippable,
                                chip_lvl_cost=chip_lvl_cost, cost=cost, stat=stat, description=description)
        self.add_and_commit(skill)


class StatBlueprints(BluePrintsTable):
    __mapper_args__ = {'polymorphic_identity': 'stat_blueprints'}


class ComplicationBlueprints(BluePrintsTable):
    __mapper_args__ = {'polymorphic_identity': 'complication_blueprints'}


class TalentBluePrints(BluePrintsTable):
    levelable = Column(Boolean)
    __mapper_args__ = {'polymorphic_identity': 'talent_blueprints'}


class PerkBluePrints(BluePrintsTable):
    __mapper_args__ = {'polymorphic_identity': 'perk_blueprints'}


class DefaultAttributeOperations(DefaultTableOperations):
    def __init__(self):
        super().__init__()

    def already_exists(self, char_id: int, attribute_name: str) -> bool:
        """Check if character already has the attribute

        :param char_id: Characters unique identifier
        :param attribute_name: attribute to search for
        :return: if instance is found from the database
        """
        c = self.get_class()
        query = self.session.query(c). \
            filter(c.character_id == char_id). \
            filter(c.blueprint_name == attribute_name)
        instance = query.first()
        if instance:
            return True
        else:
            return False

    def load_attribute(self, char_id, attribute_name):
        c = self.get_class()
        query = self.session.query(c). \
            filter(c.character_id == char_id). \
            filter(c.blueprint_name == attribute_name)

        instance = query.first()
        return instance


class dbStat(Base, DefaultTableOperations):
    __tablename__ = 'stats'
    id = Column(Integer, primary_key=True)
    character_id = Column(Integer)
    name = Column(String)
    short = Column(String)
    lvl = Column(Integer)
    cc = Column(Integer)

    def load_stat(self, char_id, short):
        c = self.get_class()
        query = self.session.query(c). \
            filter(c.character_id == char_id). \
            filter(c.short == short)

        instance = query.first()
        return instance

    def update_stat(self, char_id, stat_name, stat_short, lvl):
        instance = self.load_stat(char_id=char_id, short=stat_short)
        if instance:
            instance.lvl = lvl
            self.add_and_commit(instance)
        else:
            row = dbStat(character_id=char_id, short=stat_short, name=stat_name, lvl=lvl, cc=lvl)
            self.add_and_commit(row)


class dbSkills(Base, DefaultTableOperations):
    __tablename__ = 'skills'
    id = Column(Integer, primary_key=True)
    blueprint_name = Column(String)
    character_id = Column(Integer)
    chipped = Column(Boolean)
    ip = Column(Integer)
    lvl = Column(Integer)
    carbon_lvl = Column(Integer)
    field = Column(String)
    flags = Column(String)

    def already_exists(self, char_id, skill_name):
        query = self.session.query(dbSkills). \
            filter(dbSkills.character_id == char_id). \
            filter(dbSkills.blueprint_name == skill_name)
        instance = query.first()
        if instance:
            return True
        else:
            return False

    def load_skill(self, char_id, skill_name):
        query = self.session.query(dbSkills). \
            filter(dbSkills.character_id == char_id). \
            filter(dbSkills.blueprint_name == skill_name)

        instance = query.first()
        return instance

    def update_skill(self, char_id, skill_name, lvl, chipped=False, field=None, flags=None):
        if self.already_exists(char_id=char_id, skill_name=skill_name):
            print('skill already exists')
            instance = self.load_skill(char_id=char_id, skill_name=skill_name)
            instance.lvl = lvl
            self.session.add(instance)
            self.session.commit()
        else:
            row = dbSkills(blueprint_name=skill_name, lvl=lvl, carbon_lvl=lvl, character_id=char_id,
                           chipped=chipped, field=field, flags=flags, ip=0)
            self.add_and_commit(row)

    def update_ip(self, char_id, skill_name, added_ip):
        instance = self.load_skill(char_id=char_id, skill_name=skill_name)
        instance.ip += added_ip
        self.session.commit()
        return instance.ip


class dbComplication(Base, DefaultAttributeOperations):
    __tablename__ = 'complications'
    id = Column(Integer, primary_key=True)
    blueprint_name = Column(String)
    character_id = Column(Integer)
    flags = Column(String)
    intensity = Column(Integer)
    frequency = Column(Integer)
    importance = Column(Integer)

    def update_complication(self, char_id, complication_name, frequency, intensity, importance):
        if self.already_exists(char_id=char_id, attribute_name=complication_name):
            instance = self.load_attribute(char_id=char_id, attribute_name=complication_name)
            instance.frequency = frequency
            instance.intensity = intensity
            instance.importance = importance
            self.session.commit()
        else:
            row = dbComplication(blueprint_name=complication_name, character_id=char_id, frequency=frequency,
                                 intensity=intensity, importance=importance)
            self.add_and_commit(row)


class dbTalent(Base, DefaultAttributeOperations):
    __tablename__ = 'talents'
    id = Column(Integer, primary_key=True)
    blueprint_name = Column(String)
    character_id = Column(Integer)
    flags = Column(String)
    lvl = Column(Integer)

    def update_talent(self, char_id, talent_name, lvl):
        if self.already_exists(char_id=char_id, attribute_name=talent_name):
            instance = self.load_attribute(char_id=char_id, attribute_name=talent_name)
            instance.lvl = lvl
            self.session.commit()
        else:
            row = dbTalent(blueprint_name=talent_name, character_id=char_id, lvl=lvl)
            self.add_and_commit(row)


class dbPerk(Base, DefaultAttributeOperations):
    __tablename__ = 'perks'
    id = Column(Integer, primary_key=True)
    blueprint_name = Column(String)
    character_id = Column(Integer)
    target_character_id = Column(Integer)
    flags = Column(String)
    lvl = Column(Integer)

    def update_perk(self, char_id, perk_name, lvl):
        if self.already_exists(char_id=char_id, attribute_name=perk_name):
            instance = self.load_attribute(char_id=char_id, attribute_name=perk_name)
            instance.lvl = lvl
            self.session.commit()
        else:
            row = dbPerk(blueprint_name=perk_name, character_id=char_id, lvl=lvl)
            self.add_and_commit(row)

    def update_target_character(self, char_id, perk_name, target_char_id):
        if self.already_exists(char_id=char_id, attribute_name=perk_name):
            instance = self.load_attribute(char_id=char_id, attribute_name=perk_name)
            instance.target_character_id = target_char_id
            self.session.commit()


class Stat(object):
    def __init__(self, character_id, name, short, lvl=0):
        super().__init__()
        self.character_id = character_id
        self.name = name
        self.short = short
        self.lvl = lvl
        self.cc = lvl
        self.load()

        db = dbAttributesManager()
        if lvl != 0:
            db.stats.update_stat(char_id=character_id, stat_name=name, stat_short=short, lvl=lvl)
            self.lvl = lvl

    def load(self):
        db = dbAttributesManager()
        instance = db.stats.load_stat(char_id=self.character_id, short=self.short)
        if instance:
            self.name = instance.name
            self.short = instance.short
            self.lvl = instance.lvl
            self.cc = instance.cc

    def save(self):
        db = dbAttributesManager()
        db.stats.update_stat(char_id=self.character_id, stat_name=self.name, stat_short=self.short, lvl=self.lvl)


class Stats(object):
    def __init__(self, character_id, intelligence=0, reflexes=0, technique=0, dexterity=0, presence=0, willpower=0,
                 strength=0, constitution=0, move=0, body=0):
        super().__init__()
        self.stats = {}
        self.order = []
        self.character_id = character_id
        self.add(name='intelligence', short='int', lvl=intelligence)
        self.add(name='reflexes', short='ref', lvl=reflexes)
        self.add(name='technique', short='tech', lvl=technique)
        self.add(name='dexterity', short='dex', lvl=dexterity)
        self.add(name='presence', short='pre', lvl=presence)
        self.add(name='willpower', short='will', lvl=willpower)
        self.add(name='strength', short='str', lvl=strength)
        self.add(name='constitution', short='con', lvl=constitution)
        self.add(name='move', short='move', lvl=move)
        self.add(name='body', short='body', lvl=body)
        if self.has_derived_stats():
            pass
        else:
            self.calculate_derived_stats()

    def has_derived_stats(self):
        s = Stat(self.character_id, 'luck', 'luck')
        if s.cc == 0:
            return False
        else:
            return True

    def add(self, name, short, lvl):
        self.stats[short] = Stat(self.character_id, name, short, lvl)
        self.order.append(short)

    def get(self, short) -> Stat:
        return self.stats[short]

    def alter_lvl(self, short, value):
        stat = self.get(short)
        stat.lvl = value
        stat.save()

    def calculate_derived_stats(self):
        intelligence = self.get('int').lvl
        reflexes = self.get('ref').lvl
        willpower = self.get('will').lvl
        strength = self.get('str').lvl
        constitution = self.get('con').lvl
        body = self.get('body').lvl
        luck = int((intelligence + reflexes) / 2)
        humanity = willpower * 10
        recovery = int((strength + constitution) / 2)
        endurance = constitution * 2
        hits = body * 5
        stun = body * 5
        resistance = willpower * 3
        sd = constitution
        self.add('luck', 'luck', luck)
        self.add('humanity', 'hum', humanity)
        self.add('recovery', 'rec', recovery)
        self.add('endurance', 'end', endurance)
        self.add('hits', 'hits', hits)
        self.add('stun', 'stun', stun)
        self.add('resistance', 'res', resistance)
        self.add('stun defense', 'sd', sd)


class Skill(object):
    def __init__(self, name: str, char_id: int = None, chipped: bool = False, ip: int = 0, lvl: int = 0,
                 field: str = None):
        super().__init__()
        self.name = None
        self.char_id = char_id
        self.flags = ""
        self.carbon_lvl = lvl
        self.stat = None
        self.short = None
        self.diff = None
        self.category = None
        self.chippable = None
        self.chip_lvl_cost = None
        # self.load_from_db()
        self.ip = ip
        self.lvl = lvl
        self.chipped = chipped
        self.field = field

        self.load_blueprint(name)
        self.load_character_skill()
        if self.lvl != lvl and lvl != 0:
            self.lvl = lvl
        self.save_to_db()

    def add_ip_points(self, points: int):
        db = dbAttributesManager()
        db_skills = db.databases['skills']
        if self.name:
            self.ip = db_skills.update_ip(self.char_id, self.name, points)

    def save_to_db(self):
        db = dbAttributesManager()
        skills = db.databases['skills']
        if self.name and self.lvl != 0:
            skills.update_skill(self.char_id, self.name, self.lvl, self.chipped, self.field, self.flags)

    def load_blueprint(self, name) -> bool:
        db = dbAttributesManager()
        skill_blueprints = db.databases['skill_blueprints']
        blueprint = skill_blueprints.search_by_name(name)
        if blueprint:
            self.name = blueprint.name
            self.desc = blueprint.description
            self.diff = blueprint.diff
            self.chippable = blueprint.chippable
            self.category = blueprint.category
            self.chip_lvl_cost = blueprint.chip_lvl_cost
            self.stat = blueprint.stat
            self.short = blueprint.short
            return True
        else:
            return False

    def load_character_skill(self):
        db = dbAttributesManager()
        db_skills = db.databases['skills']
        skill = db_skills.load_skill(char_id=self.char_id, skill_name=self.name)
        if skill:
            self.name = skill.blueprint_name
            self.chipped = skill.chipped
            self.ip = skill.ip
            self.lvl = skill.lvl
            self.carbon_lvl = skill.carbon_lvl
            self.field = skill.field
            self.flags = skill.flags


class Complication(object):
    def __init__(self, name: str, frequency=0, intensity=0, importance=0, character_id=None):
        super().__init__()
        self.name = name
        self.character_id = character_id
        self.frequency = None
        self.intensity = None
        self.importance = None
        self.desc = None
        self.category = None
        self.load_blueprint(name)
        self.load_character_complication()
        if frequency != 0 and intensity != 0 and importance != 0:
            self.frequency = frequency
            self.importance = importance
            self.intensity = intensity
        self.save_to_db()

    def save_to_db(self):
        db = dbAttributesManager()
        if self.desc is not None and self.frequency is not None and self.importance is not None:
            if self.intensity is not None:
                db.complications.update_complication(char_id=self.character_id, complication_name=self.name,
                                                     frequency=self.frequency, intensity=self.intensity,
                                                     importance=self.importance)

    def load_blueprint(self, name):
        db = dbAttributesManager()
        complication_blueprints = db.databases['complication_blueprints']
        blueprint = complication_blueprints.search_by_name(name)
        if blueprint:
            self.desc = blueprint.description
            # self.category = blueprint.category

    def load_character_complication(self):
        db = dbAttributesManager()
        complication = db.complications.load_attribute(self.character_id, self.name)
        if complication:
            self.frequency = complication.frequency
            self.intensity = complication.intensity
            self.importance = complication.importance


class Talent(object):
    def __init__(self, character_id, name, lvl=0):
        super().__init__()
        self.name = name
        self.lvl = lvl
        self.desc = None
        self.character_id = character_id
        self.load_blueprint(name)
        self.load_character_attribute()
        if lvl != 0:
            self.lvl = lvl
            self.save_to_db()

    def save_to_db(self):
        if self.desc is not None:
            db = dbAttributesManager()
            db.talents.update_talent(char_id=self.character_id, talent_name=self.name, lvl=self.lvl)

    def load_blueprint(self, name):
        db = dbAttributesManager()
        blueprint = db.talent_blueprints.search_by_name(name)
        if blueprint:
            self.desc = blueprint.description

    def load_character_attribute(self):
        db = dbAttributesManager()
        talent = db.talents.load_attribute(self.character_id, self.name)
        if talent:
            self.lvl = talent.lvl


class Perk(object):
    def __init__(self, character_id, name, lvl=0):
        super().__init__()
        self.name = name
        self.lvl = lvl
        self.desc = None
        self.cost = None
        self.character_id = character_id
        self.load_blueprint(name)
        self.load_character_attribute()
        if lvl != 0:
            self.lvl = lvl
            self.save_to_db()

    def save_to_db(self):
        if self.desc is not None:
            db = dbAttributesManager()
            db.perks.update_perk(char_id=self.character_id, perk_name=self.name, lvl=self.lvl)

    def load_blueprint(self, name):
        db = dbAttributesManager()
        blueprint = db.perk_blueprints.search_by_name(name)
        if blueprint:
            self.desc = blueprint.description
            self.cost = blueprint.cost

    def load_character_attribute(self):
        db = dbAttributesManager()
        perk = db.perks.load_attribute(self.character_id, self.name)
        if perk:
            self.lvl = perk.lvl


class dbAttributesManager(dbManager):
    def __init__(self):
        super().__init__("sqlite:///attributes.db", echo=False)
        blueprints_master = BluePrintsTable()
        self.skill_blueprints = SkillBlueprints()
        self.complication_blueprints = ComplicationBlueprints()
        self.talent_blueprints = TalentBluePrints()
        self.perk_blueprints = PerkBluePrints()
        self.skills = dbSkills()
        self.complications = dbComplication()
        self.talents = dbTalent()
        self.perks = dbPerk()
        self.stats = dbStat()

        blueprints_master.set_session(self.session)
        self.skill_blueprints.set_session(self.session)
        self.complication_blueprints.set_session(self.session)
        self.talent_blueprints.set_session(self.session)
        self.perk_blueprints.set_session(self.session)
        self.skills.set_session(self.session)
        self.complications.set_session(self.session)
        self.talents.set_session(self.session)
        self.perks.set_session(self.session)
        self.stats.set_session(self.session)

        self.databases['blueprints_table'] = blueprints_master
        self.databases['skill_blueprints'] = self.skill_blueprints
        self.databases['complication_blueprints'] = self.complication_blueprints
        self.databases['skills'] = self.skills
        if self.skill_blueprints.count() == 0:
            self.load_attributes(attribute_type='skill', db_table=self.skill_blueprints)
        if self.complication_blueprints.count() == 0:
            self.load_attributes(attribute_type='complication', db_table=self.complication_blueprints)
        if self.talent_blueprints.count() == 0:
            self.load_attributes(attribute_type='talent', db_table=self.talent_blueprints)
        if self.perk_blueprints.count() == 0:
            self.load_attributes(attribute_type='perk', db_table=self.perk_blueprints)

    def load_attributes(self, attribute_type, db_table):
        ep_mgr = EndpointManager()
        attributes = ep_mgr.get_attributes(attribute_type)
        for attribute in attributes:
            name = attribute['name']
            print('saving ' + name + '...')
            diff = attribute['diff']
            stat = attribute['stat']
            category = attribute['category']
            cost = attribute['cost']
            short = attribute['short']
            desc = attribute['desc']
            chippable = attribute['chippable']
            chip_lvl_cost = attribute['chip_lvl_cost']
            if attribute_type == 'skill':
                db_table.add(name=name, category=category, stat=stat, chippable=chippable, chip_lvl_cost=chip_lvl_cost,
                             diff=diff, cost=cost, short=short, description=desc)
            else:
                db_table.add(name=name, description=desc, cost=cost)


def main():
    db_mgr = dbAttributesManager()


if __name__ == '__main__':
    main()
