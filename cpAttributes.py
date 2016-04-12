__author__ = 'Toni'

from SQLAlchemyBaseClass import dbManager, DefaultTableOperations
from sqlalchemy import Column, Integer, String, Float, Boolean
from SQLAlchemyBaseClass import Base

from AWSExportImportManager import EndpointManager


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

    def add(self, name, description, cost):
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
        if chippable=='yes':
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

    def already_exists(self, char_id, attribute_name):
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

class Skill(object):
    def __init__(self, name:str, char_id:int=None, chipped:bool=False, ip:int=0, lvl:int=0, field:str=None):
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

    def add_ip_points(self, points:int):
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
    def __init__(self, name:str, frequency=0, intensity=0, importance=0, character_id=None):
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

        blueprints_master.set_session(self.session)
        self.skill_blueprints.set_session(self.session)
        self.complication_blueprints.set_session(self.session)
        self.talent_blueprints.set_session(self.session)
        self.perk_blueprints.set_session(self.session)
        self.skills.set_session(self.session)
        self.complications.set_session(self.session)
        self.talents.set_session(self.session)
        self.perks.set_session(self.session)

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
    blueprints = db_mgr.databases['skill_blueprints']


if __name__ == '__main__':
    main()


