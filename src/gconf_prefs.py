import gconf
import types

class AutoPrefs:
    def __init__(self, key, config):
        self.app_key = key
        self.client = gconf.client_get_default()
        self.first_run = True
        self.config = config

    def gconf_attributes(self):
        'returns a list with all the gconf attibute names'
        return self.config.keys()

    def gconf_load(self):
        casts = {gconf.VALUE_BOOL:   gconf.Value.get_bool,
                 gconf.VALUE_INT:    gconf.Value.get_int,
                 gconf.VALUE_FLOAT:  gconf.Value.get_float,
                 gconf.VALUE_STRING: gconf.Value.get_string}

        for name in self.gconf_attributes():
            gval = self.client.get(self.app_key + name)
            if gval == None: continue
            self.config[name] = casts[gval.type](gval)
            self.first_run = False
        return self.config

    def gconf_update_config(self, new_config):
        for name, value in new_config.iteritems():
            self.config[name] = value
        self.gconf_save()
        
    def gconf_save(self):
        casts = {types.BooleanType: gconf.Client.set_bool,
                 types.IntType:     gconf.Client.set_int,
                 types.FloatType:   gconf.Client.set_float,
                 types.StringType:  gconf.Client.set_string}

        for name in self.gconf_attributes():
            value = self.config[name]
            casts[type(value)](self.client, self.app_key + name, value)
