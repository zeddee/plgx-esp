import { Component, OnInit } from '@angular/core';
import { CommonapiService } from '../../dashboard/_services/commonapi.service';
import { ConditionalExpr } from '@angular/compiler';
import { Router, ActivatedRoute, ParamMap } from '@angular/router';

@Component({
  selector: 'app-rule',
  templateUrl: './rule.component.html',
  styleUrls: ['./rule.component.css','./rule.component.scss']
})
export class RuleComponent implements OnInit {
  public rule: any;
  public ruledata:any;
  public ruleid:any;
  public rule_condition:any;
  public rules:any = [];
  public conditions:any = {};
  searchText:any;
  show=false;
  selectedItem:any;
  public rule_alert :any = [];
  public rule_alert_val :any = [];
  public tactics_alert :any =[];
  public rule_tactics_val :any =[];
  sorted_rule_data_name_id=[];
  conditionLenght: any


  constructor(
    private commonapi: CommonapiService,
    private router: Router
  ) { }

getById(event, newValue,rule_id){
  this.selectedItem = newValue;
  console.log(newValue,rule_id)
  this.ruleid = rule_id;
  this.rule_alert_val = [];
  // this.rule_alert1 = [];
  this.rule_tactics_val = [];
  this.tactics_alert = [];
   for(const i in this.rule.data.results){
        if (this.rule.data.results[i].id == this.ruleid){
          this.ruledata =this.rule.data.results[i];
          this.rule_alert_val = this.getStringConcatinated(this.rule.data.results[i].alerters);
          this.rule_condition = this.ruledata.conditions.condition;
          this.rules = this.ruledata.conditions.rules;
          this.conditions = this.ruledata.conditions;
          this.rule_tactics_val = this.getStringConcatinated(this.rule.data.results[i].tactics);
  }
  }
  localStorage.setItem('rule_name',this.ruledata.name);
 }

 getfirst_data(firstdata){
  this.ruledata =firstdata;
  this.ruleid=this.ruledata.id;
  this.selectedItem = this.ruledata.name;
  this.conditions = this.ruledata.conditions;
  this.rule_condition = this.ruledata.conditions.condition;
  this.rules = this.ruledata.conditions.rules;
  this.rule_alert_val = [];
  this.rule_tactics_val = [];
  this.tactics_alert = []
   for(const i in this.rule.data.results){
      if (this.rule.data.results[i].id == this.ruleid){
        this.ruledata =this.rule.data.results[i];
        this.rule_alert_val = this.getStringConcatinated(this.rule.data.results[i].alerters);
        this.rule_tactics_val = this.getStringConcatinated(this.rule.data.results[i].tactics);
  }
  localStorage.setItem('rule_name',this.ruledata.name);
  }
  this.conditionLenght = this.conditions.rules.length
}
  ngOnInit() {
    this.commonapi.rules_api().subscribe((res: any) => {
        this.rule = res;
        console.log(res,"res")
        this.sorted_rule_data_name_id=[];
        let name_and_percentage=[]
        $('.rule_body2').hide();
        if( this.rule.data.count ==0){
          $('.no_data').append('No Rules Present')
          $('.rule_body').hide();
        }else{
          $('.rule_body').show();
          for (const i in this.rule.data.results){
            name_and_percentage=[]
            name_and_percentage.push(this.rule.data.results[i].name)
            var d =  Math.pow(10,10);
            var num=Number((Math.round((this.rule.data.results[i].alerts_count*100/this.rule.data.total_alerts) * d) / d).toFixed(1))
            name_and_percentage.push(num)
            name_and_percentage.push(this.rule.data.results[i].id)
            this.sorted_rule_data_name_id.push(name_and_percentage)
          }
          this.getfirst_data(this.rule.data.results[0]);
        }

  });

}
showShortDesciption = true

alterDescriptionText() {
   this.showShortDesciption = !this.showShortDesciption
}

getStringConcatinated(array_object){
  //Join Array elements together to make a string of comma separated list
  let string_object = "";
  try{
    if (array_object.length>0){
      string_object = array_object[0];
      for (let index = 1; index < array_object.length; index++) {
        string_object = string_object+', '+array_object[index];
      }
      return string_object
    }
  }
  catch(Error){
    return ""
  }
}


getRulesArray(ListObject, MainArray){
    for(const i in ListObject){
      if('condition' in ListObject[i]){
        MainArray.push({'condition':ListObject[i]['condition'], 'rules':this.getRulesArray(ListObject[i].rules, [])});
      }else
      {
        var dict = {};
        for (let key in ListObject[i]) {
          let value = ListObject[i][key];
          dict[key] = value;
        }
        MainArray.push(dict);
      }
    }
    return MainArray
}

isString(argument){
  if(typeof(argument)==typeof('')){
    return true
  }else{
    return false
  }
}
}
