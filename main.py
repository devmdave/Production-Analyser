import sys
import time
import pandas as pd
import os
import datetime
import subprocess
import threading
from multiprocessing import Process
from pycomm3 import exceptions
from Layouts import MyWindow
from fault_delay_layout import CurrentFaultDelay
from my_plc import Plc
from PyQt5.QtWidgets import QApplication



class MyApplication(MyWindow):
    def __init__(self): 
        super().__init__()  
        self.main_window()
        self.plc_status = False
        self.view_current_fault_action.triggered.connect(lambda:self.show_fault_delay_layout())
        self.view_cycle_action.triggered.connect(lambda: self.cycletime_backup_layout())
        self.status_label.setText("Plc Status: Connecting....")
        self.status_label.setStyleSheet("color: #ffffff; background: #002A4D; border-radius:15px;padding: 8px; ")
        # reader_thread = threading.Thread(target=lambda: self.plc_connection())
        # reader_thread.start()
        
    def show_fault_delay_layout(self):
        self.fault_delay_layout = CurrentFaultDelay()
        self.fault_delay_layout.show()

    # def plc_connection(self):
    #     try:
    #         plc = Plc('192.168.0.10')
    #         conn_status = None
            
    #         while True:
    #             tags_data = plc.read_dashboard_tags()
    #             if tags_data:
    #                 self.card_prod.update_value(tags_data[plc.TOTAL_PRODUCTION_TAG])
    #                 #self.card_delay.update_value(tags_data[plc.TOTAL_DELAY_TAG])
    #                 self.card_shiftA.update_value(tags_data[plc.SHIFT_A_PRODUCTION])
    #                 self.card_shiftB.update_value(tags_data[plc.SHIFT_B_PRODUCTION])
    #                 #run when plc connection is done
    #                 # if conn_status==None or conn_status == False:
    #                 #     self.status_label.setText("Plc Status: Connected!")
    #                 #     self.status_label.setStyleSheet("color: #ffffff; background:lightgreen; border-radius:10px;padding: 8px; ")
    #                 #     conn_status = True
    #                 if conn_status==None or conn_status == False:
    #                     self.status_label.setText("Plc Status: Connected!")
    #                     self.status_label.setStyleSheet("color: #ffffff; background:lightgreen; border-radius:10px;padding: 8px; ")
    #                     conn_status = True
                         
    #             elif not tags_data:
    #                 if conn_status == None or conn_status == True:
    #                     #run when plc connection is failed 
    #                     self.status_label.setText("Plc Status: Not Connected!")
    #                     self.status_label.setStyleSheet("color: #ffffff; background: #FF0000; border-radius:10px; padding: 8px; ")
    #                     conn_status = False
                    
    #             time.sleep(60)
    #     except Exception as e:
    #         pass

 
def main():
    app = QApplication(sys.argv)
    viewer = MyApplication()
    viewer.show()
    sys.exit(app.exec_())

if __name__ == "__main__":


    main()