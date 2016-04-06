__author__ = 'Toni'

from SQLAlchemyBaseClass import dbManager, DefaultTableOperations
from sqlalchemy import Column, Integer, String, Float, Boolean
from SQLAlchemyBaseClass import Base
from XmlManager import XmlManager

class BluePrintsTable(Base, DefaultTableOperations):
    __tablename__ = 'blueprints_table'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    tags = Column(String)
    type = Column(String, nullable=False)
    cost = Column(Float)

    __mapper_args__ = {'polymorphic_on': type, 'polymorphic_identity': 'blueprints_table'}

class SkillBlueprints(BluePrintsTable):
    stat = Column(String)
    short = Column(String)
    diff = Column(Integer)
    category = Column(String)
    chippable = Column(Boolean)
    chip_lvl_cost = Column(Integer)
    __mapper_args__ = {'polymorphic_identity': 'skill_blueprints'}

    def search_by_name(self, name):
        query =  self.session.query(SkillBlueprints).filter(SkillBlueprints.name == name)
        return query.first()

class StatBlueprints(BluePrintsTable):
    __mapper_args__ = {'polymorphic_identity': 'stat_blueprints'}

class ComplicationBlueprints(BluePrintsTable):
    __mapper_args__ = {'polymorphic_identity': 'complication_blueprints'}

class TalentBluePrints(BluePrintsTable):
    levelable = Column(Boolean)
    __mapper_args__ = {'polymorphic_identity': 'talent_blueprints'}

class PerkBluePrints(BluePrintsTable):
    __mapper_args__ = {'polymorphic_identity': 'perk_blueprints'}

class dbSkills(Base, DefaultTableOperations):
    __tablename__ = 'skills'
    id = Column(Integer, primary_key=True)
    blueprint_id = Column(Integer)
    character_id = Column(Integer)
    chipped = Column(Boolean)
    ip = Column(Integer)
    lvl = Column(Integer)
    carbon_lvl = Column(Integer)
    field = Column(String)
    flags = Column(String)

    def find_with_character_and_blueprint_id(self, char_id, bp_id):
        query = self.session.query(dbSkills). \
                filter(dbSkills.character_id == char_id). \
                filter(dbSkills.blueprint_id == bp_id)
        instance = query.first()
        return instance

class dbComplication(Base, DefaultTableOperations):
    __tablename__ = 'complications'
    id = Column(Integer, primary_key=True)
    blueprint_id = Column(Integer)
    character_id = Column(Integer)
    flags = Column(String)
    intensity = Column(Integer)
    frequency = Column(Integer)
    importance = Column(Integer)

    def find(self, char_id, bp_id):
        query = self.session.query(dbComplication). \
            filter(dbComplication.character_id == char_id). \
            filter(dbComplication.blueprint_id == bp_id)
        instance = query.first()
        return instance

