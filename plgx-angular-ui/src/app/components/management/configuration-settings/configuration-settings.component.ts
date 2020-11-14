import { Component, OnInit } from '@angular/core';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { CommonapiService } from '../../../dashboard/_services/commonapi.service';
import { CommonVariableService } from '../../../dashboard/_services/commonvariable.service';
import { Location } from '@angular/common';
import Swal from 'sweetalert2';
import { Title } from '@angular/platform-browser';

@Component({
  selector: 'app-configuration-settings',
  templateUrl: './configuration-settings.component.html',
  styleUrls: ['./configuration-settings.component.css']
})
export class ConfigurationSettingsComponent implements OnInit {
  ConfigureSettings: FormGroup;
  submitted = false;
  purge_data_duration:any;
  alert_aggregation_duration:any;
  constructor(
    private fb: FormBuilder,
    private commonapi:CommonapiService,
    private commonvariable: CommonVariableService,
    private _location: Location,
    private titleService: Title,
  ) { }

  ngOnInit() {
    this.titleService.setTitle(this.commonvariable.APP_NAME+"-"+"Configuration Settings");
    this.ConfigureSettings = this.fb.group({
      purged_data_value: ['', [Validators.required, Validators.min(Number.MIN_VALUE)]],
      alert_aggregation_value: ['', [Validators.required, Validators.min(Number.MIN_VALUE)]],
    });
    this.get_Platform_settings()
  }
  get_Platform_settings(){
    this.commonapi.getConfigurationSettings().subscribe(res => {
      this.purge_data_duration=res.data.purge_data_duration
      this.alert_aggregation_duration=res.data.alert_aggregation_duration
    });
  }
    get f() { return this.ConfigureSettings.controls; }
    onSubmit() {
      this.submitted = true;
      if (this.ConfigureSettings.invalid) {
        return;
      }
      else {
        Swal.fire({
          title: 'Are you sure want to update?',
          icon: 'warning',
          showCancelButton: true,
          confirmButtonColor: '#518c24',
          cancelButtonColor: '#d33',
          confirmButtonText: 'Yes, Update!'
        }).then((result) => {
          if (result.value) {
            this.commonapi.putConfigurationSettings(this.f.purged_data_value.value,this.f.alert_aggregation_value.value).subscribe(res => {
                if (res['status'] == 'success') {
                  Swal.fire({
                    icon: 'success',
                    title: res['status'],
                    text: res['message'],
                    timer: 2500,
                    showConfirmButton: false,
                  })
                  this.get_Platform_settings()
                } else {
                  Swal.fire({
                      icon: 'warning',
                      title: res['status'],
                      text: res['message'],
                    })
                }
              });
          }
        })
      }
    }
  goBack() {
    this._location.back();
  }
  clearForm() {
    this.submitted = false;
    this._location.back();
  }
}
