import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { LiveQueriesComponent } from './live-queries.component';

describe('LiveQueriesComponent', () => {
  let component: LiveQueriesComponent;
  let fixture: ComponentFixture<LiveQueriesComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ LiveQueriesComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(LiveQueriesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
