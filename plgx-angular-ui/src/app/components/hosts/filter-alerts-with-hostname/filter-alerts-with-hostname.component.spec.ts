import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { FilterAlertsWithHostnameComponent } from './filter-alerts-with-hostname.component';

describe('FilterAlertsWithHostnameComponent', () => {
  let component: FilterAlertsWithHostnameComponent;
  let fixture: ComponentFixture<FilterAlertsWithHostnameComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ FilterAlertsWithHostnameComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(FilterAlertsWithHostnameComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
