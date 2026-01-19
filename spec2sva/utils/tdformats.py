def wavedrom_to_json(wd_tds_info: dict) -> dict:
    ### Convert all timing diagrams in tds_info from WaveDrom format to JSON format ###
    
    def _valid_var_name(var: str) -> str:
        ### Convert a variable name to a valid identifier by replacing invalid characters with underscores ###
        
        return var.replace(' ', '_')
    
    def _wavelane_wd_to_js(wd_lane: dict, lane_id: int) -> dict:
        ### Convert a single wavelane from WaveDrom format to JSON format ###
        
        # { "name": "...", "values": [...] }
        js_lane = { 'name': wd_lane['name'] }

        js_values = []

        data_idx = 0
        tracked_val = ''
        for wd_val in wd_lane['wave']:
            match wd_val:
                case '0' | '1':
                    js_values.append(int(wd_val))
                    tracked_val = int(wd_val)
                case 'x':
                    js_values.append('X')
                    tracked_val = 'X'
                case '=':
                    if 'data' in wd_lane:
                        var = _valid_var_name(wd_lane['data'][data_idx])
                    else:
                        var = f'_var_{lane_id}_{data_idx}'
                    js_values.append(var)
                    tracked_val = var
                    data_idx += 1
                case '.':
                    js_values.append(tracked_val)
                # Unknown
                case _:
                    raise ValueError(f"Unsupported Wavedrom value: {wd_val}")
        
        js_lane['values'] = js_values

        return js_lane
    
    # { "signals": [...], "waveforms": [...] }
    js_tds_info = { 'signals': wd_tds_info['signals'] }
    
    js_waveform_list = []
    for wd_waveform in wd_tds_info['waveforms']:
        
        # { "name": "...", "signals": [...] }
        js_waveform = { 'name': wd_waveform['name'] }
        
        js_signal_list = []
        for lane_id, wd_signal in enumerate(wd_waveform['signal']):
            js_signal_list.append(_wavelane_wd_to_js(wd_signal, lane_id))
        
        js_waveform['signals'] = js_signal_list
        
        js_waveform_list.append(js_waveform)
        
    js_tds_info['waveforms'] = js_waveform_list
    
    return js_tds_info