class Skill(object):
    def __init__(self, name:str, table_id:int=None, bp_id:int=None, char_id:int=None, chipped:bool=False, ip:int=0,
                 lvl:int=0, field:str=None):
        super().__init__()
        self.id = table_id
        self.name = name
        self.bp_id = bp_id
        self.char_id = char_id
        self.flags = ""
        self.carbon_lvl = 0
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

    def save_to_db(self):
        db = dbAttributesManager()
        skills = db.databases['skills']

        instance = skills.find_with_character_and_blueprint_id(self.char_id, self.bp_id)
        if instance:
            instance.blueprint_id = self.bp_id
            instance.carbon_lvl = self.carbon_lvl
            instance.character_id = self.char_id
            instance.chipped = self.chipped
            instance.field = self.field
            instance.tags = self.flags
            instance.ip = self.ip
            instance.lvl = self.lvl
            skills.session.commit()
        else:
            row = dbSkills(blueprint_id=self.bp_id, carbon_lvl=self.carbon_lvl, character_id = self.char_id,
                     chipped=self.chipped, field=self.field, flags=self.flags, ip=self.ip, lvl=self.lvl)
            skills.add_and_commit(row)


    def load_from_db(self):
        char_id = self.char_id
        search_name = self.name
        db = dbAttributesManager()
        db_skills = db.databases['skills']
        if char_id and search_name:
            if self.succesful_skill_blueprint_id(search_name):
                instance = db_skills.find_with_character_and_blueprint_id(char_id=char_id, bp_id=self.bp_id)
                if instance:
                    self.id = instance.id
        if self.id:
            self.load_from_db_skills(self.id)
        if self.bp_id:
            self.load_from_db_bp_skills(self.bp_id)

    def succesful_skill_blueprint_id(self, name) -> bool:
        db = dbAttributesManager()
        skill_blueprints = db.databases['skill_blueprints']
        bp_row = skill_blueprints.search_by_name(name)
        if bp_row:
            self.bp_id = bp_row.id
            return True
        else:
            return False

    def load_from_db_skills(self, id):
        db = dbAttributesManager()
        db_skills = db.databases['skills']
        skill = db_skills.find(id)
        if skill:
            self.id = skill.id
            self.bp_id = skill.blueprint_id
            self.char_id = skill.character_id
            self.chipped = skill.chipped
            self.ip = skill.ip
            self.lvl = skill.lvl
            self.carbon_lvl = skill.carbon_lvl
            self.field = skill.field
            self.flags = skill.flags

    def load_from_db_bp_skills(self, id):
        db = dbAttributesManager()
        db_blueprints = db.databases['skill_blueprints']
        blueprint = db_blueprints.find(id)
        if blueprint:
            self.name = blueprint.name
            self.stat = blueprint.stat
            self.short = blueprint.short
            self.diff = blueprint.diff
            self.category = blueprint.category
            self.chippable = blueprint.chippable
            self.chip_lvl_cost = blueprint.chip_lvl_cost

class Complication(object):
    def __init__(self, name:str, frequency=0, intensity=0, importance=0, id=None, character_id=None, blueprint_id=None):
        super().__init__()
        self.name = name
        self.id = id
        self.character_id = character_id
        self.blueprint_id = blueprint_id
        self.frequency = frequency
        self.intensity = intensity
        self.importance = importance

    def load_from_db(self, character_id):
        if self.character_id and self.name:
            pass




class dbAttributesManager(dbManager):
    def __init__(self):
        super().__init__("sqlite:///attributes.db", echo=False)
        blueprints_master = BluePrintsTable()
        skill_blueprints = SkillBlueprints()
        complication_blueprints = ComplicationBlueprints()
        db_skills = dbSkills()

        blueprints_master.set_session(self.session)
        skill_blueprints.set_session(self.session)
        complication_blueprints.set_session(self.session)
        db_skills.set_session(self.session)

        self.databases['blueprints_table'] = blueprints_master
        self.databases['skill_blueprints'] = skill_blueprints
        self.databases['complication_blueprints'] = complication_blueprints
        self.databases['skills'] = db_skills

def main():
    db_mgr = dbAttributesManager()
    blueprints = db_mgr.databases['skill_blueprints']
    rows_num = blueprints.count()
    if rows_num == 0:
        xml_mgr = XmlManager()
        skills = xml_mgr.import_skills()
        print(skills)
    '''if blueprints.count() == 0:
        xml_mgr = XmlManager()
        xml_mgr.import_skills()
    del(blueprints)'''
    # row = SkillBlueprints(category="reflexes", chip_lvl_cost = 100, chippable=True, diff=1, short="han", stat="ref",
    #                      name="hangun")
    # blueprints.add_and_commit(row)
    # s = Skill("hangun", char_id=1, lvl=3)
    # s.save_to_db()
    # print(s.category)
    # print(s.lvl)
    # print(s.bp_id)
    #s.save_to_db()


if __name__ == '__main__':
    main()


