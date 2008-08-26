import grok

class Song(grok.Application,grok.Container):
    pass

class Bottle(grok.Model):
    pass

class Wall(grok.Container):
    
    def add_99_bottles(self):
        for n in range(1,100):
            self[str(n)]=Bottle()

    def remove_a_bottle(self):
        bottles=list(self.keys())
        del self[bottles[-1]]
        
    def describe_me(self):
        num_bottles=self.contents()
        if num_bottles == 0:
            text='No more bottles of beer'
        elif num_bottles == 1:
            text='1 bottle of beer'
        else:
            text='%d bottles of beer' % num_bottles
        return text
    
    def contents(self):
        return len(self.items())

class Index(grok.View):
    grok.context(Song)

    def still_beer(self):
        return self.wall.contents() > 0
    
    def take_one_down(self):
        self.wall.remove_a_bottle()

    def buy_some_more(self):
        self.wall.add_99_bottles()
        
    def describe_wall(self):
        return self.wall.describe_me()
        
    def update(self):
        self.wall=self.context['wall']
        
    def render(self):
        out=['Grok-by-Example: 99 Bottles of Beer']
        out.append('===================================')
        while self.still_beer():
            description=self.describe_wall()
            out.append('%s on the wall, %s.' % (description, description.lower()))
            self.take_one_down()
            description=self.describe_wall()
            out.append('Take one down and pass it around, %s on the wall.\n' % description.lower())
        description=self.describe_wall()
        out.append('%s on the wall, %s.' % (description, description.lower()))
        self.buy_some_more()
        description=self.describe_wall()
        out.append('Go to the store and buy some more, %s on the wall.' % description.lower())
        return '\n'.join(out)
        
@grok.subscribe(Song, grok.IObjectAddedEvent)
def handle(obj, event):
    obj['wall']=wall=Wall()
    wall.add_99_bottles()
