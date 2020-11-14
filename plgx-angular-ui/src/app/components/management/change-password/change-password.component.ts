import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, FormBuilder, Validators, FormArray } from '@angular/forms';
import { timer } from 'rxjs'
import { CommonapiService } from '../../../dashboard/_services/commonapi.service';
import { CommonVariableService } from '../../../dashboard/_services/commonvariable.service';
import swal from 'sweetalert';
import { Location } from '@angular/common';
import { Title } from '@angular/platform-browser';
import Swal from 'sweetalert2';
@Component({
  selector: 'app-change-password',
  templateUrl: './change-password.component.html',
  styleUrls: ['./change-password.component.css']
})
export class ChangePasswordComponent implements OnInit {

  changePassword: FormGroup;
  submitted = false;
  error: any;
  Updated = false;
  result: any;
  existing_Password:any;
  new_Password:any;
  confirm_new_Password:any
  constructor(
    private fb: FormBuilder,
    private commonapi:CommonapiService,
    private commonvariable: CommonVariableService,
    private _location: Location,
    private titleService: Title,

  ) {   }

  ngOnInit() {
    this.titleService.setTitle(this.commonvariable.APP_NAME+"-"+"Change Password");
    this.changePassword= this.fb.group({
      existing_Password: '',
      new_Password: '',
      confirm_new_Password: ''
    });
  
  }

  get f() { return this.changePassword.controls; }

  onSubmit() {
    // TODO: Use EventEmitter with form value
    this.submitted = true;
    // this.Updated = true;
    if (this.f.existing_Password.value==undefined || this.f.new_Password.value==undefined || this.f.confirm_new_Password.value==undefined ||this.f.existing_Password.value=='' || this.f.new_Password.value=='' || this.f.confirm_new_Password.value=='') {
      console.log(this.f.existing_Password.value,this.f.new_Password.value)
      swal({
        icon: 'warning', 
        text:" Please provide  Existing Password/New Password/ Confirm New Password ",
    })
    }  else {
      Swal.fire({
        title: 'Are you sure want to update?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#518c24',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes, Update!'
      }).then((result) => {
        if (result.value) {
    this.commonapi.changePassword( this.f.existing_Password.value, this.f.new_Password.value, this.f.confirm_new_Password.value).subscribe(
      res => {
        this.result = res;
        if(this.result && this.result.status === 'failure'){
          swal({
            icon: 'warning',
            title: this.result.status,
            text: this.result.message,
          })
        }else{
          swal({
            icon: 'success',
            title: this.result.status,
            text: this.result.message,
            buttons: [false],
            timer: 2000
            
          })
    
        }
        setTimeout(() => {
          this.existing_Password=null,
          this.new_Password=null,
          this.confirm_new_Password=null
        }, 2000);
       
      },
      // error => {
      //   console.log(error);
      // }
    );
   }
    })
  }

  }
  goBack(){
    this._location.back();
   }

  // clearForm(){
  //   this.submitted = false;
  //   this._location.back();
  // }

}
