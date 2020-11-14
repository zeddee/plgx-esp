import { Injectable } from '@angular/core';
import * as Rx from "rxjs";

@Injectable({
  providedIn: 'root'
})
export class WebsocketService {

  constructor() { }

  private subject: Rx.Subject<MessageEvent>;

  public connect(url): Rx.Subject<MessageEvent> {
    console.log(url);
    if (!this.subject) {
      this.subject = this.create(url);
      console.log("Successfully connected: " + url);
    }
    return this.subject;
  }

  private create(url): Rx.Subject<MessageEvent> {
    console.log(url);
    let ws = new WebSocket(url);
    let observable = Rx.Observable.create((obs: Rx.Observer<MessageEvent>) => {
      console.log(ws);
      ws.onmessage = obs.next.bind(obs);
      ws.onerror = obs.error.bind(obs);
      ws.onclose = obs.complete.bind(obs);
      return ws.close.bind(ws);
    });
    let observer = {
      next: (data: string) => {
        console.log(WebSocket.OPEN);
        if (ws.readyState === WebSocket.OPEN) {
          console.log(data);
          ws.send(JSON.stringify(data));
        }
      }
    };


    return Rx.Subject.create(observer, observable);
}

}
