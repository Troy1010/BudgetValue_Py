from setuptools import setup

setup(name='BudgetValue_Py'
    ,version='0.1'
    ,description='Financial Budgeting program'
    ,author='Troy1010'
    #,author_email=''
    ,url='https://github.com/Troy1010/BudgetValue_Py'
    ,license=''
    ,packages=['BudgetValue']
    ,zip_safe=False
    ,test_suite='nose.collector'
    ,tests_require=['nose']
    ,python_requires=">=3.6"
    #,install_requires=['dill']
    ,setup_requires=['nose']
    )
