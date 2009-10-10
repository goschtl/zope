from lms.main.app import LmsMain, addLmsMain_form, addLmsMain

def initialize(registrar):
    registrar.registerClass(LmsMain,
                            constructors=(addLmsMain_form, addLmsMain))
