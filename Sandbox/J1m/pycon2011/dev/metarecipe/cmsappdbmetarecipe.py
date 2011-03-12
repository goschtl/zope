
class MetaRecipe:
    def __init__(self, buildout, name, options):

        def add_section(section_name, **values):
            if section_name in buildout._raw:
                raise KeyError("already in buildout", section_name)
            buildout._raw[section_name] = values
            buildout[section_name] # cause it to be added to the working parts

        deployment = name + '-deployment'

        add_section(deployment,
                    recipe = 'zc.recipe.deployment',
                    name=name,
                    user=options['user'],
                    )

        main_port = options['main-port']
        index_port = options.get('index-port', str(int(main_port) + 1))
        ports = main_port, index_port
        dbnames = 'main', 'index'
        servers = zip(dbnames, ports)
        for dbname, port in servers:
            add_section(name+'-'+dbname,
                        recipe = 'zc.zodbrecipes:server',
                        deployment = deployment,
                        **{'zeo.conf': zeo_conf % dict(
                            port=port,
                            customer=name,
                            dbname=dbname,
                            )})

        add_section(name+'-ctl',
                    recipe = 'zc.recipe.rhrc',
                    deployment= deployment,
                    chkconfig = '345 99 10',
                    parts = ' '.join(name+'-'+dbname
                                     for (dbname, _) in servers),
                    )

        add_section(name+'-gc.conf',
                    recipe = 'zc.recipe.deployment:configuration',
                    deployment = deployment,
                    text='\n'.join(gc_conf % dict(dbname=dbname, port=port)
                                   for (dbname, port) in servers),
                    )

        add_section(name+'-pack.sh',
                    recipe = 'zc.recipe.deployment:configuration',
                    deployment = deployment,
                    text = pack_sh % dict(
                        customer=name,
                        addresses = ' '.join(':'+port for port in ports),
                        gcconf=name+'-gc.conf',
                        ),
                    )

        add_section(name+'-pack',
                    recipe = 'zc.recipe.deployment:crontab',
                    deployment = deployment,
                    times = '1 2 * * 6',
                    command = 'sh ${%s-pack.sh:location}' % name
                    )

    update = install = lambda self: ()

zeo_conf = """
<zeo>
   address :%(port)s
</zeo>
%%import zc.zlibstorage
<zlibstorage>
  <filestorage>
     path /var/databases/%(customer)s/%(dbname)s
     pack-gc false
  </filestorage>
</zlibstorage>
"""

gc_conf = """
    <zodb %(dbname)s>
      <zeoclient>
         server :%(port)s
      </zeoclient>
    </zodb>
"""

pack_sh = """
  ${buildout:bin-directory}/zeopack -d3 -t00 \
     %(addresses)s

  ${buildout:bin-directory}/multi-zodb-gc -d3 -lERROR \
     ${%(gcconf)s:location}
"""
