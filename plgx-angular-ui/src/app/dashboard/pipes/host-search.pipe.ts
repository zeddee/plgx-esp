import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'hostsearch'
})

export class HostSearchPipe implements PipeTransform {

transform(records: Array<any>, searchText?: string): any {
    if (!searchText || searchText == "") return records;
    return records.filter(rec => {
    return Object.keys(rec).some(x => String(rec[x]).toLowerCase().includes(searchText.toLowerCase()) ||
    rec.display_name.toLowerCase().includes(searchText)
    || rec.last_ip.toLowerCase().includes(searchText)
    || rec.os_info.name.toLowerCase().includes(searchText));
    })
    }
}