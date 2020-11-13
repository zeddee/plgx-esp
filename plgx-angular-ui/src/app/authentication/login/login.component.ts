import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, FormBuilder, Validators } from '@angular/forms';
import { FormArray } from '@angular/forms';
import { Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';

import { loginService } from './login.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  loading = false;
  submitted = false;
  data: any;
  error: string;

  constructor(
    private router: Router,
    private _loginService: loginService,
    private toastr: ToastrService
  ) { }

  ngOnInit() { }

  credentials = {
    username: "",
    password: "",
  }

  onSubmit(object) {
    console.log(object)
    if (object.value.username == "" || object.value.username == null) {
			this.toastr.warning('Please enter Username!!');
		}
		else if (object.value.password == "" || object.value.password == null) {
			this.toastr.warning('Please enter Password!!');
		}
		else {
    this.submitted = true;
    this.loading = true;

    setTimeout(()=>{
      this.loading = false;
    }, 30000);

    this._loginService.login(object).subscribe(
      response => {
        var temp = response;
        this.loading = false;
        if(temp.token){
          this.data = temp.token;
          localStorage.setItem('currentUser', JSON.stringify(response));
          localStorage.setItem('JWTkey', this.data);
          this.router.navigate(['/manage']);
          this.toastr.success('Welcome Admin');
        }else{
          this.error = 'Invalid Username or Password';
        }
      },
      error => {
        this.error = 'Something went wrong! Please try again';
        this.loading = false;
      })
    }
  }
}
