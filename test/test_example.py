# def test_eq_or_not_eq():
#     assert 3 == 3
#     assert 3 != 2

# import pytest

# class Student:
#     def __init__(self, first_name: str, last_name: str, major: str, years: int):
#         self.first_name = first_name
#         self.last_name = last_name
#         self.major = major
#         self.years = years

# @pytest.fixture
# def default_employee():
#     return Student('John', 'Doe', 'Computer Science', 3)

# def test_person_identify(default_employee):
#     p = default_employee
#     assert p.first_name == 'John', 'First Name should be John'
#     assert p.last_name == 'Doe', 'Last Name should be Doe'
#     assert p.major == 'Computer Science', 'major should be Computer Science'
#     assert p.years == 3