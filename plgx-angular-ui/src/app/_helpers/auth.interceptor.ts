import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent } from "@angular/common/http";
import { Observable } from "rxjs";
import { Injectable, Compiler } from "@angular/core";
import { Router } from "@angular/router";
import { tap } from 'rxjs/operators';


@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(
    private _router: Router,
    private _compiler: Compiler
  ) { }

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    this._compiler.clearCache();
    if (localStorage.getItem('JWTkey')) {
      req = req.clone({
        setHeaders: {
          'x-access-token': localStorage.getItem('JWTkey'),
        }
      });
    }
    return next.handle(req)
      .pipe(tap(
        succ => {
        },
        err => {
          if (err.status === 401) {
            this.clearData();
          }
          else if (err.status === 404) {
            const validationError = err.error;
          }
          else if (err.status === 400) {
            const validationError = err.error;
          }
        }
      ));
  }
  clearData() {
    localStorage.removeItem('JWTkey');
    this._router.navigate(['/']);
  }
}
