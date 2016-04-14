__author__ = 'Toni'

#!/usr/bin/env python

from distutils.core import setup

setup(name='cpAttributes',
      version='1.2',
      description='cpAttributes to use for character',
      author='Toni Nurmi',
      author_email='toni.nurmi@hotmail.com',
      install_requires=['SQLAlchemyBaseClass',
                        'awsExportImportManager',
                        'sqlalchemy'],
      dependency_links=['https://github.com/Krypticdator/SQLAlchemyBaseClass.git#egg=SQLAlchemyBaseClass-1.2',
                        'https://github.com/Krypticdator/AWSExportImportManager.git#egg=awsExportImportManager-1.1']
     )