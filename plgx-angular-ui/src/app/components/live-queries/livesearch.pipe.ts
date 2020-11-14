import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'livesearch'
})

export class LiveSearchPipe implements PipeTransform {  
  transform(records: {}, searchText?: string): any { 
    let data1= Object.keys(records)
    if (!searchText || searchText == "") return records;

     var data =  data1.filter(
      (val)=> String(val.toLowerCase()).includes(searchText.toLowerCase()))
      let dict={}
      for (let [key, value] of Object.entries(records)) {
        if(data.includes(key)){
          dict[key]=value
        }
    }
      if(Object.keys(dict).length === 0) {
        return [-1];
      }
      else{      
      return dict;
      }
      
  }

}