import untangle

class XmlManager(object):
    def __init__(self):
        super().__init__()

    def import_skills(self):
        try:
            obj = untangle.parse('skills.xml')
            array_of_skills = []
            for skill in obj.skills.skill:
                name = skill.name.cdata
                stat = skill.stat.cdata
                category = skill.category.cdata
                desc = skill.description.cdata
                chippable = skill.chippable.cdata
                diff = skill.diff_modifier.cdata
                short = skill.short.cdata

                skill = dict(name=name, stat=stat, category=category, desc=desc, chippable=chippable, diff=diff,
                             short=short)
                array_of_skills.append(skill)
            return array_of_skills
        except Exception:
            print('unable to load xml-file')
