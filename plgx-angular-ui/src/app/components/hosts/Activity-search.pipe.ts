import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'activitysearch'
})

export class ActivitySearchPipe implements PipeTransform {  
  transform(records: Array<any>, searchText?: string): any { 

    if (!searchText || searchText == "") return records;
    
     var data =  records.filter(
      (val)=> String(val.name.toLowerCase()).includes(searchText.toLowerCase()))

      if(data.length === 0) {
        return [-1];
      }
      else
      {
      return data;
      }
  }

}