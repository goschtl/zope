import boto.ec2.connection


class EBS:
    def __init__(self, buildout, name, options):
        self.size = options['size']
        self.zone = options['zone']
        self.vol_name = options['name']

        self.conn = boto.ec2.connection.EC2Connection(
            region=options['region']
        )

    def install(self):
        '''Create a EBS volumen and set tags
        '''
        vol = self.conn.create_volume(int(self.size), self.zone)
        self.conn.create_tags([vol.id], dict(Name=self.vol_name))
        return ()

    update = install
