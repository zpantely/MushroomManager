import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap

from manager import Manager
from instruments import Mode, State
from manager import GrowStage

UPDATE_INTERVAL = 1000 #ms

HEADER_SS = "QLabel {font: normal bold 14pt; padding: 0px}"

def launch_gui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Mushroom Monitor")
        self.resize(500,400)
        self.create_tabs()
        self.run_gui()
        self.update()
        
    def run_gui(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(UPDATE_INTERVAL)
            
    def update(self):
        #get all sensor data and update the sensor ui
        humidity = Manager().instance.humidity_sensor.get_value()
        temperature = Manager().instance.thermometer.get_value()
        c02 = Manager().instance.co2_sensor.get_value()
        
        self.sensor_ui_list[0].set_text(humidity)
        self.sensor_ui_list[1].set_text(temperature)
        self.sensor_ui_list[2].set_text(c02)
        
        #send sensor measurements to the instruments to determine if they should run
        Manager().instance.humidifier.update(Manager().instance.grow_stage, humidity) #humidifier
        Manager().instance.light.update(Manager().instance.grow_stage) #light
        Manager().instance.fan.update(Manager().instance.grow_stage, c02) #fan
        
        for inst in self.instrument_ui_list:
            self.update_instrument_state(inst)
        
        water_present = Manager().instance.humidifier.get_water_present()
        self.update_water_present(water_present)
    
    def update_instrument_state(self, instrument_ui):
        instrument_ui.set_state("ON" if instrument_ui.instrument.get_state() == State.on else "OFF")
    
    def create_tabs(self):
        self.tabs = QTabWidget()
        self.dashboard_tab = QWidget()
        self.plot_tab = QWidget()
        self.camera_tab = QWidget()
        self.tabs.addTab(self.dashboard_tab,"Dashboard")
        self.tabs.addTab(self.plot_tab,"Plot")
        self.tabs.addTab(self.camera_tab,"Camera")
        self.setCentralWidget(self.tabs)
        
        self.create_dashboard_tab()
        self.create_plot_tab()
        self.create_camera_tab()
    
    def create_dashboard_tab(self):
        dashboard_tab_layout = QVBoxLayout(self.dashboard_tab)
        snapshot_groupbox = QGroupBox("Snapshot")
        control_panel_groupbox = QGroupBox("Control Panel")
        gbss = "QGroupBox { border: 1px solid gray; font: bold; padding: 13px 4px 4px 4px; border-radius: 10px} QGroupBox:title { padding-left: 4px; padding-top: 2px; background-color: transparent }"
        snapshot_groupbox.setStyleSheet(gbss)
        control_panel_groupbox.setStyleSheet(gbss)
        dashboard_tab_layout.addWidget(snapshot_groupbox)
        dashboard_tab_layout.addWidget(control_panel_groupbox)
        snapshot_groupbox_layout = QVBoxLayout(snapshot_groupbox)
        control_panel_groupbox_layout = QHBoxLayout(control_panel_groupbox)
        
        #create upper / lower groupboxes for the snapshot section
        #snapshot_groupbox_layout = QHBoxLayout(snapshot_groupbox)
        snapshot_upper_groupbox = QGroupBox()
        snapshot_lower_groupbox = QGroupBox()
        snapshot_upper_groupbox_layout = QHBoxLayout(snapshot_upper_groupbox)
        snapshot_lower_groupbox_layout = QHBoxLayout(snapshot_lower_groupbox)
        snapshot_groupbox_layout.addWidget(snapshot_upper_groupbox)
        snapshot_groupbox_layout.addWidget(snapshot_lower_groupbox)
        gbss = "QGroupBox { border: 0px; padding: 0px 0px 0px 0px }"
        snapshot_upper_groupbox.setStyleSheet(gbss)
        snapshot_lower_groupbox.setStyleSheet(gbss)
        
        # Set both groupboxes to be equal in size
        sp = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sp.setVerticalStretch(1)
        snapshot_groupbox.setSizePolicy(sp)
        control_panel_groupbox.setSizePolicy(sp)
        
        #add widgets to the snapshot box
        self.sensor_ui_list = []
        for snsr in Manager().instance.sensor_list:
            snapshot_upper_groupbox_layout.addWidget(self.create_sensor_groupbox(snsr))
        self.water_present_label = QLabel("Humidifer Water Level: Good")
        snapshot_lower_groupbox_layout.addWidget(self.water_present_label)
        snapshot_lower_groupbox_layout.setAlignment(Qt.AlignCenter)
#         lss = "QLabel {font: normal bold 12pt; }"
#         self.water_level_label.setStyleSheet(lss)
        
        #add widgets to the control panel box
        self.instrument_ui_list = []
        for inst in Manager.instance.instrument_list:
            control_panel_groupbox_layout.addWidget(self.create_instrument_groupbox(inst))
        control_panel_groupbox_layout.addWidget(self.create_grow_state_groupbox())
        
    class Sensor_UI():
        def __init__(self, sensor, measurement_label):
            self.sensor = sensor
            self.measurement_label = measurement_label
        def set_text(self, val):
            self.measurement_label.setText('    ' + str(val) + ' '  + self.sensor.unit)
            
    def create_sensor_groupbox(self, sensor):
        groupbox = QGroupBox()
        gbss = "QGroupBox { border: 0px none; }"
        groupbox.setStyleSheet(gbss)
        
        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignCenter) #why dont this work
        measurement_name_label = QLabel(sensor.measurement_name + ":")
        measurement_name_label.setStyleSheet(HEADER_SS)
        vbox.addWidget(measurement_name_label)
        measurement_label = QLabel("       ???")
        mlss = "QLabel {font: normal normal 12pt; }"
        measurement_label.setStyleSheet(mlss)
        vbox.addWidget(measurement_label)
        #vbox.addStretch(1)
        groupbox.setLayout(vbox)
        
        self.sensor_ui_list.append(self.Sensor_UI(sensor, measurement_label))
        
        return groupbox
    
    def update_water_present(self, is_present):
        if is_present:
            self.water_present_label.setText("Humidifier Water Level: Good")
            lss = "QLabel {font: normal bold 14pt; color: green; }"
            self.water_present_label.setStyleSheet(lss)
        else:
            self.water_present_label.setText("Humidifier Water Level: Empty")
            lss = "QLabel {font: normal bold 14pt; color: red; }"
            self.water_present_label.setStyleSheet(lss)
    
    class Instrument_UI():
        def __init__(self, instrument, state_label):
            self.instrument = instrument
            self.state_label = state_label
        def set_state(self, state_string):
            self.state_label.setText('State: ' + state_string.upper())
    
    def create_instrument_groupbox(self, instrument):
        groupbox = QGroupBox()
        gbss = "QGroupBox { border: 0px none; }"
        groupbox.setStyleSheet(gbss)
        on_rb = QRadioButton("On")
        off_rb = QRadioButton("Off")
        auto_rb = QRadioButton("Auto")
        auto_rb.setChecked(True)
        rbss = "QRadioButton {font: normal normal 11pt; padding: 0px}"
        on_rb.setStyleSheet(rbss)
        off_rb.setStyleSheet(rbss)
        auto_rb.setStyleSheet(rbss)
        state_label = QLabel("State: ???")
        state_label.setStyleSheet(HEADER_SS)

        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignCenter)
        inst_label = QLabel(instrument.name)
        inst_label.setStyleSheet(HEADER_SS)
        vbox.addWidget(inst_label)
        vbox.addWidget(on_rb)
        vbox.addWidget(off_rb)
        vbox.addWidget(auto_rb)
        vbox.addWidget(state_label)
        groupbox.setLayout(vbox)
             
        instrument_ui = self.Instrument_UI(instrument, state_label)
        self.instrument_ui_list.append(instrument_ui)
        on_rb.toggled.connect(lambda: self.rb_toggled(on_rb, instrument_ui))
        off_rb.toggled.connect(lambda: self.rb_toggled(off_rb, instrument_ui))
        auto_rb.toggled.connect(lambda: self.rb_toggled(auto_rb, instrument_ui))
        
        return groupbox
    
    def rb_toggled(self, rb, instrument_ui):
        if not rb.isChecked():
            return
        if rb.text() == "On":
            instrument_ui.instrument.set_mode(Mode.on)
            self.update_instrument_state(instrument_ui)
        elif rb.text() == "Off":
            instrument_ui.instrument.set_mode(Mode.off)
            self.update_instrument_state(instrument_ui)
        elif rb.text() == "Auto":
            instrument_ui.instrument.set_mode(Mode.auto)
            
    def create_grow_state_groupbox(self):
        groupbox = QGroupBox()
        gbss = "QGroupBox { border: 0px none; }"
        groupbox.setStyleSheet(gbss)
        self.grow_stage_cb = QComboBox()
        self.grow_stage_cb.addItem("Colonization")
        self.grow_stage_cb.addItem("Incubation")
        self.grow_stage_cb.addItem("Fruiting")
        cbss = "QComboBox {font: normal normal 11pt; padding: 0px}"
        self.grow_stage_cb.setStyleSheet(cbss)
        self.grow_stage_cb.currentIndexChanged.connect(lambda: self.update_combo_box())

        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignCenter)
        grow_stage_label = QLabel("Grow Stage")
        grow_stage_label.setStyleSheet(HEADER_SS)
        vbox.addWidget(grow_stage_label)
        vbox.addWidget(self.grow_stage_cb)
        groupbox.setLayout(vbox)
                                   
        return groupbox
    
    def update_combo_box(self):
        if self.grow_stage_cb.currentText() == "Colonization":
            Manager().instance.set_grow_stage(GrowStage.colonization)
        elif self.grow_stage_cb.currentText() == "Incubation":
            Manager().instance.set_grow_stage(GrowStage.incubation)
        elif self.grow_stage_cb.currentText() == "Fruiting":
            Manager().instance.set_grow_stage(GrowStage.fruiting)
    
    def create_plot_tab(self):
        pass
    
    def create_camera_tab(self):
        camera_tab_layout = QVBoxLayout(self.camera_tab)
        self.photo_groupbox = QGroupBox()
        control_groupbox = QGroupBox()
        gbss = "QGroupBox { border: 1px solid gray; font: bold; padding: 0px 0px 0px 0px; } QGroupBox:title { padding-left: 4px; padding-top: 2px; background-color: transparent }"
        self.photo_groupbox.setStyleSheet(gbss)
        #control_groupbox.setStyleSheet(gbss)
        camera_tab_layout.addWidget(self.photo_groupbox)
        camera_tab_layout.addWidget(control_groupbox)
        photo_groupbox_layout = QHBoxLayout(self.photo_groupbox)
        control_groupbox_layout = QHBoxLayout(control_groupbox)
        photo_groupbox_layout.setContentsMargins(0,0,0,0)
        
        self.photo_label = QLabel()
        self.refresh_preview_photo()
        photo_groupbox_layout.addWidget(self.photo_label)

        btn = QPushButton("Refresh")
        btn.clicked.connect(self.refresh_preview_photo)
        control_groupbox_layout.addWidget(btn)
        
    def refresh_preview_photo(self):
        Manager().instance.camera.snap_preview()
        img = QPixmap("./photos/last.jpg")
        img_scaled = img.scaledToWidth(self.photo_groupbox.width())
        self.photo_label.setPixmap(img_scaled)
    
    def closeEvent(self, event):
       Manager().instance.shutdown()

