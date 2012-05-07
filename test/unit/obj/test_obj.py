import pypd_obj

def fn():
    md = { 'chunk': '#X',
           'ordered_attrs': ['x', 'y', 'width', 'height', 'font-size']}

    kwargs = { 'x': 10, 'width': 100, 'height': 200, 'y': 20, 
               'font-size': 12 }

    o = pypd_obj.factory('canvas', md, **kwargs)
    print o

fn()
