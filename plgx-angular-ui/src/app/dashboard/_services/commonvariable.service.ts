import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class CommonVariableService {
  APP_NAME="EclecticIQ"
  Version="CE 3.0"
  version_in_readme_content="2.1.2"
  Windows_plgx_cpt_exe={'version':"v1.0.40.5","MD5_checksum":"7f1d5a8ff24f95d9073839a09d0630f2"}
  Linux_plgx_cpt={'version':"v1.0.40.2","MD5_checksum":"2548cf04e338dfedf90aba2de1b07eb0"}
  Darwin_plgx_cpt_sh={'version':"-","MD5_checksum":"4899f3b203d63acef7e5ac633660040d"}
  Windows_x64_plgx_osqueryd_exe={'version':"4.0.2","MD5_checksum":"2c0214270213dcc71a103aed12c8c154"}
  Windows_x64_plgx_win_extension_ext_exe={'version':"v1.0.40.5","MD5_checksum":"eac436b0088acc1daf577f5666755fb9"}
  Windows_x86_plgx_osqueryd_exe={'version':"3.2.6","MD5_checksum":"a16a1063fdfa605572798b8d4602a23b"}
  Linux_plgx_osqueryd={'version':"4.3.0","MD5_checksum":"47bb0f8c8cafd1cc147b964a8d39b80c"}
  Linux_plgx_linux_extension_ext={'version':"v1.0.40.2","MD5_checksum":"121157d0db89c8fdb060d9bc3ea45743"}
  constructor() { }
}
