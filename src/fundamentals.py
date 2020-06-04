class point:
    def __init__(self,x,y):
        self.x=x
        self.y=y

class object:
    def __init__(self,points=[],x=0,y=0,width=0,height=0):
        self.points=points[:]
        self.x=x
        self.y=y
        self.width=width
        self.height=height
        self.name=""

class layer__:
    def __init__(self):
        self.objects=[]
        self.name=""
    def new_object(self,points=[]):
        object_to_be_appended=object(points)
        self.object.append(object_to_be_appended)

class time_strip:
    def __init__(self):
        self.layers=[]
        self.name=""
    def new_layer(self):
        layer_to_be_appended=layer()
        self.layers.append(layer_to_be_appended)

class animation:
    def __init__(self):
        self.time_strips=[]
        self.unit_time=0.01
    def new_time_strip(self):
        time_strip_to_be_appended=time_strip()
        self.time_strip.append(time_strip_to_be_appended)

class curves:
    def __init__(self,x=0,y=0):
        pass
    def midpoint(self,p1,p2,T,t):
        result=[0,0]
        result[0]=p1[0]+((p2[0]-p1[0])/T)*t
        result[1]=p1[1]+((p2[1]-p1[1])/T)*t
        return result
    def make_(self,points,T,t):
        if len(points)==2:
            return self.midpoint(points[0],points[1],T,t)
        new_points=[]
        for point_index in range(len(points)-1):
            mid_=self.midpoint(points[point_index],points[point_index+1],T,t)
            new_points.append(mid_)
        return self.make_(new_points,T,t)
    def find_curve(self,points,T=10):
        curve=[points[0]]
        t=1
        while t<T:
            new_points=self.make_(points,T,t)
            curve.append(new_points)
            t+=1
        curve.append(points[-1])
        return curve
