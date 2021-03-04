import { Injectable } from '@angular/core';
import { Router, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { Observable } from 'rxjs';

import { AuthenticationService } from '../dashboard/_services/authentication.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  constructor(
        private router: Router,
        private authentication: AuthenticationService
    ) { }

/*
 CanActivate method returns a boolean indicating whether or not navigation to a route should be allowed. If the user isn’t authenticated.then in this case a route called authentication/login
*/

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot) {
    //const currentUser = this.authentication.currentUserValue;
    const currentUser = localStorage.getItem('currentUser');
          if (currentUser) {
              return true;
          } else {
              this.router.navigate(['./authentication/login'],{queryParams:{'redirectURL':state.url}});
              //location.reload();
              return false;
          }
  }

}
