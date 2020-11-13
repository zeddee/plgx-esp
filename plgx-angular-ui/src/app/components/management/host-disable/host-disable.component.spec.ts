import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { HostDisableComponent } from './host-disable.component';

describe('HostDisableComponent', () => {
  let component: HostDisableComponent;
  let fixture: ComponentFixture<HostDisableComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ HostDisableComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(HostDisableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
