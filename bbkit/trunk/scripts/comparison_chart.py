from ConfigParser import SafeConfigParser

def process_file(file_name):
    config_parser = SafeConfigParser()
    config_parser.read(file_name)
    section_attrs = dict(config_parser.items('versions'))
    return section_attrs
    
if __name__ == '__main__':
    bb_section_attrs = process_file('releases/bluebream-1.0a2.cfg')
    zope_section_attrs = process_file('releases/zope-3.4.0.cfg')
    for key, value in zope_section_attrs.iteritems():
        print "+"+ ''.rjust(31, '-') + "+" + ''.rjust(25, '-') + "+" + ''.rjust(54, '-') + "+"
        key_len = len(key)
        if key in bb_section_attrs:
            bb_len = len(bb_section_attrs[key])
            rjust = 48 if (bb_len==5) else 47
            print "|", key.ljust(29), "|", value.ljust(23), "|", bb_section_attrs[key], "|".rjust(rjust)
        else:
            #print "|", key.ljust(29), "|", value, "|".rjust(19), "|".rjust(54)
            rjust = 19 if (len(value)==5) else 21
            print "|", key.ljust(29), "|".rjust(rjust), "|".rjust(10), value, "|".rjust(54)
    for key, value in bb_section_attrs.iteritems():
        if key not in zope_section_attrs:
            rjust = 19 if (len(value)==5) else 21
            print "|", key.ljust(29), "|", value, "|".rjust(rjust), "|".rjust(54)
    print "+"+ ''.rjust(31, '-') + "+" + ''.rjust(25, '-') + "+" + ''.rjust(54, '-') + "+"
