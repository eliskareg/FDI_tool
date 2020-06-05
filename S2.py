import sys
import os
import fnmatch
import xml.etree.ElementTree as Etree
import xml.dom as dom
import fiona
import rasterio
import rasterio.mask
from rasterio.enums import Resampling
from osgeo import gdal
from osgeo import ogr
from osgeo import osr
from osgeo import gdal_array
from osgeo import gdalconst
from Satellite_image import SatelliteImage


class S2(SatelliteImage):
    images = []
    dirname = ""

    def __init__(self, name):
        super().__init__(name)
        self.cloud_cover = ""
        self.processing_level = ""
        self.tile_id = ""
        self.shp_path = ""
        self.ndvi = False
        self.rsr = False
        self.rvsi = False
        self.reip = False

    def getMetaDataFile(self):
        for path, sub_dirs, files in os.walk(self.dirname + "/" + self.name):
            for file in files:
                while file.startswith("MTD"):
                    self.md_file = file
                    self.parseXML(file)
                    return

    def parseXML(self, file):
        print(self.dirname + " " + self.name + " " + file)
        tree = Etree.parse(self.dirname + "/" + self.name + "/" + file)
        root = tree.getroot()
        self.satellite = root[0][0][9][0].text
        self.date = formatDateTime(root[0][0][9][2].text, 0)
        self.time = formatDateTime(root[0][0][9][2].text, 1)
        self.gml_coordinates = root[1][0][0][0][0].text
        self.cloud_cover = "{:.3f}".format(float(root[3][0].text))
        self.processing_level = root[0][0][3].text
        self.tile_id = self.name[39:44]

    def getBands(self):
        print("========================================================================================================"
              "\n")
        bands = ["B04", "B05", "B06", "B07", "B08", "B11"]
        if not self.ndvi:
            bands.remove("B08")
            if not (self.rsr or self.reip):
                bands.remove("B04")

        if not self.reip:
            if not self.rsr:
                bands.remove("B07")
            if not self.rvsi:
                bands.remove("B05")
                bands.remove("B06")

        if not self.rsr:
            bands.remove("B11")

        if bands:
            print("Retrieving of spectral bands for the image " + self.name[0:60])
            for band in bands:
                result = self.getBand(band)
                if result is None:
                    print(band + " image was not found.")
                    return
                else:
                    print(result)
        else:
            print("No spectral bands needed for the image " + self.name[0:60])

    def getBand(self, band):
        res = self.setResolution(band)
        for path, sub_dirs, files in os.walk(self.dirname + "/" + self.name + "/GRANULE/"):
            for file in files:
                if fnmatch.fnmatch(file, "*_" + band + "_" + res + "*.jp2") or fnmatch.fnmatch(file,
                                                                                               "*_" + band + ".jp2"):
                    setattr(self, band + "_" + res, path + "/" + file)
                    return band + " image is found in a spatial resolution of " + res + " metres."

    def countValues(self):
        attrs = ["ndvi", "rsr", "rvsi", "reip"]
        for attr in attrs:
            value = getattr(self, attr)
            if value:
                print("Checking output data folder.")
                getattr(self, "count" + attr.upper())()

    @staticmethod
    def setResolution(band):
        switch = {
            "B01": "60",
            "B02": "10",
            "B03": "10",
            "B04": "10",
            "B05": "20",
            "B06": "20",
            "B07": "20",
            "B08": "10",
            "B8A": "20",
            "B09": "60",
            "B10": "60",
            "B11": "20",
            "B12": "20",
        }
        return switch.get(band)

    @staticmethod
    def createOutDir():
        try:
            os.mkdir(S2.dirname + "/Output_data")
            print("Output_data directory was created.")
            return True
        except OSError:
            if os.path.exists(S2.dirname + "/Output_data"):
                print("Output_data directory already exists.")
                return True
            else:
                print("Creation of Output_data directory failed.")
                return False

    def extractByMask(self, ending):
        shp_name = ((os.path.basename(self.shp_path)).split("."))[0][0:10]
        try:
            print("Extracting by mask of inserted SHP...")
            with fiona.open(self.shp_path, "r") as shapefile:
                shapes = [feature["geometry"] for feature in shapefile]
                print(self.shp_path)
                print(self.dirname + "/Output_data/" + self.name[7:26] + self.name[37:44] + ending)
                with rasterio.open(self.dirname + "/Output_data/" + self.name[7:26] + self.name[37:44] + ending, "r+") \
                        as src:
                    out_image, out_transform = rasterio.mask.mask(src, shapes, crop=True, filled=True, nodata=-999)
                    out_meta = src.meta
                    out_crs = src.crs
                    out_meta.update({"driver": "GTiff",
                                     "crs": out_crs,
                                     "height": out_image.shape[1],
                                     "width": out_image.shape[2],
                                     "transform": out_transform})
                    with rasterio.open(self.dirname + "/Output_data/" + self.name[0:27] + shp_name[0:10] + ending,
                                       "w", **out_meta) as output_image:
                        output_image.write(out_image)
                        print(self.name[0:27] + shp_name[0:10] + ending + " image was created.")
            return

        except ValueError:
            print("Extraction failed.")
        return

    def countNDVI(self):
        if os.path.isfile(self.dirname + "/Output_data/" + self.name[7:26] + self.name[37:44]
                          + "_10m_NDVI.tiff"):
            print("File " + self.name[7:26] + self.name[37:44] + "_10m_NDVI.tiff already exists.")
            if self.shp_path != "":
                shp_name = ((os.path.basename(self.shp_path)).split("."))[0]
                if os.path.isfile(self.dirname + "/Output_data/" + self.name[0:27] + shp_name + "_10m_NDVI.tiff"):
                    print("File " + self.name[0:27] + shp_name + "_10m_NDVI.tiff already exists.")
                    return
                else:
                    self.extractByMask("_10m_NDVI.tiff")
                    return
            else:
                return
        else:
            print("Preparing data...")

        with rasterio.open(self.B04_10, driver='JP2OpenJPEG') as b4:
            B04 = b4.read()
        with rasterio.open(self.B08_10, driver='JP2OpenJPEG') as b8:
            B08 = b8.read()
        print("Bands for calculating NDVI have been loaded.")

        ndvi_formula = (B08.astype(float) - B04.astype(float)) / (B08.astype(float) + B04.astype(float))

        with rasterio.open(self.dirname + "/Output_data/" + self.name[7:26] + self.name[37:44]
                           + "_10m_NDVI.tiff", "w", driver="Gtiff", width=b4.width, height=b4.height, count=1,
                           crs=b4.crs, transform=b4.transform, dtype=rasterio.float32) as output_image:
            output_image.write(ndvi_formula.astype(rasterio.float32))
        if self.shp_path != "":
            self.extractByMask("_10m_NDVI.tiff")
        return

    def countREIP(self):
        if os.path.isfile(self.dirname + "/Output_data/" + self.name[7:26] + self.name[37:44]
                          + "_20m_REIP.tiff"):
            print("File " + self.name[7:26] + self.name[37:44] + "_20m_REIP.tiff already exists.")
            if self.shp_path != "":
                shp_name = ((os.path.basename(self.shp_path)).split("."))[0]
                if os.path.isfile(self.dirname + "/Output_data/" + self.name[0:27] + shp_name + "_20m_REIP.tiff"):
                    print("File " + self.name[0:27] + shp_name + "_20m_REIP.tiff already exists.")
                    return
                else:
                    self.extractByMask("_20m_REIP.tiff")
                    return
            else:
                return
        else:
            print("Preparing data...")

        with rasterio.open(self.B05_20, driver='JP2OpenJPEG') as b5:
            B05 = b5.read()
            B05 = B05.astype(float)
        with rasterio.open(self.B06_20, driver='JP2OpenJPEG') as b6:
            B06 = b6.read()
            B06 = B06.astype(float)
        with rasterio.open(self.B07_20, driver='JP2OpenJPEG') as b7:
            B07 = b7.read()
            B07 = B07.astype(float)

        if hasattr(self, "B04_20"):
            with rasterio.open(self.B04_20, driver='JP2OpenJPEG') as b4:
                B04 = b4.read()
                B04 = B04.astype(float)
        else:
            print("Resampling B04...")
            with rasterio.open(self.B04_10, driver='JP2OpenJPEG') as b4:
                B04 = b4.read(out_shape=(b5.height, b5.width), resampling=Resampling.bilinear)
                B04 = B04.astype(float)

        print("Bands for calculating REIP have been loaded.")

        reip_formula_1 = (B04 + B07) / 2 - B05
        reip_formula_2 = reip_formula_1 / (B06 - B05)
        reip_formula = 700 + 40 * reip_formula_2
        # REIP formula was divided due to the high complexity of the calculation

        # It is possible to enable 'always overcommit' mode, if at least 8 GB RAM and 64-bit system is available.
        # reip_formula = 700 + 40 * (((B04 + B07) / 2 - B05) / (B06 - B05)

        with rasterio.open(self.dirname + "/Output_data/" + self.name[7:26] + self.name[37:44] + "_20m_REIP.tiff",
                           "w", driver="Gtiff", width=b5.width, height=b5.height, count=1, crs=b5.crs,
                           transform=b5.transform, dtype=rasterio.float32) as output_image:
            output_image.write(reip_formula.astype(rasterio.float32))
        if self.shp_path != "":
            self.extractByMask("_20m_REIP.tiff")
        return

    def countRSR(self):
        if os.path.isfile(self.dirname + "/Output_data/" + self.name[7:26] + self.name[37:44]
                          + "_20m_RSR.tiff"):
            print("File " + self.name[7:26] + self.name[37:44] + "_20m_RSR.tiff already exists.")
            if self.shp_path != "":
                shp_name = ((os.path.basename(self.shp_path)).split("."))[0]
                if os.path.isfile(self.dirname + "/Output_data/" + self.name[0:27] + shp_name + "_20m_RSR.tiff"):
                    print("File " + self.name[0:27] + shp_name + "_20m_RSR.tiff already exists.")
                    return
                else:
                    self.extractByMask("_20m_RSR.tiff")
                    return
            else:
                return
        else:
            print("Preparing data...")

        with rasterio.open(self.B07_20, driver='JP2OpenJPEG') as b7:
            B07 = b7.read()
            B07 = B07.astype(float)
        with rasterio.open(self.B11_20, driver='JP2OpenJPEG') as b11:
            B11 = b11.read()
            B11 = B11.astype(float)
            for band in B11:
                B11_min = band.min()
                B11_max = band.max()

        if hasattr(self, "B04_20"):
            with rasterio.open(self.B04_20, driver='JP2OpenJPEG') as b4:
                B04 = b4.read()
                B04 = B04.astype(float)
        else:
            print("Resampling B04...")
            with rasterio.open(self.B04_10, driver='JP2OpenJPEG') as b4:
                B04 = b4.read(out_shape=(b7.height, b7.width), resampling=Resampling.bilinear)
                B04 = B04.astype(float)

        print("Bands for calculating RSR have been loaded.")

        rsr_formula_1 = (B11_max - B11) / (B11_max - B11_min)
        rsr_formula = (B07 / B04) * rsr_formula_1

        # RSR formula was divided due to the high complexity of the calculation.
        # It is possible to enable 'always overcommit' mode, if at least 8 GB RAM and 64-bit system is available.
        # If you would like to do that, replace rsr_formula_1 and rsr_formula with the row below:
        # rsr_formula = (B07 / B04) * ((B11_stats[max] - B11) / (B11_stats[max]) - B11_stats[min])

        with rasterio.open(self.dirname + "/Output_data/" + self.name[7:26] + self.name[37:44] + "_20m_RSR.tiff",
                           "w", driver="Gtiff", width=b7.width, height=b7.height, count=1, crs=b7.crs,
                           transform=b7.transform, dtype=rasterio.float32) as output_image:
            output_image.write(rsr_formula.astype(rasterio.float32))
        if self.shp_path != "":
            self.extractByMask("_20m_RSR.tiff")
        return

    def countRVSI(self):
        if os.path.isfile(self.dirname + "/Output_data/" + self.name[7:26] + self.name[37:44]
                          + "_20m_RVSI.tiff"):
            print("File " + self.name[7:26] + self.name[37:44] + "_20m_RVSI.tiff already exists.")
            if self.shp_path != "":
                shp_name = ((os.path.basename(self.shp_path)).split("."))[0]
                if os.path.isfile(self.dirname + "/Output_data/" + self.name[0:27] + shp_name + "_20m_RVSI.tiff"):
                    print("File " + self.name[0:27] + shp_name + "_20m_RVSI.tiff already exists.")
                    return
                else:
                    self.extractByMask("_20m_RVSI.tiff")
                    return
            else:
                return
        else:
            print("Preparing data...")

        with rasterio.open(self.B05_20, driver='JP2OpenJPEG') as b5:
            B05 = b5.read()
            B05 = B05.astype(float)
        with rasterio.open(self.B06_20, driver='JP2OpenJPEG') as b6:
            B06 = b6.read()
            B06 = B06.astype(float)
            for band in B06:
                B06_min = band.min()

        print("Bands for calculating RVSI have been loaded.")

        rvsi_formula = ((B05 + B06) / 2) - B06_min

        with rasterio.open(self.dirname + "/Output_data/" + self.name[7:26] + self.name[37:44] + "_20m_RVSI.tiff",
                           "w", driver="Gtiff", width=b5.width, height=b5.height, count=1, crs=b5.crs,
                           transform=b5.transform, dtype=rasterio.float32) as output_image:
            output_image.write(rvsi_formula.astype(rasterio.float32))

        if self.shp_path != "":
            self.extractByMask("_20m_RVSI.tiff")
        return


def formatDateTime(datetime, part):
    date = datetime[0:10]
    time = datetime[11:23]
    if part == 0:
        return date
    elif part == 1:
        return time
