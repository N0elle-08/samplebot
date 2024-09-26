from build.actions import Actions

actions = Actions()
def funct_call(name, args):
    if name == "get_employee_details":
        return actions.get_employee_details()

