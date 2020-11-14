import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { HuntComponent } from './hunt.component';

describe('HuntComponent', () => {
  let component: HuntComponent;
  let fixture: ComponentFixture<HuntComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ HuntComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(HuntComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
