from qgis.utils import iface
from qgis.core import * 

class PerfectFilterFunctions(): 
    def __init__(self) -> None:
        self.instance = QgsProject.instance()
        self.canvas = iface.mapCanvas()
        pass
    
    def GetProjectLayers(self) -> list:
        """GetProjectLayers Get list of project layer names
        
        :return list: project layers name
        """    
        lyrs = self.canvas.layers()
        return lyrs
    
    def GetLayerFields(self,layer) -> list:
        """GetLayerFields Get list of layer field names
        
        :param _type_ layer: layer name
        :return list: field names
        """  
        lyr  = self.instance.mapLayersByName(layer)[0]        
        fields =  lyr.fields()
        return fields
    
    def GetUniqueValues(self,layer:str,index:int):
        """GetUniqueValues returns list of unique values

        _extended_summary_

        :param str layer: layer's name
        :param str field: field's name
        :return _type_: uniques values list
        """     
        lyr = self.instance.mapLayersByName(layer)[0]
        values = lyr.uniqueValues(index)
        return values
    
    def SelectFeaturesByExpression(self,layer:str,expression:str,zoom:bool=False): 
        lyr = self.instance.mapLayersByName(layer)[0]
        lyr.selectByExpression(expression)
        if zoom: 
            iface.actionZoomToSelected().trigger()
    
    def FilterFeaturesByExpression(self,layer:str,expression:str,zoom:bool=True): 
        lyr = self.instance.mapLayersByName(layer)[0]
        lyr.setSubsetString(expression)
        if zoom: 
            iface.setActiveLayer(lyr)
            iface.zoomToActiveLayer()
        
        
        
    
     