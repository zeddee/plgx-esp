import { Component, OnInit } from '@angular/core';
import { CommonapiService } from '../../dashboard/_services/commonapi.service';
import { Router, ActivatedRoute } from '@angular/router';
import { FormControl, FormGroup, FormBuilder, Validators, FormArray } from '@angular/forms';
import swal from 'sweetalert';


@Component({
selector: 'app-packs',
templateUrl: './packs.component.html',
styleUrls: ['./packs.component.scss']
})
export class PacksComponent implements OnInit {
    packsfile: FormGroup;
    public pack: any;
    first_pack : any = [];
    pack_data: any = [];
    dataval:any;
    pack_query_name:any;
    searchText:any;
    term:any;
    packs:File;
    submitted:any;
    pack_upload:any;
    category:any;
    selectedItem:any;
    result:any;
    error:any;
    Updated = false;
    pack_addtags_val:any;
    pack_removetags_val:any;
    queries_addtags_val:any;
    queries_removetags_val:any;
    updatepackObj= {};
    packs_category_dictionary = [];
    sorted_pack_data_name=[];


constructor(
private commonapi: CommonapiService,
private fb: FormBuilder,
private router: Router
) { }

clearValue:string = '';
clearInput() {
  this.clearValue = null;
}

getById(event, newValue,any){
    this.selectedItem = newValue;
    for(const i in this.pack.data.results){
        if (this.pack.data.results[i].name == any) {
            this.pack_data =this.pack.data.results[i]
        }
    }
}

getfirst_data(first_pack){
    this.pack_data = first_pack
    this.selectedItem = this.pack_data.name;
}

uploadFile(event){
    console.log(event);
    if (event.target.files.length > 0) {
        this.pack = event.target.files;
    }
}
deletePacks(pack_id, pack_name){
  swal({
    title: 'Are you sure?',
    text: "Want to delete the pack "+ pack_name+"!",
    icon: 'warning',
    buttons: ["Cancel", true],
    closeOnClickOutside: false,
    dangerMode: true,
    }).then((willDelete) => {
    if (willDelete) {
      this.commonapi.deleteApipacks(pack_id).subscribe(res =>{
        console.log(res);
        swal({
      icon: 'success',
      title: 'Deleted!',
      text: 'Pack has been deleted.',
      buttons: [false],
      timer: 2000
      })
      setTimeout(() => {
        this.packs_category_dictionary = [];
        this.ngOnInit();
        // this.dtElement.dtInstance.then((dtInstance: DataTables.Api) => {
        //   // Destroy the table first
        //   dtInstance.destroy();
        //   // Call the dtTrigger to rerender again
        //   this.dtTrigger.next();
        // });
      },300);
    })
  }
})
}


    pack_addTag(test,id){
      this.commonapi.packs_addtag_api(id,test.toString()).subscribe(res => {
        this.pack_addtags_val = res ;
      });
    }
    pack_removeTag(event,pack_id) {
      this.commonapi.packs_removetags_api(pack_id,event).subscribe(res => {
        this.pack_removetags_val = res ;
      });

    }
    queries_addTag(tags,query_id){
      this.commonapi.queries_addtag_api(query_id,tags.toString()).subscribe(res => {
        this.queries_addtags_val = res ;

      });
    }
    queries_removeTag(event,query_id) {
      this.commonapi.queries_removetags_api(query_id,event).subscribe(res => {
        this.queries_removetags_val = res ;

      });

    }

runAdHoc(queryId){
    this.router.navigate(["/live-queries/",queryId]);
}

ngOnInit() {

    this.packsfile = this.fb.group({
        pack: '',
        category:'General'
      });
    this.pack=this.packsfile.value.pack
    this.commonapi.packs_api().subscribe((res: any) => {
      
    this.pack = res;

    let dataval_sort=[];
    this.sorted_pack_data_name=[];
    $('.placeholder_event').hide();
    if( this.pack.data.count ==0){
      $('.no_data').append('No Packs Present')
    }else{
      
      $('.show_packs_data').show(); 

      for(const i in this.pack.data.results){
        let is_present = false;
        for(const j in this.packs_category_dictionary){
          if(this.pack.data.results[i].category == this.packs_category_dictionary[j]['category']){
            is_present = true;
            if(this.pack.data.results[i].name in this.packs_category_dictionary[j]['packs']){
              break;
            }else{
              this.packs_category_dictionary[j]['packs'].push(this.pack.data.results[i].name);
            }
          }
        }
        if(is_present == false){
          this.packs_category_dictionary.push({'category':this.pack.data.results[i].category, 'packs': [this.pack.data.results[i].name]});
        }
      }
  
      for(const item_index in this.packs_category_dictionary){
        this.packs_category_dictionary[item_index]['packs'] = this.getSortedPackArray(this.packs_category_dictionary[item_index]['packs']);
      }
  
      this.sorted_pack_data_name = this.packs_category_dictionary[0]['packs'];
  
      for(const i in this.pack.data.results){
          if (this.pack.data.results[i].name == this.packs_category_dictionary[0]['packs'][0]){
              this.getfirst_data(this.pack.data.results[i]);
          }
      }
    }
   
  }
);

}
get f() { return this.packsfile.controls; }



onSubmit() {
  if (this.pack[0]==null){
    swal(
      "Please select a file for upload"
    )
  }

    this.category = this.packsfile.value.category;
    this.submitted = true;
    if (this.packsfile.invalid) {
        return;
    }

  this.commonapi.pack_upload_api(this.pack, this.category).subscribe(res =>{
    this.result=res;
    if(this.result && this.result.status === 'failure'){
        swal({
        icon: 'warning',
        title: this.result.status,
        text: this.result.message,

        })
        this.clearInput()

    }else{
        swal({
        icon: 'success',
        title: this.result.status,
        text: this.result.message,
        buttons: [false],
        timer: 2000
        })
    this.error = null;
    this.Updated = true;

    }
    setTimeout(() => {
      this.ngOnInit()
    },1000)
    },
    error => {
    console.log(error);
    })
}

redirect(pack) {
    console.log(pack);
    this.router.navigate(['/tag']);
}

getSortedPackArray(list){
  let  pack_names = [];
  let  pack_names_lowercase = [];
  let pack_name_sorted_list = [];
  let list_to_return = [];
  for(const pack_name_index in list){
    pack_names_lowercase.push(list[pack_name_index].toLowerCase());
  }
  pack_name_sorted_list  = pack_names_lowercase.sort();
  pack_name_sorted_list = pack_name_sorted_list.filter((el, i, a) => i === a.indexOf(el))

  for(const index in pack_name_sorted_list){
    for(const index2 in list){
      if(pack_name_sorted_list[index]==list[index2].toLowerCase()){
        list_to_return.push(list[index2]);
      }
    }
  }
  list_to_return = list_to_return.filter((el, i, a) => i === a.indexOf(el))

  return list_to_return
}


}
