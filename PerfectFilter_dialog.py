# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PerfectFilterDialog
                                 A QGIS plugin
 This plugin offers a more intuitive way to filter information from one or more layers through a user friendly interface.

 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2022-10-09
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Francisco Contreras
        email                : franciscocontreras93@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from warnings import filterwarnings

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import pyqtSignal
from qgis.utils import iface
from qgis.core import * 
from PyQt5.QtWidgets import *

from .PerfectFilter_functions import PerfectFilterFunctions







# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'PerfectFilter_dialog_base.ui'))


class PerfectFilterDialog(QDialog, FORM_CLASS):
    closingPlugin = pyqtSignal()
    def __init__(self, parent=None):
        """Constructor."""
        super(PerfectFilterDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        
        self.functions = PerfectFilterFunctions() # PyQGIS functions
        self.setupUi(self)
        self.uiComponents()
        
        self.fields = None
        
        self.layer = None
        
        
        self.rules = list()
        
    
    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
    
    def uiComponents(self): 
        """  Function to create and manipulate UI widgets
        """        
        self.cmb_layers.addItem('Seleccionar capa...')
        self.ProjectLayers()
        self.cmb_layers.currentTextChanged.connect(self.LayerFields)
        self.cmb_fields.currentIndexChanged.connect(self.UniquesValues)
        
        # self.value_list.itemSelectionChanged.connect(self.GetSelectedValues)
        
        self.createRule_btn.clicked.connect(self.SetFilterRule)
        
        self.removeRule_btn.clicked.connect(self.RemoveFilterRule)
        
        self.select_btn.clicked.connect(self.CreateSelection)
        
        self.filter_btn.clicked.connect(self.SetFilterToLayerProvider)

    def ProjectLayers(self):
        """ Function to automatically add the layers in the project to the corresponding combobox 
        """        
        lyrs = self.functions.GetProjectLayers()
        lyrs = [l.name() for l in lyrs]
        self.cmb_layers.addItems(lyrs)
    
    def LayerFields(self,layer:str):
        """ Function to automatically add the names of the fields of the selected layer.

        :param str layer: layer name
        """
        self.cmb_fields.clear()       
        try: 
            index = self.cmb_layers.currentIndex()
            if index > 0:
                self.fields  = self.functions.GetLayerFields(layer)
                fNames = [f.name() for f in self.fields]
                self.cmb_fields.addItems(fNames)
                self.layer = layer
            else:
                self.cmb_fields.clear()
                
        except Exception as ex: 
            QgsMessageLog.logMessage("Ocurrio Un error: {}".format(ex), level=2)
            
    def UniquesValues(self,index:int):
        """ Function to automatically add the unique values ​​of the selected field to the list widget
        
        :param int index: index of select field
        """        
        self.value_list.clear()
        try: 
            layer = self.cmb_layers.currentText()
            values = [str(v) for v in self.functions.GetUniqueValues(layer,index)]
            self.value_list.addItems(values)
            
            field = self.fields.field(index)
            if field.type() != 10 and len(values) > 1:
                minimum = min([float(v) for v in values if v != 'NULL'])
                maximum = max([float(v) for v in values if v != 'NULL'])
                self.range_check.setEnabled(True)
                
                self.min_spin.setValue(minimum)
                self.min_spin.setMinimum(minimum)
                self.min_spin.setEnabled(True)
                
                self.max_spin.setEnabled(True)
                self.max_spin.setValue(maximum)
                self.max_spin.setMaximum(maximum)
                
            else: 
                self.range_check.setEnabled(False)
                self.min_spin.setEnabled(False)
                self.max_spin.setEnabled(False)
                self.min_spin.setValue(0)
                self.max_spin.setValue(0)
                
        except Exception as ex: 
            QgsMessageLog.logMessage('Ocurrio un Error: {}'.format(ex))        
        
    def GetSelectedValues(self) -> list:
        """ Returns selected items from list widget

        :return list: item list
        """        
        selection = [item.text() for item in self.value_list.selectedItems()]
        return selection
    
    def SetFilterRule(self):
        """ Create rules to select of filter features. Trigger CheckOptions

        """        
        
        if self.strict_check.isChecked(): 
            logic_operator = 'and'
        else:
            logic_operator = 'or'
        selection = self.GetSelectedValues()
        field = self.cmb_fields.currentText()
        tree_node = QTreeWidgetItem(self.rules_tree,[self.layer])
        for e in selection:
            if e not in self.rules: 
                self.rules.append('''{}  "{}" = '{}' '''.format(logic_operator,field,e)) # must be equal as the QTreeWidgetItem
                tree_rule = QTreeWidgetItem(tree_node,['''{}  "{}" = '{}' '''.format(logic_operator,field,e)])
        self.CheckOptions()
        
    def CheckOptions(self):
        """ Checker for Options
        #* SELECCION Y FILTRADO AUTOMATICO
        """        
        if self.selection_check.isChecked():
            self.CreateSelection()
        elif self.filter_check.isChecked(): 
            self.SetFilterToLayerProvider()
        pass        
    
    def RemoveFilterRule(self):
        """ Remove rules from rules_tree, trigger CheckOptions

        _extended_summary_
        """
        #! BUG: 
        #! 1) AL ELIMINAR UN NODO DE REGLAS, ARROJA UN ERROR AL REMOVERLAS DE LA LISTA DE REGLAS (SELF.RULES)
        #! HAY QUE CONTROLAR EL ROOT DEL TREE WIDGET PARA OBTENER LOS HIJOS DEL NODO SUPERIOR. 
        
        #* AGREGADO EN RAMA RFR01
        
        
        root = self.rules_tree.invisibleRootItem() 
        selected = self.rules_tree.selectedItems()
        for item in selected: 
            (item.parent() or root).removeChild(item)
            
            self.rules.remove(item.text(0))
        self.CheckOptions()
            
            
    
          
    def CreateExpression(self) -> str:
        """ Create the QgsExpression

        

        :return str: QgsExpression to filter
        """        
        expression = ''
        # self.rules[0] = self.rules[0][3:] # modify first rule to delete logic_operator (or,and)
        # self.rules[-1] = self.rules[-1][3:] # modify last rule to delete logic_operator (or,and)
        for rule in self.rules: 
            expression = expression + ' ' + rule
        expression = expression[4:]
        return str(expression)
    
        
    def CreateSelection(self):
        """CreateSelection Select features by expression action

        """ 
                 
        lyr = self.cmb_layers.currentText()
        exp = self.CreateExpression()
        if self.zoom_check.isChecked():
            zoom = True
        else: 
            zoom = False
        
        self.functions.SelectFeaturesByExpression(lyr,exp,zoom)
        
    def SetFilterToLayerProvider(self):
        """ Set filter to provider
        """         
        lyr = self.cmb_layers.currentText() 
        exp = self.CreateExpression() 
        
        self.functions.FilterFeaturesByExpression(lyr,exp)
        
        
        
        
        
        
