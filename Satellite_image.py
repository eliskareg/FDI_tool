class SatelliteImage(object):
    images = []

    def __init__(self, name):
        self.name = name
        self.md_file = ""
        self.satellite = ""
        self.date = ""
        self.time = ""
        self.gml_coordinates = ""
        self.images.append(self)



