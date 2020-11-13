import { Component, OnInit } from '@angular/core';
import { CommonapiService } from '../../../dashboard/_services/commonapi.service';
import { CommonVariableService } from '../../../dashboard/_services/commonvariable.service';
import { Router, ActivatedRoute } from '@angular/router';
import swal from 'sweetalert';
import { Location } from '@angular/common';
import { Title } from '@angular/platform-browser';

@Component({
  selector: 'app-tagged',
  templateUrl: './tagged.component.html',
  styleUrls: ['./tagged.component.scss']
})

export class TaggedComponent implements OnInit {
  id: any;
  query_data: any;
  queryid: any;
  sub: any;
  first_pack: any = [];
  host_data_val: any;
  pack_data_val: any;
  query_data_val: any;
  public tags_val: any;
  tagged: any;
  urlString = "";
  pack_data: any;
  packdata_tags: any;
  packdata_id: any;
  packdata_name: any;
  term: any;
  hosts_addtags_val: any;
  hosts_removetags_val: any;
  pack_addtags_val: any;
  pack_removetags_val: any;
  queries_addtags_val: any;
  queries_removetags_val: any;
  selectedItem:any;
  selectedItem_query:number;
  constructor(
    private commonapi: CommonapiService,
    private commonvariable: CommonVariableService,
    private _Activatedroute: ActivatedRoute,
    private router: Router,
    private _location: Location,
    private titleService: Title,

  ) { }

  getById(query_id) {
    this.selectedItem_query = query_id;
    for (const i in this.query_data_val) {
      if (this.query_data_val[i].id == query_id) {
        this.query_data = this.query_data_val[i]
      }
    }
  }

  getfirst_data() {
    if (this.tagged.data.queries.length > 0) {
      this.query_data = this.tagged.data.queries[0];
      this.queryid = this.query_data.id
      this.selectedItem_query = this.query_data.id;
    }
  }

  getById_pack(pack_name) {
    this.selectedItem = pack_name
    for (const i in this.pack_data_val) {
      if (this.pack_data_val[i].name == pack_name) {
        this.pack_data = this.pack_data_val[i];
        this.packdata_tags = this.pack_data.tags;
        this.packdata_id = this.pack_data.id;
        this.packdata_name = this.pack_data.name;
      }
    }
  }

  getfirstpack_data() {
    this.pack_data = this.tagged.data.packs[0];
    this.packdata_tags = this.pack_data.tags;
    this.packdata_id = this.pack_data.id;
    this.packdata_name = this.pack_data.name;
    this.selectedItem = this.pack_data.name
  }
  ngOnInit() {
    this.titleService.setTitle(this.commonvariable.APP_NAME+"-"+"Tag");

    this._Activatedroute.paramMap.subscribe(params => {
      this.id = params.get('id');
    });

    this.urlString =decodeURIComponent(this.router.url);
    let toArray = this.urlString.split('/');
    this.tags_val = toArray[3];
    var qrytags_val = this.tags_val;
    this.commonapi.tagged_api(qrytags_val).subscribe((res: any) => {
      this.tagged = res;
      this.first_pack = res;
      this.host_data_val = this.tagged.data.hosts;
      this.pack_data_val = this.tagged.data.packs;
      this.query_data_val = this.tagged.data.queries;
      
        if (this.tagged.data.queries.length > 0) {
          this.getfirst_data() 
        }
    
      if (this.tagged.data.packs.length > 0) {
        this.getfirstpack_data()
      }
     
    });
    
  }

  hosts_addTag(tags, node_id) {
    this.commonapi.hosts_addtag_api(node_id, tags.toString()).subscribe(res => {
      this.hosts_addtags_val = res;
    });
  }
  hosts_removeTag(event, node_id) {
    this.commonapi.hosts_removetags_api(node_id, event).subscribe(res => {
      this.hosts_removetags_val = res;
    });
  }

  pack_addTag(test, id) {
    this.commonapi.packs_addtag_api(id, test.toString()).subscribe(res => {
      this.pack_addtags_val = res;
    });
  }
  pack_removeTag(event, pack_id) {
    this.commonapi.packs_removetags_api(pack_id, event).subscribe(res => {
      this.pack_removetags_val = res;
    });
  }

  queries_addTag(tags, query_id) {
    this.commonapi.queries_addtag_api(query_id, tags.toString()).subscribe(res => {
      this.queries_addtags_val = res;
    });
  }
  queries_removeTag(event, query_id) {
    this.commonapi.queries_removetags_api(query_id, event).subscribe(res => {
      this.queries_removetags_val = res;
    });
  }
  goBack() {
    this._location.back();
  }

  runAdHoc(queryId) {
    this.router.navigate(["/live-queries/", queryId]);
  }

}
