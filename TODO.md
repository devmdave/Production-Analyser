# Refactoring TODO List

## Step 1: Create New Directory Structure
- [ ] Create `gui/` directory
- [ ] Create `gui/dialogs/` directory
- [ ] Create `gui/layouts/` directory
- [ ] Create `gui/widgets/` directory
- [ ] Create `plc/` directory
- [ ] Create `plc/mock_plc_server/` directory
- [ ] Create `config/` directory
- [ ] Create `data/backups/` directory
- [ ] Create `assets/` directory
- [ ] Create `tests/` directory

## Step 2: Move Files to New Locations
- [ ] Move `test.py` to root (already there, but will be updated)
- [ ] Move `Dialog.py` to `gui/dialogs/dialog.py`
- [ ] Move `custom_listview_dialog.py` to `gui/dialogs/custom_listview_dialog.py`
- [ ] Move `custom_tag_view.py` to `gui/dialogs/custom_tag_view.py`
- [ ] Move `OEE_config_dialog.py` to `gui/dialogs/oee_config_dialog.py`
- [ ] Move `dashboard_parameter_manager.py` to `gui/dialogs/dashboard_parameter_manager.py`
- [ ] Move `TagManager.py` to `gui/dialogs/tag_manager.py`
- [ ] Move `TipDressTagManager.py` to `gui/dialogs/tip_dress_tag_manager.py`
- [ ] Move `Layouts.py` to `gui/layouts/layouts.py`
- [ ] Move `fault_delay_layout.py` to `gui/layouts/fault_delay_layout.py`
- [ ] Move `tipdress_layout.py` to `gui/layouts/tipdress_layout.py`
- [ ] Move `summary_card.py` to `gui/widgets/summary_card.py`
- [ ] Move `Graph.py` to `gui/widgets/graph.py`
- [ ] Move `GraphCopy.py` to `gui/widgets/graph_copy.py`
- [ ] Move `my_plc.py` to `plc/my_plc.py`
- [ ] Move `MockPLCServer/mock_plc.py` to `plc/mock_plc_server/mock_plc.py`
- [ ] Move `oee_calculator.py` to `plc/oee_calculator.py`
- [ ] Move `oeecalc_cl.py` to `plc/oeecalc_cl.py`
- [ ] Move `json_reader.py` to `plc/json_reader.py`
- [ ] Move `tag_read.py` to `plc/tag_read.py`
- [ ] Move `write_at_time.py` to `plc/write_at_time.py`
- [ ] Move `config.json` to `config/config.json`
- [ ] Move `oee_config.json` to `config/oee_config.json`
- [ ] Move `tags.json` to `config/tags.json`
- [ ] Move `plc_custom_user_tags/` to `config/plc_custom_user_tags/`
- [ ] Move backup directories to `data/backups/`
- [ ] Move `icon.png` and `logo.PNG` to `assets/`

## Step 3: Extract Dashboard Class
- [ ] Extract `Dashboard` class from `test.py` to `gui/dashboard.py`
- [ ] Update `test.py` to import `Dashboard` from `gui.dashboard`

## Step 4: Update Import Statements
- [ ] Update imports in `test.py`
- [ ] Update imports in all moved files to reflect new paths
- [ ] Update any relative imports to absolute or proper relative paths

## Step 5: Update Hardcoded Paths
- [ ] Update paths for config files (e.g., `plc_custom_user_tags/dashboard_tags.json` to `config/plc_custom_user_tags/dashboard_tags.json`)
- [ ] Update paths for backup directories (e.g., `CycleTimeBackup` to `data/backups/CycleTimeBackup`)
- [ ] Update paths for assets (e.g., `icon.png` to `assets/icon.png`)

## Step 6: Testing and Verification
- [ ] Run the application to ensure it launches correctly
- [ ] Verify all dialogs and layouts work
- [ ] Check PLC communication and data loading
- [ ] Ensure no import errors or path issues

## Step 7: Cleanup
- [ ] Remove old files after successful move
- [ ] Update any documentation if needed
