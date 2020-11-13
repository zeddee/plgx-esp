import { AfterViewInit,Component, OnInit,ViewChild } from '@angular/core';
import { FormControl, FormGroup, FormBuilder, Validators, FormArray } from '@angular/forms';
import { Location } from '@angular/common';
import { DataTableDirective } from 'angular-datatables';
import { Subject } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Subscription } from 'rxjs';
import {NgDatepickerModule, DatepickerOptions} from 'ng2-datepicker';
import {NgModule} from '@angular/core';
import { HttpClient } from '@angular/common/http';


class DataTablesResponse {
  data: any[];
  draw: number;
  recordsFiltered: number;
  recordsTotal: number;
}
@Component({
  selector: 'app-hunt',
  templateUrl: './hunt.component.html',
  styleUrls: ['./hunt.component.css']
})
@NgModule({
  imports: [
    NgDatepickerModule
  ],

})
export class HuntComponent implements AfterViewInit,OnInit {
  @ViewChild(DataTableDirective, {static: false})
  dtElement: DataTableDirective;
  dtTrigger: Subject<any> = new Subject();
  dtOptions: DataTables.Settings = {};
  md5form: FormGroup;
  loading = false;
  submitted = false;
  indicator_file:File;
  indicator:any;
  dropdownPacknameList = [];
  selectedPacknameItems = [];
  dropdownPacknameSettings = {};
  huntObj = {};
  search_data_output:any
  myjson: any = JSON;
  datepicker_date = {};
  constructor(
    private fb: FormBuilder,
    private _location: Location,
    private http: HttpClient
  ) { }

  ngOnInit() {
    this.dropdownPacknameList = [
      {"id":"md5","itemName":"MD5"},
      {"id":"sha256","itemName":"SHA256"},
      {"id":"domain_name","itemName":"Domain Name"},
      {"id":"ja3_md5","itemName":"Certificates"},
    ];
    this.dropdownPacknameSettings = {
      singleSelection: true,
      text:"Select Hunt Type",
      selectAllText:'Select All',
      unSelectAllText:'UnSelect All',
      enableSearchFilter:true,
      lazyLoading: false,
      classes: "angular-multiselect-class",
      searchPlaceholderText: "Search Hunt Type here.."
    };

    this.md5form= this.fb.group({
      indicator_file: [''],
      hunt_type:['',Validators.required]
    });

    $('.table_data').hide();
    this.getDate()
  }
  get f() { return this.md5form.controls; }


  uploadFile(event){
    if (event.target.files.length > 0) {
      this.indicator_file = event.target.files;
      this.indicator=event.target.files

      }

  }
onSubmit(){
  this.submitted = true;
  if(this.f.hunt_type.value !=null){
    this.huntObj= {   
      "hunt_type":this.f.hunt_type.value[0].id,
      }
  }
  if (this.md5form.invalid) {
      return;
  }
  this.loading = true;
  this.indicator=this.indicator_file;
  if(this.indicator==undefined){
   alert("No valid indicators provided")
    this.loading = false;
  }else{
  this.Rerender_datatable()
  $("#table_noresults").hide()
  $('.table_data').show();
  }
}



goBack(){
  this._location.back();
}
onItemSelect(item:any){
  console.log(this.selectedPacknameItems);
}
OnItemDeSelect(item:any){
  console.log(this.selectedPacknameItems);
}
onSelectAll(items: any){
  console.log(items);
}
onDeSelectAll(items: any){
  this.md5form.controls['hunt_type'].reset()
}
get_dtOptions( ){
  this.dtOptions = {
    pagingType: 'full_numbers',
    pageLength: 10,
    serverSide: true,
    processing: true,
    searching: false,
    "language": {
      "search": "Search: "
    },
    ajax: (dataTablesParameters: any,callback) => {
      var body = dataTablesParameters;
      var uploadData = new FormData();
      if(this.indicator_file !=undefined){    
          uploadData.append('indicator_type', this.huntObj['hunt_type']);
          uploadData.append('file', this.indicator_file[0], this.indicator_file[0].name);
          uploadData.append('start', dataTablesParameters.start);
          uploadData.append('limit', body['length']);
          uploadData.append('date', this.datepicker_date['date']);
          uploadData.append('duration', this.datepicker_date['duration']);
      }else{
        return
      }
      this.http.post<DataTablesResponse>(environment.api_url + "/indicators/upload", uploadData, {
        headers: {
          // 'Content-Type': 'multipart/form-data',
          'x-access-token': localStorage.getItem('JWTkey')
        }
      }).subscribe(res => { 
        this.loading = false
        if(res['status']=='success'){
          this.search_data_output=res.data['results']  
          if(res.data['count'] > 0 && res.data['results'] != undefined)
          {
            $('.dataTables_paginate').show();
            $('.dataTables_info').show();
            $('.dataTables_filter').show()
            $("#table_noresults").hide()
          }
          else{
            $('.dataTables_paginate').hide();
            $('.dataTables_info').hide();
            $("#table_noresults").show()
      
          } 
          callback({
            recordsTotal: res.data['count'],
            recordsFiltered: res.data['count'],
            data: []
          });
        }  
      });
    },
    ordering: false,
    columns: [{data: 'hostname'}]
  }  
}
ngAfterViewInit(): void {
  this.dtTrigger.next();
}
ngOnDestroy(): void {
  this.dtTrigger.unsubscribe();
}
Rerender_datatable(){
  this.dtElement.dtInstance.then((dtInstance: DataTables.Api) => {
    // Destroy the table first
    dtInstance.destroy();
    // Call the dtTrigger to rerender again
    this.dtTrigger.next();
  });
}
getDate() {
  var today = new Date();
  var date = today.getFullYear() + '-' + (today.getMonth() + 1) + '-' + today.getDate();
  this.datepicker_date['date']=date;
  this.datepicker_date['duration']=3;
  this.getconverted_date()
  this.get_dtOptions()
  
}
getconverted_date() {
  var date =  this.datepicker_date['date'];
  if(date instanceof Date){
    date=this.convertDate(date);
    this.datepicker_date['date']=date
  }
}
myHandler(){
  this.getconverted_date()
  this.Rerender_datatable()
}
convertDate(date) {
  var  mnth = ("0" + (date.getMonth() + 1)).slice(-2),
    day = ("0" + date.getDate()).slice(-2);
  return [date.getFullYear(), mnth, day].join("-");
}
get_duration(duration_period){
  this.datepicker_date['duration']=duration_period
this.Rerender_datatable()
}
action(event): void {
  event.stopPropagation();
}
}


