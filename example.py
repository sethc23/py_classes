class Two:
    def __init__(self):
        self                                =   _parent.T.To_Sub_Classes(self,_parent)
    class Bravo:
        def __init__(self):
            self                            =   _parent.T.To_Sub_Classes(self,_parent)
            def funct_1(self):
                print                           'funct_1 of class "Bravo"'

                method_1                    =   'self.C.One.Alpha.funct_1()'
                print                           'Now executing: %s' % method_1
                eval(                           method_1)

                method_2                    =   'self.F.one_alpha_funct_1()'
                print                           'Now executing: %s' % method_2
                eval(                           method_2)

class One:
    def __init__(self):
        self                                =   _parent.T.To_Sub_Classes(self,_parent)
    class Alpha:
        def __init__(self):
            self                            =   _parent.T.To_Sub_Classes(self,_parent)
        def funct_1(self):
            print                               'This is funct_1 of class "Alpha".'


class Start:
    def __init__(self):
        from os                                 import environ          as os_environ
        from uuid                               import uuid4            as get_guid
        D                                   =   {'guid'                 :   str(get_guid().hex)[:7],
                                                 'user'                 :   os_environ['USER'],
                                                }

        self.T                              =   To_Class_Dict(D)
        self.One                            =   One(self)
        self.Two                            =   Two(self)
