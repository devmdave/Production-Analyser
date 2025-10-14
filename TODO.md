# TODO: Create Fault Delay Window with Back Button

## Step 1: Modify fault_delay_layout.py
- Add back button to CurrentFaultDelay.__init__ layout (QPushButton("Back").clicked.connect(self.close)).
- Modify __init__ to accept optional file_path param (default today's fault files).
- Update load_data_to_view to use passed file_path if provided.

## Step 2: Modify test.py
- Import fault_delay_layout.
- Connect view_current_fault_action.triggered to show CurrentFaultDelay().
- Connect view_backup_fault_action.triggered to show file selection dialog (CustomListViewDialog with files from FaultDelayBackup/), then show CurrentFaultDelay(selected_file).

## Step 3: Test
- Run test.py, select Fault Delay > View Fault Delay (Current), verify window shows two tables with data, back button closes and returns to dashboard.
- Select View Fault Delay (Backup), verify file list, select file, window shows data from selected file.
