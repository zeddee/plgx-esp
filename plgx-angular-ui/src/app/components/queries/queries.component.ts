
import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import {CommonapiService} from '../../dashboard/_services/commonapi.service';
import swal from 'sweetalert';
import { ThrowStmt } from '@angular/compiler';

@Component({
  selector: 'app-queries',
  templateUrl: './queries.component.html',
  styleUrls: ['./queries.component.scss']
})
export class QueriesComponent implements OnInit {
  id:any;
  sub:any;
  public queries: any;
  query_data: any;
  first_query : any = [];
  // dataval:any;
  queryid:any;
  term:any;
  query_tags_val:any;
  associated_data:any;
  dataval_packs:any;
  dataval_all:any;
  show=false;
  searchText:any;
  selectedItem:any;
  queries_addtags_val:any;
  queries_removetags_val:any;
  sorted_pack_data_name_id=[];
  first_data:any;
  id_to_get_particular_queries:any;
  constructor(
    private _Activatedroute:ActivatedRoute,
    private commonapi: CommonapiService,
    private router: Router
  ) { }



  getById_all_queries(event, newValue,query_id){
    this.selectedItem = newValue;
     for(const i in this.queries.data.results){
       this.queryid = query_id;
          if (this.queries.data.results[i].id == query_id){
            this.query_data =this.queries.data.results[i]
            if (this.query_data.platform==null){
              this.query_data.platform="all"
            }
            
          }
      }
   }
   getById_associated_queries(event, newValue,query_id){
    this.selectedItem = newValue;
     for(const i in this.associated_data.data.results){
       this.queryid = query_id;
          if (this.associated_data.data.results[i].id == query_id){
            this.query_data =this.associated_data.data.results[i]
            if (this.query_data.platform==null){
              this.query_data.platform="all"
            }
            
          }
      }
   }
   getfirst_data(any){
    
           this.query_data = any;
           this.selectedItem = this.query_data.id;
           this.queryid=this.query_data.id
           if (this.query_data.platform==null){
            this.query_data.platform="all"
          }
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

    type_query(data,id_of_packs){
     this.id_to_get_particular_queries=id_of_packs
      this.sorted_pack_data_name_id=[];
      
    let dataval_sort=[];
      for (const i in data){
        var l = data[i].name
        dataval_sort.push(l.toLowerCase())
       
      }
      if(id_of_packs == 'all_queries_id' && dataval_sort.length ==0){
        $('.no_data_all').show();
        $('.no_data').hide();
      }else{
        $('.no_data_all').hide();
        $('.no_data').show();
      }
      if( dataval_sort.length ==0){
        $('.present_data').hide();
      }else{
        $('.no_data').hide();
        $('.no_data_all').hide();
        $('.present_data').show();
        $('.queries_body').show(); 
        $('.queries_body2').hide();
      }
     let  dataval_sorted=[];
      dataval_sorted=dataval_sort.sort()
      dataval_sorted = dataval_sorted.filter((el, i, a) => i === a.indexOf(el))

      for(const j in dataval_sorted){
       for(const i in data){
        var l = data[i].name
          if(l.toLowerCase() == dataval_sorted[j]){
            let sorted_name_id=[]
            sorted_name_id.push(data[i].name)
            sorted_name_id.push(data[i].id)
            this.sorted_pack_data_name_id.push(sorted_name_id)
        }
  
        }
      }
      for(const i in data){
        let name = data[i].name
       if(name.toLowerCase() == dataval_sorted[0]){
        
        this.first_data=data[i]
      }
     }
     this.getfirst_data(this.first_data);
     console.log(this.sorted_pack_data_name_id,"this.sorted_pack_data_name_id")
    }

  ngOnInit() {
    this.sub = this._Activatedroute.paramMap.subscribe(params => {
      this.id = params.get('id');
    });
    $('.present_data').show();         
    $('.queries_body').hide();
    this.commonapi.queries_api().subscribe((res: any) => {
            this.queries = res;
            $('.queries_body2').hide()
            if( this.queries.data.count ==0){
              $('.no_data').show()
              $('.present_data').hide()         
            }else{
              $('.no_data').hide();
            }
   
            this.dataval_all = this.queries.data.results;
            console.log(this.dataval_all,"this.dataval_all")
            
    }
  );
  this.commonapi.associated_api().subscribe((res: any) => {
            this.associated_data=res;
            $('.present_data').show();
            $('.queries_body2').hide()
            this.dataval_packs = this.associated_data.data.results;
            console.log( this.associated_data," this.associated_data")

            if( this.associated_data.data.count ==0){
              $('.no_data').show()
              $('.present_data').hide()         
            }else{
              $('.no_data').hide();         
              $('.queries_body').show();
            }
           
            this.sorted_pack_data_name_id=[];
            let dataval_sort=[]
            for (const i in this.associated_data.data.results){
              var name = this.associated_data.data.results[i].name
              // var dataval_sorted =[]
              dataval_sort.push(name.toLowerCase())
             
            }
            let  dataval_sorted=[];
            dataval_sorted=dataval_sort.sort()
           
            dataval_sorted = dataval_sorted.filter((el, i, a) => i === a.indexOf(el))
            console.log(dataval_sorted,"dataval_sorted")

            for(const j in dataval_sorted){
             for(const i in this.associated_data.data.results){
              var name = this.associated_data.data.results[i].name
                if(name.toLowerCase() == dataval_sorted[j]){
                  let sorted_name_id=[]
                  sorted_name_id.push(this.associated_data.data.results[i].name)
                  sorted_name_id.push(this.associated_data.data.results[i].id)
                  this.sorted_pack_data_name_id.push(sorted_name_id)
              }
        
              }
            }

            for(const i in this.associated_data.data.results){
              let name = this.associated_data.data.results[i].name
             if(name.toLowerCase() == dataval_sorted[0]){
              
              this.first_data=this.associated_data.data.results[i]
            }
           }
          
           console.log(this.first_data)
           this.getfirst_data(this.first_data);
           this.id_to_get_particular_queries="associated_packs_id" 
                 
          });
        
  }
  deleteQueries(query_id, query_name){
    swal({
      title: 'Are you sure?',
      text: "Want to delete the Query "+ query_name,
      icon: 'warning',
      buttons: ["Cancel", true],
      closeOnClickOutside: false,
      dangerMode: true,
      }).then((willDelete) => {
      if (willDelete) {
        this.commonapi.deleteApiQueries(query_id).subscribe(res =>{
          console.log(res);
          swal({
        icon: 'success',
        title: 'Deleted!',
        text: 'Query has been deleted.',
        buttons: [false],
        timer: 2000
        })
        setTimeout(() => {
          this.ngOnInit();
              },1500);
      })
    }
  })
  }
}


