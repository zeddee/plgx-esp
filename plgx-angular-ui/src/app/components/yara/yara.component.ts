import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { FormControl, FormGroup, FormBuilder, Validators, FormArray } from '@angular/forms';
import { CommonapiService } from '../../dashboard/_services/commonapi.service';
import { HttpClient } from '@angular/common/http';
import swal from 'sweetalert';
import Swal from 'sweetalert2'
@Component({
  selector: 'app-yara',
  templateUrl: './yara.component.html',
  styleUrls: ['./yara.component.css']
})
export class YaraComponent implements OnInit {
  yarafile: FormGroup;
  yaras:any;
  yara_data:any;
  submitted:any;
  yara:any;
  yara_view:any;
  yara_title:any;
  yara_upload:any;
  yara_delete:any;
  constructor(
    private httpClient: HttpClient,
    private fb: FormBuilder,
    private commonapi:CommonapiService,
    private router: Router
  ) { }

  ngOnInit() {
    this.yarafile = this.fb.group({
      yara:''  
    });
    this.yara=this.yarafile.value.yara
    this.commonapi.yara_api().subscribe(res => {
      this.yaras = res ;
      this.yara_data = this.yaras.data;
      console.log(this.yaras);
    });
  }
  get f() { return this.yarafile.controls; }

  clearValue:string = '';
  clearInput() {
    this.clearValue = null;
  }
  
onFileSelect(event){
  console.log(event.target.files)
  if (event.target.files.length > 0) {
    this.yara = event.target.files;
    }   
}
onSubmit() {
  if (this.yara[0]==null  || this.yara ==''){
    swal(
      "Please select a yara file for upload"
    )
  }

  this.submitted = true;
    if (this.yarafile.invalid) {
    return;
    }
    
  this.commonapi.yara_add_api(this.yara).subscribe(res =>{
    this.yara_upload = res;
    // console.log(res);
    if(this.yara_upload && this.yara_upload.status === 'failure'){
      swal({
        icon: 'warning',
        title: this.yara_upload.status,
        text: this.yara_upload.message,
        
      })
      this.clearInput()
     
    }else{
      swal({
        icon: 'success',
        title: this.yara_upload.status,
        text: this.yara_upload.message,
        buttons: [false],
        timer: 2000
      })
      setTimeout(() => {
        this.ngOnInit()
      },1500);
    }    
		})
}
viewFile(event){
  var event_type = event.target.value;
  this.commonapi.yara_view_api(event_type).subscribe(res => {
      this.yara_view = res;
      this.yara_title = event.target.value;;
    })
}
deleteFile(event){
    console.log(event.target.value);
    var yara_name = event.target.value;
  //   swal({
  //   title: 'Are you sure?',
  //   text: "You won't be able to revert this!",
  //   icon: 'warning',
  //   buttons: ["cancel", "Yes, delete it!"],
  //   dangerMode: true,
  //   closeOnClickOutside: false

  // }).then((willDelete) => {
  // if (willDelete) {
    Swal.fire({
      title: 'Are you sure?',
      text: "You won't be able to revert this!",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#518c24',
      cancelButtonColor: '#d33',
      confirmButtonText: "Yes, delete it!"
    }).then((result) => {
      if (result.value) {
    this.commonapi.yara_delete_api(yara_name).subscribe(res=>{
      this.yara_delete = res;
      swal({
        icon: 'success',
        title: 'Deleted!',
        text: '',
        buttons: [false],
        timer: 2000
        })
    setTimeout(() => {
      this.ngOnInit()
    },2100);
     
  })
  }
})
}
}

