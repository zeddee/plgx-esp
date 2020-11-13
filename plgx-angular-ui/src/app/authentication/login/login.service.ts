import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})

export class loginService {
  constructor(private _http: HttpClient) {
  }
  login(object) {
    var username = object.value.username;
    var password = object.value.password;
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json'
      })
    };
    return this._http.post<any>(environment.api_url + '/login', { username, password },httpOptions)
  }
}