import os
import sys
from Control import *
from Satellite_image import *
from S2 import *
from FirstPage import *
from SecondPage import *

os.environ['PROJ_LIB'] = "${CONDA_PREFIX}/Library/share/proj"
GDAL_DISABLE_READDIR_ON_OPEN = False


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = FirstPage()
    win.show()
    sys.exit(app.exec_())


def call():
    Control.getImage(S2)
    S2.countValues(self)
    Control.showInstances(S2)


if __name__ == "__main__":
    main()



