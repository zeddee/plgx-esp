
import { Component, OnInit,ViewChild, AfterViewInit } from '@angular/core';
import { CommonapiService } from '../../dashboard/_services/commonapi.service';
import { JsonEditorComponent, JsonEditorOptions } from 'ang-jsoneditor';
import { FormControl, FormGroup, FormBuilder, Validators, FormArray } from '@angular/forms';
import { timer } from 'rxjs'
// import swal from 'sweetalert2';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-config',
  templateUrl: './config.component.html',
  styleUrls: ['./config.component.css', './config.component.scss']
})
export class ConfigComponent implements OnInit{
  @ViewChild(JsonEditorComponent, { static: true }) editor: JsonEditorComponent;
  public editorOptions: JsonEditorOptions;
  options = new JsonEditorOptions();
  configsform: FormGroup;
  uploaded_data:any;
  updateconfigObj:any;
  Updated = false;
  config_updatedata:any;
  submitted = false;
  tab : any = 'tab1';
  tab1 : any
  tab2 : any
  tab3 : any
  tab_shallow:any='tab11';
  tab11:any
  Clicked : boolean
  public config: any;
  public config_data: any = [];
  public filters={};
  public json_data:any;
  public dict_data_to_api:any={};
  public result:any;
  id="showbutton";
  error:any;
  platform_d:any;
  shallow_status:any;
  deep_status:any;
  shallow_deep_id_button:any;
  update_shallow_deep_data={};
  constructor(
    private fb: FormBuilder,
      private commonapi: CommonapiService
   ) {
    this.options.mode = 'code';
    this.options.modes = ['code', 'text', 'tree', 'view'];
    this.options.onChange = () =>this.dict_data_to_api['filters']=this.editor.get();
    }
toggle:boolean=false;
showDataAsPerPlatformSelection(config_queries,filter_val,platform_name,arch_of_platform,type_f_platform,status){
  if(platform_name=="windows" && arch_of_platform=="x86_64"){
    this.id="showbutton";
    this.tab_shallow = 'tab11'
    this.platform_d=type_f_platform
    if (this.platform_d=='shallow'){
     this.shallow_deep_id_button='shallow'
    }
    if (this.platform_d=='deep'){
      this.shallow_deep_id_button='deep'
    }
  }
  else{
    this.id="notshowbutton"
  }
 
  this.config_data = config_queries;
  this.toggle=false;
  // setTimeout(()=>{
  this.filters=filter_val;
  console.log("this.filters",this.filters)
  this.dict_data_to_api['platform']=platform_name;
  this.dict_data_to_api['queries']=this.config_data;
  this.dict_data_to_api['filters']=this.filters;
  this.dict_data_to_api['arch']=arch_of_platform;
  this.dict_data_to_api['type']=type_f_platform;
  this.toggle=true;
// }, 100);
}
ngOnInit() {
  this.toggle=false;
  // setTimeout(()=>{
    this.commonapi.configs_api().subscribe((res: any) => {
        this.config = res;
        console.log(this.config,"this.config")
        this.editorOptions = new JsonEditorOptions();
        this.editorOptions.mode = 'code';
        this.editorOptions.modes = ['code', 'text', 'tree', 'view'];
        this.config_data = this.config.data.windows.x86_64['1']['queries'];
        if(this.config_data!==''){
          $('.config_body').show();
          $('.config_body2').hide();
        }
        this.filters=this.config.data.windows.x86_64['1']['filters'];
        this.dict_data_to_api['platform']='windows';
        this.dict_data_to_api['queries']=this.config_data;
        this.dict_data_to_api['filters']=this.filters;
        this.dict_data_to_api['type']='shallow';
        this.platform_d="shallow"
        this.shallow_status=this.config.data.windows.x86_64['1']['status'];
        this.deep_status=this.config.data.windows.x86_64['2']['status'];
        this.shallow_deep_id_button='shallow'
      
        this.toggle=true;
  });
// }, 100);
}
public setTreeMode() {
   this.editor.setMode('code');
 }
onSubmit(){
  Swal.fire({
    title: 'Are you sure want to update?',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#518c24',
    cancelButtonColor: '#d33',
    confirmButtonText: 'Yes, Update!'
  }).then((result) => {
    if (result.value) {
    this.commonapi.config_upload(this.dict_data_to_api).subscribe(res=>{
    this.result=res;
    if(this.result && this.result.status === 'failure'){
      Swal.fire({
      icon: 'warning',
      title: this.result.status,
      text: this.result.message,
      
      })
    }else{  
      this.error = null;
      if (this.Updated != true){
          Swal.fire({
            title: 'Updating...',
            allowEscapeKey: false,
            allowOutsideClick: false,
            timer: 1000,    
            onOpen: () => {     
              Swal.showLoading( );
              this.commonapi.configs_api().subscribe((res: any) => {
                this.config = res;
              })
            }     
      
    }).then((result) => { 
            Swal.fire({
              icon: 'success',
              title: "successfully updated the config",
              allowOutsideClick: false,
              allowEscapeKey: false,
              allowEnterKey: false,
              showConfirmButton: false,
              timer: 1000, 
                
          })
        })
     } 
    }
  },
  error => {
  console.log(error);
  }
)
}
})
}

get_changed_data(changed_data){
    this.dict_data_to_api['queries']=changed_data;
    console.log(this.dict_data_to_api)
    }

onClick(check){
    if(check==1){
      this.tab = 'tab1';
    }else if(check==2){
      this.tab = 'tab2';
    }else if(check==3){
      this.tab = 'tab3';
     }else{
       this.tab = 'tab4';
     }
     }

   
     onClick_1(check_1){
    if(check_1==1){
      this.tab_shallow = 'tab11';
    }else if(check_1==2){
      this.tab_shallow= 'tab12';
    }
     }
    
     update_shallow_deep(platform,arch,type){
      this.update_shallow_deep_data['platform']=platform
      this.update_shallow_deep_data['arch']=arch
      this.update_shallow_deep_data['type']=type
      if(type=='shallow'){
        this.shallow_status=true
        this.deep_status=false
      }
      if(type=='deep'){
        this.deep_status=true
        this.shallow_status=false
      }
    //
      console.log(this.config," this.config",this.update_shallow_deep_data)
        this.commonapi.configs_api_shallow_deep_update(this.update_shallow_deep_data).subscribe(res=>{
              console.log("res") 
        })
      
     }

}




